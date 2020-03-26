#!/usr/bin/python3

import sys
import os
import subprocess
import functionLib


def execute(command):
    try:
        res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return res.stdout
    except BaseException as error:
        return error


def execute_outputfile(command,file_name):
    try:
        fout =  open(file_name,"a+")
        res = subprocess.run(command, shell=True, check=True, stdout=fout, stderr=fout, universal_newlines=True)
        fout.close()
    except BaseException as error:
        print (' ---Error: ',error)
        #return error


class phpManager():

    @staticmethod
    def get_current_ver():
        for i in ('php', 'php53', 'php70', 'php71', 'php72', 'php73'):
            if functionLib.is_active(i+'-fpm') == 0:
                return i

    @staticmethod
    def switch_php(php_version):
        functionLib.enable_php(php_version)

