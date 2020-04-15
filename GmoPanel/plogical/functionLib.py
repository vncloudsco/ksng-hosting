#!/usr/bin/env python3

import os
import subprocess
import re


def execute(command):
    try:
        res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return res.stdout
    except subprocess.CalledProcessError as error:
        return error


def execute_outputfile(command, file_name):
    try:
        fout = open(file_name, "a+")
        res = subprocess.run(command, shell=True, check=True, stdout=fout, stderr=fout, universal_newlines=True)
        fout.close()
    except FileNotFoundError as error:
        print(' ---Error: ', error)


def is_enabled(service):
    command = 'systemctl is-enabled ' + service + ' 2> /dev/null | grep ^enabled > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


def is_active(service):
    command = 'systemctl is-active ' + service + ' 2> /dev/null | grep ^active > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


def restart_service(service):
    command = 'systemctl restart %s' % service
    execute(command)


def reload_service(service):
    command = 'systemctl reload %s' % service
    execute(command)


def stop_and_disable_service(service):
    command = 'systemctl stop %s && systemctl disable %s' % (service, service)
    execute(command)


def restart_and_enable_service(service):
    command = 'systemctl restart %s && systemctl enable %s' % (service, service)
    execute(command)


def change_php_bin(change=None):
    if os.path.islink('/usr/local/bin/php'):
        os.unlink('/usr/local/bin/php')
    else:
        change = 1

    for i in ('php73', 'php72', 'php71', 'php70', 'php53'):
        if is_active(i+'-fpm') == 0:
            os.symlink('/usr/local/%s/bin/php' % i, '/usr/local/bin/php')
    if is_active('php-fpm') == 0:
        os.symlink('/bin/php', '/usr/local/bin/php')

    if change:
        execute('hash -r')
        print('Issued "hash -r"')


def enable_php(php_version):
    change = 0
    if is_enabled('hhvm') == 0:
        stop_and_disable_service('hhvm')
        change = 1
    for i in ('php73', 'php72', 'php71', 'php70', 'php', 'php53'):
        if (is_enabled(i+'-fpm') == 0) and (i != php_version):
            stop_and_disable_service(i+'-fpm')
            change = 1

    restart_and_enable_service(php_version+'-fpm')
    change_php_bin(change)


def enable_hhvm():
    change = 0
    for i in ('php73', 'php72', 'php71', 'php70', 'php', 'php53'):
        if is_enabled(i+'-fpm') == 0:
            stop_and_disable_service(i+'-fpm')
            change = 1

    restart_and_enable_service('hhvm')
    change_php_bin(change)


def verify_prov_existed(profile):
    profile_config = "/etc/kusanagi.d/profile.conf"
    string = "\["+profile+"\]"
    regex = re.compile(string)
    with open(profile_config) as fp: lines = fp.read().splitlines()
    for line in lines:
        if regex.match(line):
            return True
    print('No such provision in the profile conf')
    return False


def verify_nginx_prov_existed(profile):
    http_file = os.path.isfile('/etc/nginx/conf.d/%s_http.conf' % profile)
    ssl_file = os.path.isfile('/etc/nginx/conf.d/%s_ssl.conf' % profile)
    if http_file and ssl_file:
        return True
    else:
        print("nginx configuration files don't exist")
        return False


def check_nginx_valid():
    command = 'nginx -t > /dev/null 2>&1;echo $?'
    res = execute(command)
    return int(res)


def get_fqdn(profile):
    fqdn = None
    with open('/etc/nginx/conf.d/%s_http.conf' % profile, 'r') as fp: lines = fp.read().splitlines()
    for line in lines:
        grep = re.findall(r'server_name', line)
        if grep:
            fqdn = line.split()[1]
            break
    return fqdn


def yum_install(package):
    command = 'rpm -q %s > /dev/null 2>&1; echo $?' % package
    res = execute(command)
    if int(res) == 0:
        return 0
    else:
        yum = execute('yum install -y %s > /dev/null 2>&1; echo $? ' % package)
        return yum.stdout



