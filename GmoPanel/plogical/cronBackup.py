#!/usr/bin/env python3

from plogical.backupSetting import BackupAllProvision
from backupManager.models import CronJob
from django.core.exceptions import ObjectDoesNotExist
import argparse
import django
import sys
import os
sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()


def get_options(argv):
    parser = argparse.ArgumentParser()
    # parser.add_argument('mode', type=str, choices=['local', 'remote', 'drive'])
    # parser.add_argument('options', nargs=argparse.REMAINDER)
    parser.add_argument('-i', required=True)
    return parser.parse_args(argv)


def main():
    args = get_options(sys.argv[1:])
    try:
        tasks = CronJob.objects.get(id="%s" % args.i)
    except ObjectDoesNotExist as error:
        print(error)
    job = BackupAllProvision()
    if tasks.backup_type == 0:
        print(tasks.backup_schedu)
    # if args.mode == 'local':
    #    job.local_backup('/home/kusanagi/backup/%s/' % args.options[0])
    # if args.mode == 'remote':
    #    job.remote_backup(*args.options)
    # if args.mode == 'drive':
    #    job.drive_backup(*args.options)
    

if __name__ == '__main__':
    main()

# print('the meo nao')
