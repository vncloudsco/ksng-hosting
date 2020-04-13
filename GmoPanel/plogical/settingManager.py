#!/usr/bin/env python3

import os
import sys
import subprocess
import re
import glob
import shutil
import pathlib
import urllib.parse
import plogical.functionLib as fLib
import django
sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
from websiteManager.models import Provision
from django.core.exceptions import ObjectDoesNotExist


class SettingManager:

    def __init__(self, provision=None):
        self.provision = provision
        self.path = '/etc/nginx/conf.d/%s_*.conf' % self.provision
        self.template_file = '/etc/nginx/restrict_access/rule.template'
        self.filter_template_file = '/etc/nginx/restrict_rule/rule.template'
        self.tmp_file = '/opt/user_defined_rule.txt'

    @staticmethod
    def check_existence_in_file(pattern, source_files):
        regex = re.compile(pattern)
        for fi in glob.glob(source_files):
            with open(fi, 'rt') as fp: lines = fp.read().splitlines()
            for line in lines:
                if regex.search(line):
                    return True
        return False

    def backup_nginx_conf(self):
        for fi in glob.glob(self.path):
            shutil.copy(fi, '/etc/backup_restrict/')

    def rollback_nginx_only(self):
        bk_path = '/etc/backup_restrict/%s_*' % self.provision
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
            data = data.replace(anchor_string, '%s \n\tinclude %s;' % (anchor_string, file_included))
            f.close()
            f = open(fi, 'wt')
            f.write(data)
            f.close()

    def add_authentication(self, url=None, user=None, password=None, rule_id=None):
        if not fLib.verify_prov_existed(self.provision):
            return False
        if not fLib.verify_nginx_prov_existed(self.provision):
            return False
        if self.check_existence_in_file('au_%s_%s' % (self.provision, rule_id), self.path):
            print('the rule authentication ID already existed')
            return False
        if os.path.isfile('/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id)):
            print('the authentication file already existed')
            return False
        if os.path.isfile('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id)):
            print('the user conf file already existed')
            return False
        self.backup_nginx_conf()

        output_file = '/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id)

        if url == 'wp-admin':
            pattern = ('location', '#auth_basic', '#auth_basic_user_file', 'provision_name', '}')
            replacement = ('#location', 'auth_basic', 'auth_basic_user_file', 'user_%s_%s' % (self.provision, rule_id), '#}')
            self.replace_multiple(self.template_file, output_file, pattern, replacement)
            fLib.execute('htpasswd -nb  %s %s > /etc/nginx/restrict_access/user_%s_%s' % (user, password, self.provision, rule_id))
            self.inject_rule_to_nginx('#Restric filter here', output_file)
        elif url == 'wp-login':
            print('can not add restriction rule to wp-login url')
            return False
        else:
            if self.check_existence_in_file(url, self.path):
                print(' the %s location has been added' % url)
                return False
            else:
                pattern = ('url', '#auth_basic', '#auth_basic_user_file', 'provision_name')
                replacement = (url, 'auth_basic', 'auth_basic_user_file', 'user_%s_%s' % (self.provision, rule_id))
                self.replace_multiple(self.template_file, output_file, pattern, replacement)
                fLib.execute('htpasswd -nb  %s %s > /etc/nginx/restrict_access/user_%s_%s' % (user, password, self.provision, rule_id))
                self.inject_rule_to_nginx('#Addnew Restrict Filter', output_file)

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            fLib.reload_service('nginx')
            print('Done')
            return True

        self.rollback_nginx_only()
        os.remove(output_file)
        os.remove('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id))
        return False

    def add_filterip(self, url=None, ip_address=None, rule_id=None):
        if not fLib.verify_prov_existed(self.provision):
            return False
        if not fLib.verify_nginx_prov_existed(self.provision):
            return False
        self.backup_nginx_conf()
        if self.check_existence_in_file('filter_%s_%s' % (self.provision, rule_id), self.path):
            print('the filter ID already existed')
            return False

        output_file = '/etc/nginx/restrict_rule/filter_%s_%s' % (self.provision, rule_id)

        if url == 'wp-admin':
            pattern = ('location', '#deny all', '#allow ipas', '}')
            replacement = ('#location', 'deny all', 'allow %s' % ip_address, '#}')
            self.replace_multiple(self.filter_template_file, output_file, pattern, replacement)
            self.inject_rule_to_nginx('#Restric filter here', output_file)
        elif url == 'wp-login':
            print('can not add restriction rule to wp-login url')
            return False
        else:
            if self.check_existence_in_file(url, self.path):
                print(' the %s location has been added' % url)
                return False
            else:
                pattern = ('url', '#deny all', '#allow ipas')
                replacement = (url, 'deny all', 'allow %s' % ip_address)
                self.replace_multiple(self.filter_template_file, output_file, pattern, replacement)
                self.inject_rule_to_nginx('#Addnew Restrict Filter', output_file)

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            fLib.reload_service('nginx')
            print('Done')
            return True

        self.rollback_nginx_only()
        os.remove(output_file)
        return False

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

        if not fLib.verify_prov_existed(self.provision):
            return False
        if not fLib.verify_nginx_prov_existed(self.provision):
            return False
        self.backup_nginx_conf()

        if not self.check_existence_in_file('au_%s_%s' % (self.provision, rule_id), self.path):
            print('Not found the rule authentication ID as %s' % rule_id)
            return False

        if url == 'wp-login':
            print('can not configure wp-login url')
            return False
        else:
            self.remove_conf_related_nginx('au_%s_%s' % (self.provision, rule_id))

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            os.remove('/etc/nginx/restrict_access/user_%s_%s' % (self.provision, rule_id))
            os.remove('/etc/nginx/restrict_access/au_%s_%s' % (self.provision, rule_id))
            print('Done')
            fLib.reload_service('nginx')
            return True
        else:
            print('NGINX config check failed')
            self.rollback_nginx_only()
            return False

    def delete_filterip(self, url=None, rule_id=None):
        if not fLib.verify_prov_existed(self.provision):
            return False
        if not fLib.verify_nginx_prov_existed(self.provision):
            return False
        self.backup_nginx_conf()

        if url == 'wp-login':
            print('can not configure wp-login url')
            return False
        else:
            if not self.check_existence_in_file('filter_%s_%s' % (self.provision, rule_id), self.path):
                print('Not found the rule ID as %s in nginx config' % rule_id)
                return False
            else:
                self.remove_conf_related_nginx('filter_%s_%s' % (self.provision, rule_id))

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            os.remove('/etc/nginx/restrict_rule/filter_%s_%s' % (self.provision, rule_id))
            print('Done')
            fLib.reload_service('nginx')
            return True
        else:
            print('NGINX config check failed')
            self.rollback_nginx_only()
            return False

    def before_edit_nginx(self):
        if not fLib.verify_prov_existed(self.provision):
            return False
        nginx_check = fLib.check_nginx_valid()
        if nginx_check > 0:
            print('nginx config check failed. Please abort')
            return False
        else:
            if not fLib.verify_nginx_prov_existed(self.provision):
                return False
            else:
                for fi in glob.glob(self.path):
                    shutil.copy(fi, '/etc/nginx/bk_nginx_conf/')
                    shutil.copy(fi, '/etc/temp_nginx_conf/')
                shutil.chown('/etc/temp_nginx_conf/', 'httpd', 'www')
                for root, dirs, files in os.walk('/etc/temp_nginx_conf/'):
                    for name in files:
                        shutil.chown(os.path.join(root, name), 'httpd', 'www')
                return True

    def edit_nginx(self, domain_name):
        if not fLib.verify_prov_existed(self.provision) or not fLib.verify_prov_existed(domain_name):
            return False
        if not os.path.isfile('/etc/temp_nginx_conf/%s_http.conf' % self.provision) or not os.path.isfile('/etc/temp_nginx_conf/%s_ssl.conf' % self.provision):
            print('No temporary nginx file exists. Please backup firstly')
            return False
        # check new nginx conf right after editing
        for fi in glob.glob('/etc/temp_nginx_conf/%s_*.conf' % self.provision):
            shutil.copy(fi, '/etc/nginx/conf.d/')
        nginx_check = fLib.check_nginx_valid()
        if nginx_check > 0:
            # rollback
            for fi in glob.glob('/etc/nginx/bk_nginx_conf/%s_*.conf' % self.provision):
                shutil.copy(fi, '/etc/nginx/conf.d/')
            # fLib.reload_service('nginx')
            print('Insert failed. Might your conf is invalid')
            return False
        else:
            # if editing nginx okie, apply new conf
            nginx_check = fLib.check_nginx_valid()
            if nginx_check == 0:
                fLib.reload_service('nginx')
                return True
            else:
                print('nginx conf check failed. Please run "nginx -t" for more details')
                return False

    def replace_in_file(self, regex_pattern, replacement, file_path):
        regex = re.compile(regex_pattern)
        for fi in glob.glob(file_path):
            f = open(fi, 'rt')
            g = open('/opt/tmp_nginx.conf', 'wt')
            for line in f:
                line = regex.sub(replacement, line)
                g.write(line)
            f.close()
            g.close()
            shutil.copy('/opt/tmp_nginx.conf', fi)
        os.remove('/opt/tmp_nginx.conf')

    def f_cache(self, action=None, uri=None):
        if action == 'on':
            # regex = re.compile(r"set\s+\$do_not_cache\s+1\s*;\s+#+\s+page\s+cache")
            pat = 'set\s+\$do_not_cache\s+1\s*;\s+#+\s+page\s+cache'
            repl = 'set $do_not_cache 0; ## page cache'
            self.replace_in_file(pat, repl, self.path)
        if action == 'off':
            pat = 'set\s+\$do_not_cache\s+0\s*;\s*#+\s*page\s*cache'
            repl = 'set $do_not_cache 1; ## page cache'
            self.replace_in_file(pat, repl, self.path)
        if action == 'clear':
            nginx_cache_dir = '/var/cache/nginx/wordpress'
            p = pathlib.Path(nginx_cache_dir)
            if p.exists():
                res = fLib.execute('ls -dl %s | wc -l' % nginx_cache_dir) # deo hieu de lam gi
                if p.owner() == 'httpd' and int(res) == 1:
                    fqdn = fLib.get_fqdn(self.provision)
                    if uri:
                        url_unicode = urllib.parse.quote(uri)
                        if not url_unicode.startswith('/', 0, 1):
                            url_unicode = '/%s' % url_unicode
                        command = 'grep -i -a -r -m 1 -E "^KEY.*:https?://%s%s" %s' % (
                        fqdn, url_unicode, nginx_cache_dir)
                        # res = fLib.execute('grep -i -a -r -m 1 -E "^KEY.*:https?://%s%s" %s' % (
                        # fqdn, url_unicode, nginx_cache_dir))
                        try:
                            res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, universal_newlines=True)
                            g = open('/opt/tmp_nginx.conf', 'w')
                            g.write(res.stdout)
                            g.close()
                            g = open('/opt/tmp_nginx.conf', 'r')
                            for line in g:
                                binary_file = line.replace(':KEY:', '').split()[0]
                                os.remove(binary_file)
                            g.close()
                        except subprocess.CalledProcessError as error:
                            if error.returncode > 0:
                                print("URL has not been cached")
                                return True
                    else:
                        command = 'grep -r -E "%s" %s' % (fqdn, nginx_cache_dir)
                        # res = fLib.execute('grep -r -E "%s" %s' % (fqdn, nginx_cache_dir))
                        try:
                            res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, universal_newlines=True)
                            g = open('/opt/tmp_nginx.conf', 'w')
                            g.write(res.stdout)
                            g.close()
                            g = open('/opt/tmp_nginx.conf', 'r')
                            for line in g:
                                binary_file = line.split()[2]
                                os.remove(binary_file)
                            g.close()
                        except subprocess.CalledProcessError as error:
                            if error.returncode > 0:
                                print("No cache found")
                                return True
            else:
                print('Nginx cache dir %s is not found' % nginx_cache_dir)
                return False

        nginx_check = fLib.check_nginx_valid()
        if nginx_check == 0:
            fLib.reload_service('nginx')
            return True
        else:
            print('Nginx conf check failed. Please run "nginx -t" for more details')
            return False

    def b_cache(self, action=None, uri=None):
        try:
            profile_info = Provision.objects.get(provision_name='%s' % self.provision)
        except ObjectDoesNotExist as error:
            return error
        kusanagi_dir = '/home/kusanagi/%s' % self.provision
        app_id = profile_info.app_id
        if not pathlib.Path(kusanagi_dir).exists():
            print("%s is not found" % kusanagi_dir)
            return False
        if app_id == 1:
            if os.path.isfile('%s/wp-config.php' % kusanagi_dir):
                wpconfig = '%s/wp-config.php' % kusanagi_dir
            elif os.path.isfile('%s/DocumentRoot/wp-config.php' % kusanagi_dir):
                wpconfig = '%s/DocumentRoot/wp-config.php' % kusanagi_dir
            else:
                wpconfig = ""
        if wpconfig == "":
            print("WordPress is not installed. Nothing to do")
            return False
        regex = re.compile("^.*define\('WP_CACHE'")
        count = 0
        with open(wpconfig, 'r') as f:
            for line in f:
                if regex.search(line):
                    count += 1
        if count > 1 or count == 0:
            print('None or multiple WP_CACHE constant')
            return False
        if action == 'on':
            pat = "^\s*#+\s*define\s*\(\s*'WP_CACHE'.*$"
            repl = "define('WP_CACHE', true);"
            self.replace_in_file(pat, repl, wpconfig)
        if action == 'off':
            pat = "^\s*define\('WP_CACHE'.*$"
            repl = "#define('WP_CACHE', true);"
            self.replace_in_file(pat, repl, wpconfig)
        if action == 'clear':
            command = 'php %s/tools/bcache.clear.php %s' %(kusanagi_dir, uri)
            fLib.execute(command)
        return True
