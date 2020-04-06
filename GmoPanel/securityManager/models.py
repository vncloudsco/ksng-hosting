from django.db import models
from websiteManager.models import Provision
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Waf(models.Model):
    provision = models.ForeignKey(Provision, on_delete=models.CASCADE)
    url = models.CharField(max_length=255,default=None)
    type = models.SmallIntegerField(default=0)
    user = models.CharField(max_length=255,default=None,null=True)
    password = models.CharField(max_length=255,default=None,null=True)
    ip = models.CharField(max_length=255,default=None,null=True)
    serial = models.IntegerField(default=None,null=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='wafs'

