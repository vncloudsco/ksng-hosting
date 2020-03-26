#!/usr/bin/env python3

import os
import subprocess

def execute(command):
    try:
        res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return res.stdout
    except BaseException as error:
        return error


def is_enabled(service):
    command = 'systemctl is-enabled ' + service + ' 2> /dev/null | grep ^enabled > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


def is_active(service):
    command = 'systemctl is-active ' + service + ' 2> /dev/null | grep ^active > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


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


