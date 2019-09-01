#!/usr/bin/env python

import argparse
import logging
import os
import subprocess
import sys
from os.path import expanduser

# TODO(ruan.lj@foxmail.com): add test case.

HOME = expanduser("~")
LOG_DIR = os.path.join(HOME, '.log')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(LOG_DIR, 'my_rm.log'),
                    filemode='a')


def get_mount_points():
    """get system network disk mount points"""

    points = []
    t = subprocess.check_output(['mount'])
    t = t.decode()

    for line in t.splitlines():
        t = line.find('smbfs')
        if t < 0: continue
        b = line.find(' on ')
        points.append(line[b+4: t-2])
        # //share@win10.shared/storage on /Volumes/storage (smbfs, nodev, nosuid, mounted by ruan)
    return points


def match_trash_bin(abs_path, trash_bins):
    """
    args:
        abs_path: string, file abs path, eg /Volumes/storage/xxx
        trash_bins: dict, {mount_point: trash_bin}, eg {'/Volumes/storage': '/Volumes/storage/.Trashes'}
    """
    assert abs_path[0] == '/'
    tmp = []
    for k, v in trash_bins.items():
        if abs_path.find(k) != -1:
            tmp.append(k)

    if not tmp:
        return None
    mp = max(tmp, key=lambda i: len(i))
    return trash_bins[mp]


def check_trash_bins(trash_bins):
    """
    args:
        trash_bins: list, path of trash bin, eg ['/Volumes/storage/.Trashes']
    """
    for p in trash_bins:
        if not os.path.exists(p):
            os.mkdir(p)


def main():
    logging.info('run: %s', sys.argv)
    parser = argparse.ArgumentParser(description="remove file support mac trash bin and smb trash")
    parser.add_argument('file', nargs='+', help='files need to remove')
    parser.add_argument('-f')   # dummy options
    parser.add_argument('-r')   # dummy options
    args, unknown = parser.parse_known_args()

    trash_bins = {i: os.path.join(i, '.Trashes') for i in get_mount_points()}
    check_trash_bins(trash_bins.values())

    files = []
    for i in args.file:
        p = os.path.abspath(i)
        if not os.path.exists(p):
            print("cannot stat '{}': No such file or directory".format(p))
            continue

        # TODO(ruan.lj@foxmail.com): can imporve trash bin match time complexity, use tried tree.
        m = match_trash_bin(p, trash_bins)
        if m:
            subprocess.check_call(['mv', p, m])
        else:
            subprocess.check_call(['trash', p])
        files.append(p)

    logging.info('remove files: %s', files)


if __name__ == '__main__':
    main()
