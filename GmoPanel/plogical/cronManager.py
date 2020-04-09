#!/usr/bin/env python3

from crontab import CronTab
import django


class CronManager:
    def __init__(self, command=None, comment=None):
        self.command = command
        self.comment = comment
        self.cron = CronTab(user='root')
        self.job = self.cron.new(command=self.command, comment='%s' % self.comment)
        self.job.minute.on(0)
        self.job.hour.on(23)

    def daily(self, dow):
        self.job.dow.on(*dow)
        self.cron.write()

    def weekly(self, dow):
        self.job.dow.on(dow)
        self.cron.write()
        
    def monthly(self):
        self.job.dom.on(1)
        self.cron.write()

    @staticmethod
    def delete_cron(comment):
        cron = CronTab(user='root')
        cron.remove_all(comment='%s' % comment)
        cron.write()
