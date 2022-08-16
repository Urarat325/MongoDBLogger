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
    last_index = 0
    for arg in args:
        if arg.startswith('--LogPath='):
            mongo_log_path = arg.split('=')[1]
            mongo_log_path = 'C:\\Project\\Py\\MongoDBLogger\\test.log'
        if arg.startswith('--OutputPath='):
            output_dir = arg.split('=')[1]

    while True:
        if not os.path.isdir(output_dir):
            logging.error('Output directory does not exist = ' + output_dir)
            sys.exit(2)
        try:
            stamp = os.stat(mongo_log_path).st_mtime
            if stamp != cached_stamp:
                cached_stamp = stamp
                log_file = open(mongo_log_path, 'r')
                lines = log_file.readlines()
                flag = True
                if len(lines) < last_index:
                    flag = False

                file = open('C:\\Project\\Py\\MongoDBLogger\\outTest.log', 'a+')
                for index, line in enumerate(lines, 1):
                    group = re.search('\$date":"(.*)"},', line)
                    if group is None:
                        logging.error('Could not find date in line =' + line)
                    print(group.group(1))
                    if index <= last_index and flag:
                        continue
                    json_line: dict = json.loads(line)
                    result_line = ''
                    for key, value in json_line.items():
                        if key == "t":
                            # "%Y-%m-%dT%H:%M:%S.%f%z"
                            date = datetime.strptime(value['$date'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                                '%Y-%m-%d %H:%M:%S %Z')
                            result_line += str(date)
                            result_line += ' CEF:0|'

                    result_line += '\n'
                    file.write(result_line)
                    last_index = index
                file.close()
        except IOError as e:
            logging.error('Could not open/read log file =' + mongo_log_path)
        except JSONDecodeError as e:
            logging.error(e)
        except Exception as e:
            logging.exception(e)
            sys.exit(2)

        time.sleep(1)


if __name__ == "__main__":
    main()
