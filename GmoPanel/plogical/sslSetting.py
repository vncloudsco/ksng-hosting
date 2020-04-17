#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from plogical.settingManager import SettingManager as setMng
import plogical.functionLib as fLib


class SslMng:
    def __init__(self, provision=None):
        self.provision = provision
        self.fqdn = fLib.get_fqdn(self.provision)
        self.kusanagi_dir = '/home/kusanagi/%s' % self.provision
        self.app_id = fLib.get_app_id(self.provision)
        self.wpconfig = self.get_wpconf()

    def get_wpconf(self):
        wpconfig = None
        if self.app_id == "WordPress":
            if os.path.isfile('%s/wp-config.php' % self.kusanagi_dir):
                wpconfig = '%s/wp-config.php' % self.kusanagi_dir
            elif os.path.isfile('%s/DocumentRoot/wp-config.php' % self.kusanagi_dir):
                wpconfig = '%s/DocumentRoot/wp-config.php' % self.kusanagi_dir
            else:
                wpconfig = ''
        return wpconfig

    def wp_replace_proto(self, old_protocol=None, new_protocol=None, fqdn=None):
        if os.path.isfile(self.wpconfig):
            wp_cmd = 'sudo -u kusanagi -i -- /usr/local/bin/wp'
            document_root = '%s/DocumentRoot' % self.kusanagi_dir
            command = '%s option get home --path=%s | ' \
                      'grep %s >/dev/null 2>&1; echo $?' % (wp_cmd, document_root, old_protocol)
            res = fLib.execute(command)
            if int(res) == 0:
                command = '%s search-replace %s://%s %s://%s --path=%s --all-tables > /dev/null' \
                          % (wp_cmd, old_protocol, fqdn, new_protocol, fqdn, document_root)
                fLib.execute(command)

    def k_https(self, action=None):
        httpd_http = '/etc/httpd/conf.d/%s_http.conf' % self.provision
        nginx_http = '/etc/nginx/conf.d/%s_http.conf' % self.provision
        old_proto = None
        new_proto = None
        if action == 'redirect':
            print('Redirect all traffic on %s to HTTPS.(Permanently)' % self.fqdn)
            setMng.replace_in_file(r'(\s+)#\s*rewrite \^(.*)\$ https:', r'\1rewrite ^(.*)$ https:', nginx_http)
            setMng.replace_in_file(r'RewriteEngine Off', r'RewriteEngine On', httpd_http)
            if not setMng.check_existence_in_file('REDIRECT_SSL:', httpd_http):
                pat = r'RewriteEngine(\s*.*)'
                repl = r'RewriteEngine\1\n\t\tRewriteRule . - [E=REDIRECT_SSL:on]\n\t\tRewriteCond %{ENV:REDIRECT_SSL} ^on$'
                setMng.replace_in_file(pat, repl, httpd_http)
            setMng.replace_in_file(r'E=REDIRECT_SSL:off', r'E=REDIRECT_SSL:on', httpd_http)
            if os.path.isfile(self.wpconfig):
                setMng.replace_in_file(r"^[#\s]+define\('FORCE_SSL_ADMIN", r"define('FORCE_SSL_ADMIN", self.wpconfig)
            old_proto = 'http'
            new_proto = 'https'
        if action == 'noredirect':
            print('Disable redirect all traffic to HTTPS (Permanently')
            setMng.replace_in_file(r'^([^#]+\s*)rewrite \^(.*)\$ https:', r'\1#rewrite ^(.*)$ https:', nginx_http)
            setMng.replace_in_file(r'RewriteEngine Off', r'RewriteEngine On', httpd_http)
            if not setMng.check_existence_in_file('REDIRECT_SSL:', httpd_http):
                pat = r'RewriteEngine(\s*.*)'
                repl = r'RewriteEngine\1\n\t\tRewriteRule . - [E=REDIRECT_SSL:on]\n\t\tRewriteCond %{ENV:REDIRECT_SSL} ^on$'
                setMng.replace_in_file(pat, repl, httpd_http)
            setMng.replace_in_file(r'E=REDIRECT_SSL:on', r'E=REDIRECT_SSL:off', httpd_http)
            if os.path.isfile(self.wpconfig):
                setMng.replace_in_file(r"^define\('FORCE_SSL_ADMIN", r"#define('FORCE_SSL_ADMIN", httpd_http)
            old_proto = 'https'
            new_proto = 'http'
        self.wp_replace_proto(old_proto, new_proto, self.fqdn)

    def k_hsts(self, action=None):
        if action == 'off':
            pat = r'([^#]+)add_header Strict-Transport-Security[ \t]+(.*)'
            repl = r'\1#add_header Strict-Transport-Security \2'
            setMng.replace_in_file(pat, repl, '/etc/nginx/conf.d/%s_ssl.conf' % self.provision)
            pat = r'([^#]+)Header set Strict-Transport-Security[ \t]+(.*)'
            repl = r'\1#Header set Strict-Transport-Security \2'
            setMng.replace_in_file(pat, repl, '/etc/httpd/conf.d/%s_ssl.conf' % self.provision)
        if action == 'on':
            pat = r'#[ \t]*add_header Strict-Transport-Security[ \t]+(.*)'
            repl = r'add_header Strict-Transport-Security \1'
            setMng.replace_in_file(pat, repl, '/etc/nginx/conf.d/%s_ssl.conf' % self.provision)
            pat = r'#[ \t]*Header set Strict-Transport-Security[ \t]+(.*)'
            repl = r'Header set Strict-Transport-Security \1'
            setMng.replace_in_file(pat, repl, '/etc/httpd/conf.d/%s_ssl.conf' % self.provision)
            print('NOTICE: Recommend that you should submit your domain %s at https://hstspreload.org/' % self.fqdn)

    def enable_ssl(self, email=None):
        certbot = '/usr/local/certbot/certbot-auto'
        option = '-m %s --agree-tos' % email
        if email != "" and os.path.isfile(certbot):
            root_domain = fLib.is_root_domain(self.fqdn)
            if root_domain == 0:
                command = '%s certonly --text --noninteractive --webroot -w %s/DocumentRoot -d %s -d www.%s %s' \
                        % (certbot, self.kusanagi_dir, self.fqdn, self.fqdn, option)
                fLib.execute(command)
            elif root_domain == 1:
                apex = self.fqdn.split('www.')[1]
                command = '%s certonly --text --noninteractive --webroot -w %s/DocumentRoot -d %s -d %s %s' \
                          % (certbot, self.kusanagi_dir, self.fqdn, apex, option)
                fLib.execute(command)
            else:
                command = '%s certonly --text --noninteractive --webroot -w %s/DocumentRoot -d %s %s' \
                            % (certbot, self.kusanagi_dir, self.fqdn, option)
                fLib.execute(command)
            command = 'ls -1t /etc/letsencrypt/live/%s*/fullchain.pem 2> /dev/null | head -1' % self.fqdn
            full_chain_path = fLib.execute(command)
            full_chain_dir = full_chain_path.rsplit('/', 1)[0]
            if full_chain_path != "":
                fLib.execute('env RENEWD_LINAGE=%s /usr/bin/ct-submit.sh' % full_chain_dir)
            else:
                print('Can not get Lets Encrypt SSL certificate files.')
                return False
            pat = (r'^(\s*ssl_certificate\s+)\S+;', r'^(\s*ssl_certificate_key\s+)\S+;')
            repl = (r'\1%s/fullchain.pem;' % full_chain_dir, r'\1%s/privkey.pem;' % full_chain_dir)
            setMng.replace_multiple_in_file('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, pat, repl)
            pat = (r'^(\s*SSLCertificateFile\s+)\S+', r'^(\s*SSLCertificateKeyFile\s+)\S+')
            repl = (r'\1%s/fullchain.pem' % full_chain_dir, r'\1%s/privkey.pem' % full_chain_dir)
            setMng.replace_multiple_in_file('/etc/httpd/conf.d/%s_ssl.conf' % self.provision, pat, repl)

            self.wp_replace_proto('http', 'https', self.fqdn)

    @staticmethod
    def k_autorenewal(action=None):
        cron_file = '/var/spool/cron/root'
        exist = setMng.check_existence_in_file('/usr/bin/kusanagi update cert', cron_file)
        if action == 'on':
            if exist:
                print('Auto renew certificate already enabled. Nothing to do')
            else:
                has_auto = 0
                for root, dirs, files in os.walk('/etc/letsencrypt/live'):
                    for name in files:
                        if os.path.islink(os.path.join(root, name)) and re.search('fullchain.pem',
                                                                                  os.path.join(root, name)):
                            has_auto = 1
                            break
                    if has_auto == 1:
                        break
                if has_auto:
                    f = open(cron_file, 'a+')
                    f.write('07 03 * * 0 /usr/bin/kusanagi update cert')
                    f.close()
                else:
                    print('Auto renew certificate already enabled. Nothing to do')
        if action == 'off':
            if exist:
                f = open(cron_file, 'rt')
                g = open('/opt/tmp_nginx.conf', 'wt')
                for line in f:
                    if not re.search('/usr/bin/kusanagi update cert', line):
                        g.write(line)
                f.close()
                g.close()
                shutil.copy('/opt/tmp_nginx.conf', cron_file)
                os.remove('/opt/tmp_nginx.conf')

    def k_ssl(self, email=None, https=None, hsts=None):
        if email != "":
            self.enable_ssl(email)
            self.k_autorenewal('on')
        if hsts != "":
            self.k_hsts(hsts)
        if https != "":
            self.k_https(https)
        fLib.reload_service('httpd')
        if fLib.check_nginx_valid() == 0:
            fLib.reload_service('nginx')
            print('Done')
            # return True
        else:
            print('Nginx conf check failed.')
            # return False
