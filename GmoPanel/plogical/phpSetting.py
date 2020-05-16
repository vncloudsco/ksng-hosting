#!/usr/bin/python3

import subprocess
import plogical.functionLib as fLib
import django


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
    except subprocess.CalledProcessError as error:
        print(' ---Error: ', error)
        # return error


class phpManager():

    @staticmethod
    def get_current_ver():
        for i in ('php', 'php53', 'php70', 'php71', 'php72', 'php73', 'php74'):
            if fLib.is_active(i+'-fpm') == 0:
                return i

    @staticmethod
    def switch_php(php_version):
        fLib.enable_php(php_version)
        if fLib.is_active(php_version+'-fpm') == 0:
            return True
        else:
            return False

    @staticmethod
    def restart_php(php_version):
        if fLib.is_enabled(php_version+'-fpm') == 0:
            fLib.restart_service(php_version+'-fpm')
        if fLib.is_active(php_version+'-fpm') == 0:
            return True
        else:
            return False

