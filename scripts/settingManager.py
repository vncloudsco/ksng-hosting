#!/usr/bin/env python3

import os
import subprocess
import re
import glob
import shutil
import functionLib as fLib
import sys


class SettingManager:

    def __init__(self, provision=None):
        self.provision = provision
        self.path = '/etc/nginx/conf.d/%s_*.conf' % self.provision
        self.template_file = '/etc/nginx/restrict_access/rule.template'
        self.tmp_file = '/tpm/userdefined_rule.txt'

    def check_authid_existed(self, rule_id):
        string = 'au_%s_%s' % (self.provision, rule_id)
        regex = re.compile(string)
        exist = 0
        for fi in glob.glob(self.path):
            with open(fi, 'r') as fp: lines = fp.read().splitlines()
            for line in lines:
                if regex.search(line):
                    exist = 1
                    print('the rule authentication ID already existed')
                    return False
                    sys.exit(0)

    def check_authenconf_existed(self, rule_id):
        rule_conf = os.path.isfile('/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id))
        # return rule_conf
        if rule_conf:
            print('the authentication conf file already existed')
            return False
            sys.exit(0)

    def check_userconf_existed(self, rule_id):
        user_conf = os.path.isfile('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id))
        # return user_conf
        if user_conf:
            print('the user conf file already existed')
            return False
            sys.exit(0)

    def check_filterid_existed(self, rule_id):
        regex = re.compile('filter_%s_%s' % (self.provision, rule_id))
        for fi in glob.glob(self.path):
            with open(fi, 'r') as fp: lines = fp.read().splitlines()
            for line in lines:
                if regex.search(line):
                    print('the rule filter id already existed')
                    return False
                    sys.exit(0)

    def backup_nginx_conf(self):
        for fi in glob.glob(self.path):
            shutil.copy(fi, '/etc/backup_restric/')

    def rollback(self, rule_id):
        bk_path = '/etc/backup_restric/%s_*' % self.provision
        for fi in glob.glob(bk_path):
            shutil.copy(fi, '/etc/nginx/conf.d/')
        os.remove('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id))
        os.remove('/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id))
        return False
        sys.exit(0)

    def rollback_nginx_only(self):
        bk_path = '/etc/backup_restric/%s_*' % self.provision
        for fi in glob.glob(bk_path):
            shutil.copy(fi, '/etc/nginx/conf.d/')

    @staticmethod
    def replace_multiple(input_file=None, output_file=None, pattern=None, replacement=None):
        f = open(input_file, 'rt')
        g = open(output_file, 'wt')
        for line in f:
            for pat, rep in zip(pattern, replacement):
                line = line.replace(pat, rep)
            g.write(line)
        f.close()
        g.close()

    def inject_rule_to_nginx(self, anchor_string=None, file_included=None):
        for fi in glob.glob(self.path):
            f = open(fi, 'rt')
            data = f.read()
            data.replace(anchor_string, '%s \n\t\tinclude %s;' % (anchor_string, file_included))
            f.close()
            f = open(fi, 'wt')
            f.write(data)
            f.close()

    def add_authentication(self, url=None, user=None, password=None, rule_id=None):
        fLib.verify_prov_existed(self.provision)
        fLib.verify_nginx_prov_existed(self.provision)
        self.check_authid_existed(rule_id)
        self.check_authenconf_existed(rule_id)
        self.check_userconf_existed(rule_id)
        self.backup_nginx_conf()
        self.check_filterid_existed(rule_id)

        output_file = '/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id)

        if url == 'wp-admin':
            pattern = ('location', '#auth_basic', '#auth_basic_user_file', 'provision_name', '}')
            replacement = ('#location', 'auth_basic', 'auth_basic_user_file', 'user_%s_%s' % (self.provision, rule_id), '#}')
            self.replace_multiple(self.template_file, output_file, pattern, replacement)
            # create credential file
            fLib.execute('htpasswd -nb  %s %s > /etc/nginx/restrict_access/user_%s_%s' % (user, password, self.provision, rule_id))
            # configure nginx
            self.inject_rule_to_nginx('#Restric filter here', output_file)

        if url == 'wp-login':
            print('can not add restriction rule to wp-login url')
            return False
            sys.exit(0)

        if url != 'wp-login':
            existed = re.search(url, '/etc/nginx/conf.d/%s_http.conf' % self.provision)
            if bool(existed):
                print('%s has been added in http nginx conf' % url)
                return False
                sys.exit(1)
            existed = re.search(url, '/etc/nginx/conf.d/%s_ssl.conf' % self.provision)
            if bool(existed):
                print('%s has been added in ssl nginx conf' % url)
                return False
                sys.exit(1)

            pattern = ('url', '#auth_basic', '#auth_basic_user_file', 'provision_name')
            replacement = (url, 'auth_basic', 'auth_basic_user_file', 'user_%s_%s' % (self.provision, rule_id))
            self.replace_multiple(self.template_file, output_file, pattern, replacement)
            # create credential file
            fLib.execute('htpasswd -nb  %s %s > /etc/nginx/restrict_access/user_%s_%s' % (user, password, self.provision, rule_id))
            # configure nginx
            self.inject_rule_to_nginx('#Addnew Restrict Filter', output_file)

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            fLib.reload_service('nginx')
            print('Done')
            return True
            sys.exit(0)

        self.rollback(rule_id)

    def add_filterip(self, url=None, ip_address=None, rule_id=None):
        fLib.verify_prov_existed(self.provision)
        fLib.verify_nginx_prov_existed(self.provision)
        self.backup_nginx_conf()
        self.check_filterid_existed(rule_id)

        output_file = '/etc/nginx/restrict_rule/filter_%s_%s' % (self.provision, rule_id)

        if url == 'wp-admin':

            pattern = ('location', '#deny all', '#allow ipas', '}')
            replacement = ('#location', 'deny all', 'allow %s' % ip_address, '#}')
            self.replace_multiple(self.template_file, output_file, pattern, replacement)
            # configure nginx
            self.inject_rule_to_nginx('#Restric filter here', output_file)

        if url == 'wp-login':
            print('can not add restriction rule to wp-login url')
            return False
            sys.exit(0)

        if url != 'wp-login':
            existed = re.search(url, '/etc/nginx/conf.d/%s_http.conf' % self.provision)
            if bool(existed):
                print('%s has been added in http nginx conf' % url)
                return False
                sys.exit(1)
            existed = re.search(url, '/etc/nginx/conf.d/%s_ssl.conf' % self.provision)
            if bool(existed):
                print('%s has been added in ssl nginx conf' % url)
                return False
                sys.exit(1)

            pattern = ('url', '#deny all', '#allow ipas')
            replacement = (url, 'deny all', 'allow $IP' % ip_address)
            self.replace_multiple(self.template_file, output_file, pattern, replacement)
            # configure nginx
            self.inject_rule_to_nginx('#Addnew Restrict Filter', output_file)

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            fLib.reload_service('nginx')
            print('Done')
            return True
            sys.exit(0)

        self.rollback(rule_id)

    def remove_conf_related_nginx(self, pat=None):
        for fi in glob.glob(self.path):
            f = open(fi, 'rt')
            g = open(self.tmp_file, 'wt')
            for line in f:
                if pat not in line:
                    g.write(line)
            f.close()
            g.close()
            shutil.copy(self.tmp_file, fi)
        os.remove(self.tmp_file)

    def delete_authentication(self, url=None, rule_id=None):

        fLib.verify_prov_existed(self.provision)
        fLib.verify_nginx_prov_existed(self.provision)
        self.backup_nginx_conf()

        string = 'au_%s_%s' % (self.provision, rule_id)
        regex = re.compile(string)
        exist = 0
        for fi in glob.glob(self.path):
            with open(fi, 'r') as fp: lines = fp.read().splitlines()
            for line in lines:
                if regex.search(line):
                    exist = 1
                    break
        if exist == 0:
            print('Not found the rule authentication ID as %s' % rule_id)
            return False
            sys.exit(0)

        if url == 'wp-admin':
            self.remove_conf_related_nginx('au_%s_%s' % (self.provision, rule_id))

        if url == 'wp-login':
            print('can not configure wp-login url')
            return False
            sys.exit(1)

        if url != 'wp-login':
            existed = re.search(url, '/etc/nginx/conf.d/%s_http.conf' % self.provision)
            if not bool(existed):
                print('Not found %s location in http nginx conf' % url)
                return False
                sys.exit(0)
            existed = re.search(url, '/etc/nginx/conf.d/%s_ssl.conf' % self.provision)
            if not bool(existed):
                print('Not found %s location in ssl nginx conf' % url)
                return False
                sys.exit(0)

            self.remove_conf_related_nginx('au_%s_%s' % (self.provision, rule_id))

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            os.remove('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id))
            os.remove('/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id))
            print('Done')
            fLib.reload_service('nginx')
            return True
            sys.exit(0)
        else:
            print('NGINX config check failed')
            self.rollback_nginx_only()
            return False
            sys.exit(1)

    def delete_filterip(self, url=None, rule_id=None):
        fLib.verify_prov_existed(self.provision)
        fLib.verify_nginx_prov_existed(self.provision)
        self.backup_nginx_conf()

        rule_regex = re.compile('filter_%s_%s' % (self.provision, rule_id))

        if url == 'wp-admin':
            regex = re.compile(url)
            exist = 0
            exist_rule = 0
            for fi in glob.glob(self.path):
                with open(fi, 'r') as fp:
                    lines = fp.read().splitlines()
                for line in lines:
                    if regex.search(line):
                        exist = 1
                    if rule_regex.search(line):
                        exist_rule = 1

            if exist == 0:
                print('Not found the %s location in NGINX config' % url)
                return False
                sys.exit(0)

            if exist_rule == 0:
                print('Not found the rule ID as %s in NGINX config' % rule_id)
                return False
                sys.exit(0)

            self.remove_conf_related_nginx('filter_%s_%s' % (self.provision, rule_id))

        if url != 'wp-login':
            exist_rule = 0
            for fi in glob.glob(self.path):
                with open(fi, 'r') as fp:
                    lines = fp.read().splitlines()
                for line in lines:
                    if rule_regex.search(line):
                        exist_rule = 1
                        break

            if exist_rule == 0:
                print('Not found the rule ID as %s in NGINX config' % rule_id)
                return False
                sys.exit(0)

            self.remove_conf_related_nginx('filter_%s_%s' % (self.provision, rule_id))

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            os.remove('/etc/nginx/restrict_access/filter_%s_%s' % (self.provision, rule_id))
            print('Done')
            fLib.reload_service('nginx')
            return True
            sys.exit(0)
        else:
            print('NGINX config check failed')
            self.rollback_nginx_only()
            return False
            sys.exit(1)
