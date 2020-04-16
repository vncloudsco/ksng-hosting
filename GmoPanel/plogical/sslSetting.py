#!/usr/bin/env python3

import os
import subprocess
from plogical.settingManager import SettingManager as setMng
import plogical.functionLib as fLib


class SslMng:
    def __init__(self, provision=None):
        self.provision = provision
        self.fqdn = fLib.get_fqdn(self.provision)
        self.kusanagi_dir = '/home/kusanagi/%s' % self.provision
        self.app_id = setMng.get_app_id(self.provision)

    def wp_replace_proto(self, old_protocol=None, new_protocol=None, fqdn=None):
        wpconfig = ''
        if self.app_id == "WordPress":
            if os.path.isfile('%s/wp-config.php' % self.kusanagi_dir):
                wpconfig = '%s/wp-config.php' % self.kusanagi_dir
            elif os.path.isfile('%s/DocumentRoot/wp-config.php' % self.kusanagi_dir):
                wpconfig = '%s/DocumentRoot/wp-config.php' % self.kusanagi_dir
        if os.path.isfile(wpconfig):
            print('OK', self.app_id)

    def printappid(self):
        return self.app_id

