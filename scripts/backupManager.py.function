#!/usr/bin/env python3
import argparse
import os
import sys,shutil
from shutil import make_archive
import pathlib
from phpManager import execute,execute_outputfile
from datetime import date,datetime
import re
import pymysql
import tarfile


def append_log(log,message):
    f = open(log, "a+")
    today = datetime.now()
    f.write("%s %s \n" % (today.strftime("%Y-%m-%d %H:%M:%S"), message))
    f.close()

def get_root_pass():
    with open("/root/.my.cnf") as fp: lines = fp.read().splitlines()
    for line in lines:
        grep = re.findall(r'password', line)
        if grep:
            pwrd = line.split('"')[1]
    return pwrd

def get_db_name(argv):
    try:
        pwrd = get_root_pass()
        db = pymysql.connect("localhost","root",pwrd,"secure_vps")
        cursor = db.cursor()
        cursor.execute("select id,db_name from provision where provision_name='%s'" % argv)
        data = cursor.fetchone()
        db.close()
        return data
    except pymysql.err.OperationalError as err:
        print (' An error has occurred \n', err)
    except pymysql.err.InternalError as err:
        print (' An error has occurred \n', err)

def backup_db(argv):

    data = get_db_name(argv)
    db_name = data[1]
    try:
        sqldir = '/home/kusanagi/'+argv+'/sql_backup/'
        p = pathlib.Path(sqldir)
        if not p.exists():
            p.mkdir(mode=0o755, parents=True, exist_ok=True)
            shutil.chown(sqldir,'kusanagi','kusanagi')
    except BaseException as error:
        print(error)
    pwrd = get_root_pass()

    log = '/home/kusanagi/'+argv+'/log/backup.log'
    mess = 'Backed up database '+db_name
    append_log(log,mess)

    cmd = 'mysqldump --single-transaction -p'+pwrd+' --databases '+db_name+' | gzip > '+sqldir+db_name+'.sql.gz'
    execute_outputfile(cmd,log)

def update_backup_record(argv,backup_type,result):

    pwrd = get_root_pass()
    data = get_db_name(argv)
    provi_id = data[0]
    log = '/home/kusanagi/'+argv+'/log/backup.log'

    db = pymysql.connect("localhost","root",pwrd,"secure_vps")
    cursor = db.cursor()
    cursor.execute("select id from logs where provision_id=%d and status=0 and backup_type=%d" % (provi_id,backup_type))
    res = cursor.fetchone()
    record_id = res[0]

    if result:
        cursor.execute("update logs set status=1,message='Done' where provision_id=%d and id=%d" % (provi_id,record_id))
    else:
        cursor.execute("update logs set status=-1,message='Failed. See %s' where provision_id=%d and id=%d" % (log,provi_id,record_id))

    db.commit()
    db.close()

def compress_provision_dir(argv,chdir=''):
    date = datetime.now()
    today = date.strftime("%Y-%m-%d")
    if chdir:
        tarname = chdir+argv+'.'+today
    else:
        tarname = '/home/kusanagi/backup/'+argv+'.'+today
    source_dir = '/home/kusanagi/'+argv
    shutil.make_archive(tarname,"gztar",source_dir)
    return tarname

def local_backup(argv):
   
    append_log('/home/kusanagi/'+argv+'/log/backup.log', '--- Local backup')
    backup_db(argv)
    tarname = compress_provision_dir(argv)

    tar_file=pathlib.Path(tarname+'.tar.gz')
    if tar_file.exists():
        update_backup_record(argv,0,1)
    else:
        update_backup_record(argv,0,0)

def check_ssh_conn(argv,remote_user,remote_host,remote_port,remote_pass):
    cmd = 'sshpass -p "'+remote_pass+'" ssh -o StrictHostKeyChecking=no -p '+remote_port+' -q '+remote_user+'@'+remote_host+' exit;echo $?'
    res = execute(cmd)
    log = '/home/kusanagi/'+argv+'/log/backup.log'
    if int(res) == 0:
        #print('Connect OK \n')
        pass
    else:
        append_log(log, 'Remote connection failed. Can not issue remote backup')
        update_backup_record(argv,1,0)
        sys.exit(1)

def remote_backup(argv, remote_user, remote_host, remote_port, remote_pass, remote_dest):

    log = '/home/kusanagi/'+argv+'/log/backup.log'
    append_log(log, '--- Remote backup')
    check_ssh_conn(argv, remote_user, remote_host, remote_port, remote_pass)
    backup_db(argv)
    tarname = compress_provision_dir(argv,'/home/kusanagi/')
    
    conf_ssh = '/etc/ssh/ssh_config'
    with open(conf_ssh) as fp: lines = fp.read().splitlines()
    for line in lines:
        grep = re.findall(remote_host, line)
        if grep:
            break
    if not grep:
        #configure stricthostkey ssh
        f = open(conf_ssh,"a+")
        f.write('Host %s\n\tStrictHostKeyChecking no\n' % remote_host)
        f.close()
    
    cmd = 'sshpass -p "'+remote_pass+'" rsync --remove-source-files -azhe \'ssh -p'+remote_port+'\' '+tarname+'.tar.gz '+remote_user+'@'+remote_host+':'+remote_dest+' 2>> '+log+' ; echo $?'
    res = execute(cmd)
    if int(res) == 0:
        update_backup_record(argv,1,1)
    else:
        update_backup_record(argv,1,0)


def drive_backup(argv,drive_dir):
    
    log = '/home/kusanagi/'+argv+'/log/backup.log'
    append_log(log,'--- Backup to Google Drive')
    backup_db(argv)
    tarname = compress_provision_dir(argv,'/home/kusanagi/')
    cmd = 'rclone copy '+tarname+'.tar.gz GGD1:'+drive_dir+ ' 2>> '+log+' ; echo $?'
    res = execute(cmd)
    if int(res) == 0:
        update_backup_record(argv,2,1)
    else:
        update_backup_record(argv,2,0)
    os.remove(tarname+'.tar.gz')
    
def get_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, choices=['local', 'remote', 'drive'])
    parser.add_argument('options', nargs=argparse.REMAINDER)
    return parser.parse_args(argv)

def main():
   
    args=get_options(sys.argv[1:])
    #pwrd = get_root_pass()
    options = ' '.join(map(str, args.options))
    if args.mode == 'local':
        local_backup(*args.options)
    elif args.mode == 'remote':
        remote_backup(*args.options)
    else:
        drive_backup(*args.options)

if __name__ == '__main__':
    main()

