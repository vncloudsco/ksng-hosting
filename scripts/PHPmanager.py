#!/usr/bin/python3
import sys
import os
import subprocess

libdir = '/usr/lib/kusanagi/lib'

def execute(command):
    try:
        res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output=res.stdout
        print(output)
    except:
        pass

class PHPmng():

    @staticmethod
    def get_current_ver():
        try:
            command = 'kusanagi which_php'
            execute(command)
        except:
            pass

#PHPmng.get_current_ver()
        
