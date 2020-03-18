import os
import psutil
from pathlib import Path
import sys
import glob
import django
import wget
import zipfile
import logging
import shutil
import re
import mysql.connector as MySQLdb
import hashlib
import fileinput
import subprocess

sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
logger = logging.getLogger(__name__)

import json
from plogical import hashPassword
from websiteManager.models import Provision
from loginSys.models import Account
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

class Website:

    def __init__(self,proName=None,userName='kusanagi'):
        self.proName = proName
        self.userName = userName
        self.status = 0

    def createWebsite(self,data=None):
        """
        create wwebsite
        :param data:
        :return:
        """
        listCms = {
            1: 'wordpress',
            2: 'woo',
            3: 'drupal',
            4: 'c5',
            5: 'LAMP',
        }
        try:
            cmd = 'kusanagi provision --' + listCms[int(data['app_id'])] + ' --wplang en_US --fqdn ' + data['domain'] + ' --email ' + data['email'] + ' --dbname ' + data['db_name'] + ' --dbuser ' + data['db_user'] + ' --dbpass ' + data['db_password'] + ' ' + self.proName
            res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = res.stdout
            if re.search('Failed',str(output)):
                raise ValueError(str(output))
            return {'status': 1,'msg': 'Done!'}
        except BaseException as e:
            return {'status': 0,'msg': str(e)}

    def deleteWebsite(self):
        """
        Delete provision
        :return:
        """
        try:
            cmd = 'kusanagi remove -y {}'.format(self.proName)
            res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = res.stdout
            if re.search('Done.',str(output)):
                return {'status': 1,'msg': "Done!"}
            raise ValueError(str(output))
        except BaseException as e:
            return {'status': 0,'msg': str(e)}


    def activeTheme(self,data=None):
        """
        active Theme wordpress
        :param data:
        :return:
        """
        try:
            # download source
            provisionPath = '/home/{}/{}'.format(self.userName,self.proName)
            path = '/home/{}/{}/Up'.format(self.userName,self.proName)
            pathRoot = '/home/{}/{}/DocumentRoot/'.format(self.userName,self.proName)
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.mkdir(path)
            os.chdir(path)
            namezip = 'wordpress{}.top.zip'.format(data['theme_id'])
            namesql = 'wp{}.sql'.format(data['theme_id'])
            wget.download('http://tentenwordpress1.top/code/tentenwordpress{}.top.zip'.format(data['theme_id']), path+'/'+namezip)
            wget.download('http://tentenwordpress1.top/db/wp{}.sql'.format(data['theme_id']), path+'/'+namesql)
            os.system('unzip -qq '+path+'/{}'.format(namezip))
            #with zipfile.ZipFile(path+'/'+namezip,'r') as zip_ref:
            #    zip_ref.extractall(path)
            #os.system('mv {}/* {}'.format(path+'/tentenwordpress{}.top'.format(data['theme_id']),path))
            if not os.path.isdir(path+'/'+'wp-content'):
                raise ValueError('Failed - No such wp-content source directory')
            # apply source
            #shutil.rmtree(pathRoot+'wp-content/cache/*')
            os.system('rsync --exclude=*.zip -azh {}/* {}'.format(path,pathRoot))
            if not os.path.isfile(pathRoot+'wp-config.php'):
                raise ValueError('Failed - No such wp-config.php source file')

            file = open(pathRoot + 'wp-config.php', "r")
            for line in file:
                if re.search('\$table_prefix', line):
                    wp_prefix = line.replace('\n', '').split("'")[1]
                    break
            if not wp_prefix:
                raise ValueError('Can not find table_prefix in file wp-config.php')

            # restore mysql
            if not glob.glob(path+'/*.sql'):
                raise ValueError('Failed - MySQL file not found')
            file = os.stat(path+'/'+namesql)
            if file.st_size < 1024:
                raise ValueError('MySQL source file errors')
            os.chdir(path.replace('/Up',''))
            shutil.move('wp-config.php', 'wp-config.php.origi')
            # get PW mysql
            fileMysqlConf = open('/root/.my.cnf', "r").read().split('password="')
            pass_mysql = fileMysqlConf[1].replace('"', '')
            pass_mysql = pass_mysql.replace('\n', '')
            # get config db provision
            fileConfig = open('{}/wp-config.php.origi'.format(provisionPath), "r")
            for line in fileConfig:
                if re.search("DB_NAME", line):
                    db_name = line.replace('\n', '').split("'")[3]
                if re.search("DB_USER", line):
                    db_user = line.replace('\n', '').split("'")[3]
                if re.search("DB_PASSWORD", line):
                    db_pass = line.replace('\n', '').split("'")[3]
            fileConfig.close()
            try:
                # create database Provision
                conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd=pass_mysql)
                cursor = conn.cursor()
                cursor.execute("DROP database IF EXISTS {}".format(db_name))
                cursor.execute("CREATE database {}".format(db_name))
                cursor.execute("grant all privileges on {}.* to '{}'@'%' identified by '{}'".format(db_name,db_user,db_pass))
                cursor.execute('flush privileges')
                conn.commit()
                conn.close()
                # import data .sql to database
                os.system('mysql -uroot -p{} {} < {}'.format(pass_mysql,db_name,path+'/'+namesql))
                # random Pass admin and hash pass
                pass_admin = hashPassword.generate_pass(10)
                pass_admin_md5 = hashlib.md5(pass_admin.encode()).hexdigest()
                db = MySQLdb.connect(host='127.0.0.1',user='root',passwd=pass_mysql,database=db_name)
                cursor = db.cursor()
                cursor.execute("UPDATE {}options SET option_value = 'http://{}' WHERE option_id in(1,2)".format(wp_prefix,data['domain']))
                cursor.execute("UPDATE {}users SET user_login='WPadmiN',user_pass='{}',user_email='{}',user_nicename='Admin',display_name='Admin' WHERE ID = 1".format(wp_prefix,pass_admin_md5,data['email']))
                db.commit()
                db.close()
            except BaseException as e:
                raise ValueError(str(e))

            # wp config
            shutil.move(pathRoot+'/wp-config.php',provisionPath+'/wp-config.php')
            f = open(provisionPath+'/wp-config.php', "r")
            for line in f:
                if re.search('DB_NAME', line):
                    db_name_temp = line.replace('\n', '').split("'")[3]
                if re.search('DB_USER', line):
                    db_user_temp = line.replace('\n', '').split("'")[3]
                if re.search('DB_PASSWORD', line):
                    db_pass_temp = line.replace('\n', '').split("'")[3]
                if re.search('DB_HOST', line):
                    db_host_temp = line.replace('\n', '').split("'")[3]
            f.close()
            f = open(provisionPath+'/wp-config.php', "r")
            dataText = f.read()
            f.close()
            dataText = dataText.replace("define('DB_NAME', '{}')".format(db_name_temp), "define('DB_NAME', '{}')".format(db_name))
            dataText = dataText.replace("define('DB_USER', '{}')".format(db_user_temp), "define('DB_USER', '{}')".format(db_user))
            dataText = dataText.replace("define('DB_PASSWORD', '{}')".format(db_pass_temp), "define('DB_PASSWORD', '{}')".format(db_pass))
            dataText = dataText.replace("define('DB_HOST', '{}')".format(db_host_temp),"define('DB_HOST', '{}')".format('localhost'))
            f = open(provisionPath+'/wp-config.php', 'w')
            f.write(dataText)
            f.close()
            shutil.rmtree(path)
            shutil.chown('/home/{}/{}'.format(self.userName,self.proName), user='kusanagi', group='kusanagi')
            os.system('find {} -type d | xargs chmod 0755'.format(provisionPath))
            os.system('find {} -type f | xargs chmod 0644'.format(provisionPath))
            shutil.chown(provisionPath+'/wp-config.php', user='kusanagi', group='www')
            if os.path.isfile("{}/wp-content/advanced-cache.php".format(pathRoot)):
                os.remove("{}/wp-content/advanced-cache.php".format(pathRoot))

            return {
                'status': 1,
                'msg': 'Your website has been created successfully',
                'data': {
                    'url': "http://{}/wp-admin".format(data['domain']),
                    'user': 'WPadmiN',
                    'password': pass_admin
                }
            }
        except BaseException as e:
            if os.path.isdir(path):
               shutil.rmtree(path)
            return {'status': 0, 'msg': str(e)}




