#!/usr/bin/env python3
import argparse
import subprocess
import sys
from phpManager import execute

class WebsiteManager():
    @staticmethod
    def create_new_provision(argv):
        parse=argparse.ArgumentParser()
        parse.add_argument('-f', '--fqdn', required=True)
        parse.add_argument('-d', '--dbname', required=True)
        parse.add_argument('-u', '--dbuser', required=True)
        parse.add_argument('-p', '--dbpass', required=True)
        parse.add_argument('-t', '--prov', required=True)
        #parse.add_argument('-e', '--email', action='store_true', help="email [option]")
        parse.add_argument('-e', '--email', default='--noemail')
        parse.add_argument('-c', dest='cms', required=True)
        args=parse.parse_args()

        cmd='kusanagi provision --' + args.cms + ' --wplang en_US --fqdn ' + args.fqdn + ' ' + args.email + ' --dbname ' + args.dbname + ' --dbuser ' + args.dbuser + ' --dbpass ' + args.dbpass + ' ' + args.prov
        #print(cmd)
        execute(cmd)

WebsiteManager.create_new_provision(sys.argv[1:])
