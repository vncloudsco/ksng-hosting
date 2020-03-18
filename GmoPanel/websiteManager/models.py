from django.db import models
from loginSys.models import Account
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Provision(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    domain = models.CharField(max_length=200,default='None')
    ip = models.CharField(max_length=20,default='None')
    username = models.CharField(max_length=20,default='None')
    provision_name = models.CharField(max_length=24,default='None')
    app_id = models.SmallIntegerField(default=0)
    db_name = models.CharField(max_length=50)
    db_user = models.CharField(max_length=50)
    db_password = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    status = models.SmallIntegerField(default=1)
    deactive_flg = models.SmallIntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='prosivions'

    def __str__(self):
        return self.provision_name