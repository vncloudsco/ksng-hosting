from django.db import models
from websiteManager.models import Provision
from django.utils import timezone

class BackupLog(models.Model):
    provision = models.ForeignKey(Provision, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0)
    backup_type = models.SmallIntegerField(default=0)
    message = models.TextField(default='None')
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='logs'

class CronJob(models.Model):
    backup_schedu = models.CharField(max_length=255,default=None)
    backup_day = models.CharField(max_length=255,default=None)
    backup_week = models.SmallIntegerField(default=0)
    backup_day_retention = models.IntegerField(default=0)
    backup_week_retention = models.IntegerField(default=0)
    backup_type = models.SmallIntegerField(default=0)
    host = models.CharField(max_length=255,default=None)
    port = models.IntegerField(default=0)
    user = models.CharField(max_length=255,default=None)
    password = models.CharField(max_length=255,default=None)
    path = models.TextField(default=None)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='cron_job'

    def __str__(self):
        return self.id
