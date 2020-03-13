#!/usr/bin/env python3

import argparse
import os
import sys, shutil
from shutil import make_archive
import pathlib
from phpManager import execute, execute_outputfile
from datetime import date, datetime
import re
import pymysql
import tarfile
from backupManager import backupManager
import backupManager
class backupAll():

    pwrd = backupManager.get_root_pass()
    def list_provision(self):
        db = pymysql.connect("localhost", "root", self.pwrd, "secure_vps")
        cursor = db.cursor()
        cursor.execute("select provision_name from provision")
        data = cursor.fetchall
        db.close()
        return  data





