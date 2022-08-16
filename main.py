import json
import logging
import os
import sys
import time


def main():
    args = sys.argv[1:]
    mongo_log_path = ''
    output_dir = ''
    cached_stamp = ''
    last_index = 0
    for arg in args:
        if arg.startswith('--LogPath='):
            mongo_log_path = arg.split('=')[1]
            mongo_log_path = 'C:\\Project\\Py\\MongoDBLogger\\test.txt'
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

                file = open('C:\\Project\\Py\\MongoDBLogger\\outTest.txt', 'a+')
                for index, line in enumerate(lines, 1):
                    if index <= last_index and flag:
                        continue
                    json_line: dict = json.loads(line)
                    result_line = ''
                    for key, value in json_line.items():
                        result_line +=
                    file.write(line)
                    last_index = index
                file.close()
                print(123)

        except Exception as e:
            logging.error('Log file does not exist = ' + mongo_log_path)
            sys.exit(2)

        # time.sleep(1)


if __name__ == "__main__":
    main()
