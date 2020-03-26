#!/usr/bin/env python3

import phpManager
from phpManager import execute


def is_enabled(service):
    command = 'systemctl is-enabled ' + service + ' 2> /dev/null | grep ^enabled > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


def is_active(service):
    command = 'systemctl is-active ' + service + ' 2> /dev/null | grep ^active > /dev/null ; echo $?'
    res = execute(command)
    return int(res)


def stop_and_disable_service(service):
    command = 'systemctl stop %s && systemctl disable %s' % service
    execute(command)


def restart_and_enable_service(service):
    command = 'systemctl restart %s && systemctl enable %s' % service
    execute(command)


def enable_php(php_version):
    change = 0
    if is_enabled('hhvm') == 0:
        stop_and_disable_service('hhvm')
        change = 1
    for i in ('php73', 'php72', 'php71', 'php70', 'php', 'php53'):
        if (is_enabled(i+'-fpm') == 0) and (i != php_version):
            stop_and_disable_service(i+'-fpm')

    restart_and_enable_service(php_version+'-fpm')

