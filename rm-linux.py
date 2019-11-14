#!/usr/bin/env python

import argparse
import logging
import os
import subprocess
import sys
from os.path import expanduser
from datetime import datetime

def check_dirs(paths):
    for p in paths:
        if not os.path.exists(p):
            os.mkdir(p)

HOME = expanduser("~")
TRASH_BIN = expanduser("~/.trashes")
LOG_DIR = os.path.join(HOME, '.log')
TODAY_BIN = os.path.join(TRASH_BIN, datetime.now().strftime('%Y%m%d'))
DAYS = 30


check_dirs([TRASH_BIN, LOG_DIR, TODAY_BIN])

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=os.path.join(LOG_DIR, 'my_rm.log'),
    filemode='a'
)


def clean_outdated():
    now = datetime.now()
    to_del = []
    for i in os.listdir(TRASH_BIN):
        try:
            d = datetime.strptime(i, '%Y%m%d')
            if (now- d).days > DAYS:
                to_del.append(os.path.join(TRASH_BIN, i))
        except Exception as e:
            logging.info(e)
            continue

    if to_del:
        subprocess.check_call(['rm', '-r', '-f'] + to_del)
        logging.info('clean trashes: %s', to_del)


def main():
    logging.info('run: %s', sys.argv)
    parser = argparse.ArgumentParser(description="remove file support mac trash bin and smb trash")
    parser.add_argument('file', nargs='+', help='files need to remove')
    parser.add_argument('-f')   # dummy options
    parser.add_argument('-r')   # dummy options
    args, unknown = parser.parse_known_args()

    files = []
    for i in args.file:
        p = os.path.abspath(i)
        if not os.path.exists(p):
            print("cannot stat '{}': No such file or directory".format(p))
            continue

        subprocess.check_call(['mv', p, TODAY_BIN])
        files.append(p)

    logging.info('remove files to `%s`: %s', TODAY_BIN, files)

    clean_outdated()

if __name__ == '__main__':
    main()
