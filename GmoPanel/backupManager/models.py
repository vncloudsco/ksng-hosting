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

    def __str__(self):
        return self.provision_name
