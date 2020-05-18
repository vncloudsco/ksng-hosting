#!/usr/bin/env python3

import os
import re
import shutil
from datetime import datetime
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
                setMng.replace_in_file(r"^define\('FORCE_SSL_ADMIN", r"#define('FORCE_SSL_ADMIN", self.wpconfig)
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
                        if os.path.islink(os.path.join(root, name)) and re.search(r'fullchain\.pem',
                                                                                  os.path.join(root, name)):
                            has_auto = 1
                            break
                    if has_auto == 1:
                        break
                if has_auto:
                    f = open(cron_file, 'a+')
                    f.write('07 03 * * 0 /usr/bin/kusanagi update cert \n')
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

    def k_cert_change(self, cert_file_path=None, key_file_path=None):
        ssl_dir = '/etc/kusanagi.d/ssl/%s' % self.provision
        if cert_file_path and key_file_path:
            if not os.path.isdir(ssl_dir):
                os.mkdir(ssl_dir, mode=0o755)
            date_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            cert_file_name = cert_file_path.rsplit('/', 1)[1]
            target_cert = '%s/%s' % (ssl_dir, cert_file_name)
            if os.path.isfile(target_cert):
                shutil.move(target_cert, '%s.%s' % (target_cert, date_str))
            shutil.copy(cert_file_path, target_cert)

            key_file_name = key_file_path.rsplit('/', 1)[1]
            target_key = '%s/%s' % (ssl_dir, key_file_name)
            if os.path.isfile(target_key):
                shutil.move(target_key, '%s.%s' % (target_key, date_str))
            shutil.copy(key_file_path, target_key)

            pat = (r'^(\s*ssl_certificate\s+)\S+;', r'^(\s*ssl_certificate_key\s+)\S+;')
            repl = (r'\1%s;' % target_cert, r'\1%s;' % target_key)
            setMng.replace_multiple_in_file('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, pat, repl)
            pat = (r'^(\s*SSLCertificateFile\s+)\S+', r'^(\s*SSLCertificateKeyFile\s+)\S+')
            repl = (r'\1%s' % target_cert, r'\1%s' % target_key)
            setMng.replace_multiple_in_file('/etc/httpd/conf.d/%s_ssl.conf' % self.provision, pat, repl)

            print("Change SSL Certificate configuration.")
            self.wp_replace_proto('http', 'https', self.fqdn)

            fLib.reload_service('httpd')
            if fLib.check_nginx_valid() == 0:
                fLib.reload_service('nginx')
                print('Done')
                return True
            else:
                print('Nginx conf check failed.')
                return False

    def k_ssl(self, email=None, https=None, hsts=None):
        if email:
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
            return True
        else:
            print('Nginx conf check failed.')
            return False

    @staticmethod
    def diff_date(cert_file=None):
        date_array = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                      'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        res = fLib.execute('openssl x509 -in %s -enddate -noout' % cert_file)
        month = res.split('=')[1].split(' ')[0]
        month = date_array[month]
        tmp = res.split('=')[1].split(' ')[1]+'/'+res.split('=')[1].split(' ')[3]
        expire_date = '%s/%s' % (month, tmp)
        expire_date = fLib.execute('date -d "{}" +%s'.format(expire_date))
        now = fLib.execute('date +%s')
        m = (int(expire_date) - int(now)) / 86400
        if 0 < int(m):
            # print('The certificate will expire in %s day(s)' % int(m))
            life_time = 'The certificate will expire in %s day(s)' % int(m)
        else:
            # print('The certificate has EXPIRED')
            life_time = 'The certificate has EXPIRED'
        return life_time

    def ssl_status(self):
        has_installed = 0
        with open('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, 'rt') as f:
            for line in f:
                if re.search(r'^\s*ssl_certificate\s+', line) and not re.search(r'localhost\.', line):
                    cert_file = line.split('ssl_certificate')[1].split(';')[0].strip()
                    has_installed = 1
                    break
        if has_installed:
            if os.path.isfile(cert_file):
                # print(fLib.execute('openssl x509 -in %s -subject -issuer -dates -noout' % cert_file))
                # self.diff_date(cert_file)
                ssl_info = fLib.execute('openssl x509 -in %s -subject -issuer -dates -noout' % cert_file)
                return {'general_info': ssl_info, 'expiration_date': self.diff_date(cert_file)}
            else:
                print('Nginx conf: cert file doesn\'t exist')
                return False
        else:
            print('Not installed SSL')
            return False

    def remove_ssl(self):
        has_installed = 0
        with open('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, 'rt') as f:
            for line in f:
                if re.search(r'^\s*ssl_certificate\s+', line) and not re.search(r'localhost\.', line):
                    # cert_file = line.split('ssl_certificate')[1].split(';')[0].strip()
                    has_installed = 1
                # if re.search(r'^\s*ssl_certificate_key\s+', line) and not re.search(r'localhost\.', line):
                #    key_file = line.split('ssl_certificate_key')[1].split(';')[0].strip()
                    break
        if has_installed:
            if not os.path.isdir('/etc/kusanagi.d/ssl/recycle_bin'):
                os.mkdir('/etc/kusanagi.d/ssl/recycle_bin', mode=0o755)
            self.k_https('noredirect')
            pat = (r'^(\s*ssl_certificate\s+)\S+;', r'^(\s*ssl_certificate_key\s+)\S+;')
            repl = (r'\1/etc/pki/tls/certs/localhost.crt;', r'\1/etc/pki/tls/private/localhost.key;')
            setMng.replace_multiple_in_file('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, pat, repl)
            pat = (r'^(\s*SSLCertificateFile\s+)\S+', r'^(\s*SSLCertificateKeyFile\s+)\S+')
            repl = (r'\1/etc/pki/tls/certs/localhost.crt;', r'\1/etc/pki/tls/private/localhost.key;')
            setMng.replace_multiple_in_file('/etc/httpd/conf.d/%s_ssl.conf' % self.provision, pat, repl)
            if os.path.isfile('/etc/letsencrypt/renewal/%s.conf' % self.fqdn):
                shutil.move('/etc/letsencrypt/renewal/%s.conf' % self.fqdn, '/etc/kusanagi.d/ssl/recycle_bin/%s.conf' % self.fqdn)
            for root, dirs, files in os.walk('/etc/letsencrypt/renewal'):
                for name in files:
                    if re.search(r'%s-\d+' % self.fqdn, os.path.join(root, name)):
                        renewal_file = os.path.join(root, name)
                        dest_file = '/etc/kusanagi.d/ssl/recycle_bin/%s' % name
                        shutil.move(renewal_file, dest_file)
            # shutil.move(cert_file, '/etc/kusanagi.d/ssl/recycle_bin/')
            # shutil.move(key_file, '/etc/kusanagi.d/ssl/recycle_bin/')
            fLib.reload_service('httpd')
            if fLib.check_nginx_valid() == 0:
                fLib.reload_service('nginx')
                print('Done')
                return True
            else:
                print('Nginx conf check failed.')
                return False
        else:
            print('Not installed SSL. Nothing to do')
            return True

    def k_view_cert(self):
        has_installed = 0
        cert_file = '/etc/pki/tls/certs/localhost.crt'
        key_file = '/etc/pki/tls/private/localhost.key'
        with open('/etc/nginx/conf.d/%s_ssl.conf' % self.provision, 'rt') as f:
            for line in f:
                if re.search(r'^\s*ssl_certificate\s+', line) and not re.search(r'localhost\.', line):
                    cert_file = line.split('ssl_certificate')[1].split(';')[0].strip()
                    has_installed = 1
                if re.search(r'^\s*ssl_certificate_key\s+', line) and not re.search(r'localhost\.', line):
                    key_file = line.split('ssl_certificate_key')[1].split(';')[0].strip()
                    # break
        if has_installed:
            return True
        else:
            return False
