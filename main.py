import copy
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from json import JSONDecodeError


def main():
    args = sys.argv[1:]
    mongo_log_path = ''
    output_dir = ''
    cached_stamp = ''
    cached_date = ''
    is_old_version = False
    for arg in args:
        if arg.startswith('--LogPath='):
            mongo_log_path = arg.split('=')[1]
        if arg.startswith('--OutputPath='):
            output_dir = arg.split('=')[1]

    while True:
        if not os.path.isfile(output_dir):
            logging.error('Output file does not exist = ' + output_dir)
            sys.exit(2)
        try:
            stamp = os.stat(mongo_log_path).st_mtime
            if stamp != cached_stamp:
                cached_stamp = stamp
                log_file = open(mongo_log_path, 'r', encoding='utf8', errors='ignore')
                lines = log_file.readlines()

                file = open(output_dir, 'a+', encoding='utf8')
                if cached_date == '':
                    file_with_last_date = open(output_dir, 'r', encoding='utf8')
                    read_lines = file_with_last_date.readlines()
                    if len(read_lines) > 0:
                        group = re.search('(.*) CEF:0', read_lines[-1])
                        if group is not None:
                            cached_date = datetime.strptime(group.group(1), "%Y-%m-%d %H:%M:%S.%f")
                    file_with_last_date.flush()
                    file_with_last_date.close()
                for index, line in enumerate(lines, 1):
                    group = re.search('date":"(.*)"},"s"', line)
                    if is_old_version:
                        old_log_version(line, cached_date, output_dir)
                        continue

                    if group is None:
                        is_old_version = old_log_version(line, cached_date, output_dir)
                        # logging.warning('Could not find date in line by number: ' + str(index))
                        continue

                    local_date = datetime.strptime(group.group(1)[:-6], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    local_date = datetime.strptime(local_date, "%Y-%m-%d %H:%M:%S.%f")

                    if cached_date != '' and cached_date >= local_date:
                        continue
                    cached_date = copy.copy(local_date)
                    json_line: dict = json.loads(line)
                    result_line = ''

                    date = datetime.strptime(json_line['t']['$date'][:-6], "%Y-%m-%dT%H:%M:%S.%f").strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    result_line += str(date)
                    result_line += ' CEF:0|Газпром нефть|Система Корпоративного Контроля|1.0.0|'
                    result_line += str(json_line['id']) + '|'
                    result_line += json_line['c'] + '|'
                    result_line += '5' + '|'

                    result_line += 'cs1Label=name of thread'
                    result_line += ' cs1=' + json_line['ctx']
                    result_line += ' cs2Label=log output message'
                    if json_line['msg'] == 'WiredTiger message':
                        continue
                    result_line += ' cs2=' + json_line['msg']

                    if json_line.get('attr', {}).get('ns', False):
                        result_line += ' suser=' + json_line['attr']['ns']

                    if json_line.get('attr', {}).get('command', False):
                        if isinstance(json_line['attr']['command'], str):
                            result_line += ' cs3Label=command'
                            result_line += ' cs3=' + json_line['attr']['command']
                        elif isinstance(json_line['attr']['command'], dict):
                            label = str(list(json_line['attr']['command'].items())[0][0])
                            if label == 'hello' or label == 'ismaster':
                                continue
                            result_line += ' cs3Label=' + label
                            result_line += ' cs3=' + str(list(json_line['attr']['command'].items())[0][1])

                    if json_line.get('attr', {}).get('query', False):
                        if isinstance(json_line['attr'], dict) and isinstance(json_line['attr']['query'], str):
                            result_line += ' cs4Label=query'
                            result_line += ' cs4=' + str(json_line['attr']['query'])

                    if json_line.get('attr', {}).get('remote', False):
                        result_line += ' cs5Label=remote'
                        result_line += ' cs5=' + str(json_line['attr']['remote'])
                    result_line += '\n'
                    file.write(result_line)
                    file.flush()
                file.close()
                log_file.close()
            # print(cached_date)
        except IOError as e:
            logging.error('Could not open/read log file =' + mongo_log_path)
        except JSONDecodeError as e:
            logging.error(e)
        except Exception as e:
            logging.exception(e)
            sys.exit(2)

        time.sleep(1)


def old_log_version(line: str, cached_date, output_dir) -> bool:
    line_split = line.split()
    local_date = datetime.strptime(line_split[0][:-6], "%Y-%m-%dT%H:%M:%S.%f").strftime('%Y-%m-%d %H:%M:%S.%f')
    local_date = datetime.strptime(local_date, "%Y-%m-%d %H:%M:%S.%f")

    if cached_date != '' and cached_date >= local_date:
        return True
    cached_date = copy.copy(local_date)

    result_line = ''
    result_line += str(local_date)
    result_line += ' CEF:0|Газпром нефть|Система Корпоративного Контроля|1.0.0|0|'
    result_line += line_split[2] + '|'
    result_line += 'cs1Label=' + line_split[3][1:-1]
    result_line += ' cs1=' + ' '.join(line_split[4:])
    result_line += '\n'

    file = open(output_dir, 'a+', encoding='utf8')
    file.write(result_line)
    file.flush()
    file.close()
    return True


if __name__ == "__main__":
    main()
