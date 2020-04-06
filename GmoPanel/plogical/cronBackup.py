#!/usr/bin/env python3

import django
import sys
import os
sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
import argparse
from plogical.backupSetting import BackupAllProvision


def get_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, choices=['local', 'remote', 'drive'])
    parser.add_argument('options', nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main():
    args = get_options(sys.argv[1:])
    job = BackupAllProvision()
    if args.mode == 'local':
        job.local_backup('/home/kusanagi/backup/%s/' % args.options[0])
    if args.mode == 'remote':
        job.remote_backup(*args.options)
    if args.mode == 'drive':
        job.drive_backup(*args.options)
    

if __name__ == '__main__':
    main()

# print('the meo nao')
