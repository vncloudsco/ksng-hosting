#!/usr/bin/python3
import sys
import os
import argparse
import subprocess

libdir = '/usr/lib/kusanagi/lib'

def execute(command):
    try:
        res = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output=res.stdout
        print(output)
    except BaseException as error:
        return error

class PHPmng():

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
            command = 'kusanagi phpver'
            execute(command)
        except BaseException as error:
            return error


def main():
    show=PHPmng()
    parse=argparse.ArgumentParser()
    parse.add_argument('-v', '--current-version', action='store_true')
    args=parse.parse_args()
    show_ver=args.current-version
    if show_ver:
        show.get_current_ver()
if __name__ == '__main__':
    main()

        
