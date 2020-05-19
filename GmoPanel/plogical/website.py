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
import json
from plogical import hashPassword,system_os
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
            # with zipfile.ZipFile(path+'/'+namezip,'r') as zip_ref:
            #     zip_ref.extractall(path)
            os.system('unzip -qq ' + path + '/{}'.format(namezip))
            if not os.path.isdir(path+'/'+'wp-content'):
                raise ValueError('Failed - No such wp-content source directory')

            # apply source
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
            pass_mysql = fileMysqlConf[1].replace('"', '').replace('\n','')
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
                conn = MySQLdb.connect(host='localhost',user='root',passwd=pass_mysql)
                cursor = conn.cursor()
                cursor.execute("DROP database IF EXISTS {}".format(db_name))
                cursor.execute("CREATE database {}".format(db_name))
                cursor.execute("grant all privileges on {}.* to '{}'@'%' identified by '{}'".format(db_name,db_user,db_pass))
                cursor.execute('flush privileges')
                conn.commit()
                conn.close()
                # import data .sql to database
                os.system('mysql -p{} {} < {}'.format(pass_mysql,db_name,path+'/'+namesql))
                # random Pass admin and hash pass
                pass_admin = hashPassword.generate_pass(10)
                pass_admin_md5 = hashlib.md5(pass_admin.encode()).hexdigest()
                db = MySQLdb.connect(host='localhost',user='root',passwd=pass_mysql,database=db_name)
                cursor = db.cursor()
                cursor.execute("UPDATE {}options SET option_value = 'http://{}' WHERE option_id in(1,2)".format(wp_prefix,data['domain']))
                cursor.execute("UPDATE {}users SET user_login='WPadmiN',user_pass='{}',user_email='{}',user_nicename='Admin',display_name='Admin' WHERE ID = 1".format(wp_prefix,pass_admin_md5,str(data['email'])))
                db.commit()
                db.close()
            except ConnectionError:
                raise ValueError('Can not connect MYSQL')

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
            if os.path.isfile(provisionPath + '/wp-config.php.origi'):
                shutil.move(provisionPath+'/wp-config.php.origi',provisionPath+'/wp-config.php')
            return {'status': 0, 'msg': str(e)}

    def migration_wp(self,domain=None):
        """
        execute source .zip .gz from DocumentRoot website
        :return:
        """
        try:
            # extractall
            os.chdir('/home/{}/{}/Up/'.format(self.userName,self.proName))
            os.system('tar -xzf /home/{}/{}/Up/*.tar.gz'.format(self.userName,self.proName))
            os.system('unzip -qq /home/{}/{}/Up/*.zip'.format(self.userName,self.proName))
            os.system('gunzip -d /home/{}/{}/Up/*.sql.gz'.format(self.userName,self.proName))
            list_path = system_os.find_sub('/home/{}/{}/Up/'.format(self.userName, self.proName), '.trash')
            for sub in list_path:
                shutil.rmtree(sub)
            list_path = system_os.find_sub('/home/{}/{}/Up/'.format(self.userName,self.proName),'wp-content')
            if not list_path:
                raise ValueError('Failed - can not find your website documentroot')
            wp_document = list_path[0].replace('wp-content','')
            os.system('rm -rf /home/{}/{}/DocumentRoot/wp-content/cache/*'.format(self.userName,self.proName))
            os.system('rsync -azh {}/* /home/{}/{}/DocumentRoot/'.format(wp_document,self.userName,self.proName))
            list_file = system_os.find_file('/home/{}/{}/DocumentRoot/'.format(self.userName,self.proName),'wp-config.php')
            if not list_file:
                raise ValueError('Failed - can not find your file wp-config.php')
            wp_config = list_file[0]
            # get config db provision old
            fileConfig = open(wp_config, "r")
            for line in fileConfig:
                if re.search("DB_NAME", line):
                    db_name_old = line.replace('\n', '').split("'")[3]
                if re.search("DB_USER", line):
                    db_user_old = line.replace('\n', '').split("'")[3]
                if re.search("DB_PASSWORD", line):
                    db_pass_old = line.replace('\n', '').split("'")[3]
                if re.search('\$table_prefix', line):
                    wp_prefix_old = line.replace('\n', '').split("'")[1]
            fileConfig.close()
            mysql_path = system_os.find_file('/home/{}/{}/'.format(self.userName,self.proName),db_name_old+'.sql')[0]
            shutil.move('/home/{}/{}/wp-config.php'.format(self.userName,self.proName), '/home/{}/{}/wp-config.php.old'.format(self.userName,self.proName))
            # get config db provision
            fileConfig = open('/home/{}/{}/wp-config.php.old'.format(self.userName,self.proName), "r")
            for line in fileConfig:
                if re.search("DB_NAME", line):
                    db_name = line.replace('\n', '').split("'")[3]
                if re.search("DB_USER", line):
                    db_user = line.replace('\n', '').split("'")[3]
                if re.search("DB_PASSWORD", line):
                    db_pass = line.replace('\n', '').split("'")[3]
            fileConfig.close()
            # drop all table db old
            os.chdir('/home/{}/{}'.format(self.userName,self.proName))
            os.system("echo 'SET FOREIGN_KEY_CHECKS = 0;' > temp.txt")
            os.system('mysqldump -u{} -p{} --add-drop-table --no-data {} | grep ^DROP >> temp.txt'.format(db_user,db_pass,db_name))
            os.system('echo "mysqldump" $?')
            os.system('echo "SET FOREIGN_KEY_CHECKS = 1;" >> temp.txt')
            os.system('mysql -u{} -p{} {} < temp.txt'.format(db_user,db_pass,db_name))
            os.system('echo "DROP ALL TABLE" $?')
            # import database new
            shutil.move(mysql_path,'/home/{}/{}/kusanagi.sql'.format(self.userName,self.proName))
            os.system("sed 's/ENGINE=MyISAM/ENGINE=InnoDB/g' kusanagi.sql  > kusanagi.InnoDB.sql")
            os.system('mysql -u{} -p{} -h localhost {} < kusanagi.InnoDB.sql'.format(db_user,db_pass,db_name))
            try:
                db = MySQLdb.connect(host='localhost', user=db_user, passwd=db_pass, database=db_name)
                cursor = db.cursor()
                cursor.execute("UPDATE {}options SET option_value = 'http://{}' WHERE option_id in(1,2)".format(wp_prefix_old,domain))
                db.commit()
                db.close()
            except ConnectionError:
                raise ValueError('Can not connect mysql')

            shutil.move(wp_config,'/home/{}/{}/wp-config.backup.php'.format(self.userName,self.proName))
            fread = open('/home/{}/{}/wp-config.backup.php'.format(self.userName,self.proName), "r")
            fwrite = open('/home/{}/{}/wp-config.php'.format(self.userName,self.proName), "w")
            for line in fread:
                if re.search("define\('DB_NAME',", line):
                    fwrite.write("define('DB_NAME', '{}');".format(db_name))
                elif re.search("define\('DB_USER'", line):
                    fwrite.write("define('DB_USER', '');".format(db_user))
                elif re.search("define\('DB_PASSWORD'", line):
                    fwrite.write("define('DB_PASSWORD', '');".format(db_pass))
                elif re.search("define\('DB_HOST',", line):
                    fwrite.write("define('DB_HOST', 'localhost');")
                else:
                    fwrite.write(line)
            fread.close()
            fwrite.close()
            # clear file and folder
            if os.path.isdir('/home/{}/{}/Up'.format(self.userName, self.proName)):
                shutil.rmtree('/home/{}/{}/Up'.format(self.userName, self.proName))
            os.chdir('/home/{}/{}'.format(self.userName, self.proName))
            os.system('rsync -azh /backup/wpdefault.vn/DocumentRoot/ /home/{}/{}/DocumentRoot/'.format(self.userNam,self.proName))
            shutil.chown('/home/{}/{}'.format(self.userName, self.proName), user=self.userName, group=self.userName)
            os.system('find {} -type d | xargs chmod 0755'.format('/home/{}/{}'.format(self.userName,self.proName)))
            os.system('find {} -type f | xargs chmod 0644'.format('/home/{}/{}'.format(self.userName,self.proName)))
            if os.path.isfile("/home/{}/{}/DocumentRoot/wp-content/advanced-cache.php".format(self.userName,self.proName)):
                os.remove("/home/{}/{}/DocumentRoot/wp-content/advanced-cache.php".format(self.userName,self.proName))
            # turn on cache
            os.system('kusanagi target {} > /dev/null 2>&1; kusanagi bcache clear > /dev/null 2>&1; kusanagi fcache clear > /dev/null 2>&1; kusanagi bcache on > /dev/null 2>&1; kusanagi fcache on > /dev/null 2>&1'.format(self.proName))

            return {'status': 1, 'msg': 'Done!'}
        except BaseException as e:
            if os.path.isdir('/home/{}/{}/Up'.format(self.userName,self.proName)):
                shutil.rmtree('/home/{}/{}/Up'.format(self.userName,self.proName))
            return {'status': 0, 'msg': str(e)}

    def resource_up(self):
        """
        execute source code another php
        :return:
        """
        try:

            # extractall
            os.chdir('/home/{}/{}/Up/'.format(self.userName, self.proName))
            os.system('tar -xzf /home/{}/{}/Up/*.tar.gz'.format(self.userName, self.proName))
            os.system('unzip -qq /home/{}/{}/Up/*.zip'.format(self.userName, self.proName))
            os.system('gunzip -d /home/{}/{}/Up/*.sql.gz'.format(self.userName, self.proName))
            list_path = system_os.find_sub('/home/{}/{}/Up/'.format(self.userName, self.proName), '.trash')
            for sub in list_path:
                shutil.rmtree(sub)
            list_sub = system_os.find_sub('/home/{}/{}/Up/'.format(self.userName,self.proName),'public_html')
            if list_sub:
                os.system('rsync -azh --exclude=*.zip {}/* /home/{}/{}/DocumentRoot/'.format(list_sub[0],self.userName,self.proName))
            else:
                list_file = system_os.find_file('/home/{}/{}/Up/'.format(self.userName,self.proName),'index.php')
                if list_file:
                    path_root = list_file[0].replace('index.php','')
                    os.system('rsync -azh --exclude=*.zip  {}/* /home/{}/{}/DocumentRoot/'.format(path_root,self.userName,self.proName))
                else:
                    raise ValueError('Failed - can not find your website documentroot')
            shutil.rmtree('/home/{}/{}/Up'.format(self.userName,self.proName))
            shutil.chown('/home/{}/{}'.format(self.userName, self.proName), user=self.userName, group=self.userName)
            os.system('find {} -type d | xargs chmod 0755'.format('/home/{}/{}'.format(self.userName, self.proName)))
            os.system('find {} -type f | xargs chmod 0644'.format('/home/{}/{}'.format(self.userName, self.proName)))
            return {'status': 1, 'msg': 'Done!'}
        except BaseException as e:
            if os.path.isdir('/home/{}/{}/Up'.format(self.userName, self.proName)):
                shutil.rmtree('/home/{}/{}/Up'.format(self.userName, self.proName))
            return {'status': 0, 'msg': str(e)}

    def mysqldb_up(self,db_user=None,db_pass=None,db_name=None):
        """
        execute database
        :param user_db:
        :param pass_db:
        :param db_name:
        :return:
        """

        try:
            # extractall
            os.chdir('/home/{}/Up/'.format(self.userName))
            os.system('tar -xzf /home/{}/Up/*.tar.gz'.format(self.userName))
            os.system('unzip -qq /home/{}/Up/*.zip'.format(self.userName))
            os.system('gunzip -d /home/{}/Up/*.sql.gz'.format(self.userName))
            # remove .trash
            list_path = system_os.find_sub('/home/{}/{}/Up/'.format(self.userName, self.proName), '.trash')
            for sub in list_path:
                shutil.rmtree(sub)
            # remove file name default
            if os.path.isfile('/home/{}/Up/kusanagi.sql'.format(self.userName)):
                os.remove('/home/{}/Up/kusanagi.sql'.format(self.userName))
            if os.path.isfile('/home/{}/Up/kusanagi.InnoDB.sql'.format(self.userName)):
                os.remove('/home/{}/Up/kusanagi.InnoDB.sql'.format(self.userName))
            # find lisst .sql upload
            list_file = glob.glob('/home/{}/Up/*.sql'.format(self.userName))
            if list_file:
                sql_path = list_file[0]
                shutil.move(sql_path,'/home/{}/Up/kusanagi.sql'.format(self.userName))
                os.system("sed 's/ENGINE=MyISAM/ENGINE=InnoDB/g' /home/{}/Up/kusanagi.sql  > /home/{}/Up/kusanagi.InnoDB.sql".format(self.userName,self.userName))
                if os.path.getsize('/home/{}/Up/kusanagi.InnoDB.sql'.format(self.userName)) > 10:
                    # get PW mysql
                    fileMysqlConf = open('/root/.my.cnf', "r").read().split('password="')
                    pass_mysql = fileMysqlConf[1].replace('"', '').replace('\n','')
                    try:
                        # create database Provision
                        conn = MySQLdb.connect(host='localhost', user='root', passwd=pass_mysql)
                        cursor = conn.cursor()
                        cursor.execute("DROP database IF EXISTS {}".format(db_name))
                        cursor.execute("CREATE database {}".format(db_name))
                        cursor.execute("grant all privileges on {}.* to '{}'@'%' identified by '{}'".format(db_name, db_user, db_pass))
                        cursor.execute('flush privileges')
                        conn.commit()
                        conn.close()
                        # import data .sql to database
                        os.system('mysql -uroot -p{} -h localhost {} < {}'.format(pass_mysql, db_name, '/home/{}/Up/kusanagi.InnoDB.sql'.format(self.userName)))
                    except ConnectionError:
                        raise ValueError('Can not connect MYSQL')
                    shutil.rmtree('/home/{}/Up'.format(self.userName))
                    return {'status': 1, 'msg': "Done"}
                else:
                    raise ValueError('Mysql File Failed')
            else:
                raise ValueError("Failed - can not find your mysql file")
        except BaseException as e:
            if os.path.isdir('/home/{}/Up'.format(self.userName)):
                shutil.rmtree('/home/{}/Up'.format(self.userName))
            return {'status': 0, 'msg': str(e)}




