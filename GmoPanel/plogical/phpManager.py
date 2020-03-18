#!/usr/bin/python3
import sys
import os
import argparse
import subprocess

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
        try:
            command = 'kusanagi which_php'
            execute(command)
        except BaseException as error:
            return error
    @staticmethod
    def switch_php(phpver):
        try:
            command = 'kusanagi '+phpver
            execute(command)
        except BaseException as error:
            return error


def main():

    tasks=phpManager()
    parse=argparse.ArgumentParser()
    parse.add_argument('-v', '--current_version', default='', action='store_true')
    parse.add_argument('-s', '--switch', default='')
    args=parse.parse_args()
    show_ver=args.current_version
    sw=args.switch
    if show_ver:
        tasks.get_current_ver()
    if args.switch:
        print(sw)
        tasks.switch_php(sw)
        

if __name__ == '__main__':
    main()

        
