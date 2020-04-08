#!/usr/bin/env python3

import argparse
import django
import sys
import os
sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
from django.core.exceptions import ObjectDoesNotExist
from plogical.backupSetting import BackupAllProvision
from backupManager.models import CronJob


def get_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    return parser.parse_args(argv)


def main():
    args = get_options(sys.argv[1:])
    try:
        tasks = CronJob.objects.get(id="%s" % args.i)
    except ObjectDoesNotExist as error:
        print(error)
    job = BackupAllProvision()
    bktype = tasks.backup_type
    if bktype == 0:
        print(tasks.backup_schedu)
        for k in list(tasks.backup_schedu.split(",")):
            job.local_backup('/home/kusanagi/backup/%s/' % k)
    if bktype == 1:
        job.remote_backup(tasks.user, tasks.host, tasks.port, tasks.password, tasks.path)
    if bktype == 2:
        job.drive_backup(tasks.path)
    

if __name__ == '__main__':
    main()
