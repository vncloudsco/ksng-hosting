#!/usr/bin/env python3

import argparse
import os
import sys, shutil
import pathlib
from phpManager import execute, execute_outputfile
from datetime import datetime
import re
import pymysql
# import mysql.connector as MySQLdb


class BackupManager:

    def __init__(self, argv=None):
        self.provi = argv
        self.log = '/home/kusanagi/'+argv+'/log/backup.log'
        self.pwrd = self.get_root_pass()

    @staticmethod
    def append_log(log, message):
        f = open(log, "a+")
        today = datetime.now()
        f.write("%s %s \n" % (today.strftime("%Y-%m-%d %H:%M:%S"), message))
        f.close()

    @staticmethod
    def get_root_pass():
        pwd = None
        with open("/root/.my.cnf") as fp: lines = fp.read().splitlines()
        for line in lines:
            grep = re.findall(r'password', line)
            if grep:
                pwd = line.split('"')[1]
        return pwd

    def get_db_name(self):
        try:
            db = pymysql.connect("localhost", "root", self.pwrd, "secure_vps")
            cursor = db.cursor()
            cursor.execute("select id,db_name from provision where provision_name='%s' and deactive_flg=0 " % self.provi)
            data = cursor.fetchone()
            db.close()
            return data
        except pymysql.err.OperationalError as err:
            print(' An error has occurred \n', err)
        except pymysql.err.InternalError as err:
            print(' An error has occurred \n', err)

    def backup_db(self):

        data = self.get_db_name()
        db_name = data[1]
        try:
            sqldir = '/home/kusanagi/'+self.provi+'/sql_backup/'
            p = pathlib.Path(sqldir)
            if not p.exists():
                p.mkdir(mode=0o755, parents=True, exist_ok=True)
                shutil.chown(sqldir, 'kusanagi', 'kusanagi')
        except BaseException as error:
            print(error)
        
        mess = 'Back up database '+db_name
        self.append_log(self.log, mess)

        cmd = 'mysqldump --single-transaction -p'+self.pwrd+' --databases '+db_name+' | gzip > ' + sqldir + db_name + '.sql.gz'
        execute_outputfile(cmd, self.log)

    def update_backup_record(self, backup_type, result):

        data = self.get_db_name()
        provi_id = data[0]

        db = pymysql.connect("localhost", "root", self.pwrd, "secure_vps")
        cursor = db.cursor()
        cursor.execute("select id from logs where provision_id=%d and status=0 and backup_type=%d" % (provi_id, backup_type))
        res = cursor.fetchone()
        record_id = res[0]

        if result:
            cursor.execute("update logs set status=1,message='Done' where provision_id=%d and id=%d" % (provi_id, record_id))
        else:
            cursor.execute("update logs set status=-1,message='Failed. See %s' where provision_id=%d and id=%d" % (self.log, provi_id, record_id))

        db.commit()
        db.close()

    def compress_provision_dir(self, chdir=None):
        date = datetime.now()
        today = date.strftime("%Y-%m-%d")
        if chdir:
            tarname = chdir+self.provi+'.'+today
        else:
            tarname = '/home/kusanagi/backup/'+self.provi+'.'+today
        source_dir = '/home/kusanagi/'+self.provi
        shutil.make_archive(tarname, "gztar", source_dir)
        return tarname

    def local_backup(self, chdir=None):

        self.append_log(self.log, '--- Local backup')
        self.backup_db()
        tarname = self.compress_provision_dir(chdir)

        self.initial_backup_record(0)

        tar_file=pathlib.Path(tarname+'.tar.gz')
        if tar_file.exists():
            self.update_backup_record(0, 1)
        else:
            self.update_backup_record(0, 0)

    def check_ssh_conn(self, remote_user, remote_host, remote_port, remote_pass):
        cmd = 'sshpass -p "'+remote_pass+'" ssh -o StrictHostKeyChecking=no -p '+remote_port+' -q '+remote_user+'@'+remote_host+' exit;echo $?'
        res = execute(cmd)
        if int(res) == 0:
            #print('Connect OK \n')
            pass
        else:
            self.append_log(self.log, 'Remote connection failed. Can not issue remote backup')
            self.update_backup_record(1, 0)
            sys.exit(1)

    def remote_backup(self, remote_user, remote_host, remote_port, remote_pass, remote_dest):
        
        self.initial_backup_record(1)
        self.append_log(self.log, '--- Remote backup')
        self.check_ssh_conn(remote_user, remote_host, remote_port, remote_pass)
        self.backup_db()
        tarname = self.compress_provision_dir('/home/kusanagi/')

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

        cmd = 'sshpass -p "'+remote_pass+'" rsync --remove-source-files -azhe \'ssh -p'+remote_port+'\' '+tarname+'.tar.gz '+remote_user+'@'+remote_host+':'+remote_dest+' 2>> '+self.log+' ; echo $?'
        res = execute(cmd)

        if int(res) == 0:
            self.update_backup_record(1, 1)
        else:
            self.update_backup_record(1, 0)

    def drive_backup(self, drive_dir):

        self.append_log(self.log, '--- Backup to Google Drive')
        self.backup_db()
        tarname = self.compress_provision_dir('/home/kusanagi/')
        cmd = 'rclone copy '+tarname+'.tar.gz GGD1:'+drive_dir+ ' 2>> '+self.log+' ; echo $?'
        res = execute(cmd)

        self.initial_backup_record(2)

        if int(res) == 0:
            self.update_backup_record(2, 1)
        else:
            self.update_backup_record(2, 0)
        
        os.remove(tarname+'.tar.gz')

    def initial_backup_record(self, backup_type):

        data = self.get_db_name()
        provi_id = data[0]

        db = pymysql.connect("localhost", "root", self.pwrd, "secure_vps")
        cursor = db.cursor()
        cursor.execute("insert into logs(provision_id,status,backup_type) values(%d,0,%d)" % (provi_id, backup_type))

        db.commit()
        db.close()

    def delete_old_local_backup(self, chdir=None, number=0):
        count = 0
        pattern = chdir+self.provi+'\.\d+'
        regex = re.compile(pattern)
        filelist = []
        for root, dirs, files in os.walk(chdir):
            for name in files:
                if regex.match(os.path.join(root, name)):
                    count = count + 1
                    filelist.append(os.path.join(root, name))
        left = count - number
        filelist.sort(key=os.path.getmtime)
        for i in range(left):
            os.remove(filelist[i])


class BackupAllProvision:

    def __init__(self):
        self.password = BackupManager.get_root_pass()
        self.pro_list = self.list_all_provision()

    def list_all_provision(self):
        db = pymysql.connect("localhost", "root", self.password, "secure_vps")
        cursor = db.cursor()
        cursor.execute("select provision_name from provision")
        data = cursor.fetchall
        db.close()
        return data

    def drive_backup(self, drive_dir):
        for k in self.pro_list():
            BackupManager(k[0]).drive_backup(drive_dir)

    def local_backup(self, chdir=None):
        for k in self.pro_list():
            BackupManager(k[0]).local_backup(chdir)

    def remote_backup(self, remote_user, remote_host, remote_port, remote_pass, remote_dest):
        for k in self.pro_list():
            BackupManager(k[0]).remote_backup(remote_user, remote_host, remote_port, remote_pass, remote_dest)


