import os
import sys
import django
sys.path.append('/opt/scripts_py/GmoPanel')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GmoPanel.settings")
django.setup()
from backupManager.models import BackupLog


#insert = BackupLog(provision_id='22', status='0', backup_type='0')
#insert.save()
#insert.status = '1'
#insert.save()
all_record = BackupLog.objects.all()
one_record = BackupLog.objects.filter(status="1")
print(all_record)
print('---')
print(one_record)
