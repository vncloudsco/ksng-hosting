from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'backupManager'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('',views.index,name='index'),
    path('action/<int:pro_id>',views.action,name='action'),
    path('logs',views.logs,name='logs'),
    path('log/<pro_id>',views.log,name='log'),
    path('config',views.config,name='config'),
    path('getTokenGoogle',views.getTokenGoogle,name='getTokenGoogle'),
    path('cronJob',views.cronJob,name='cronJob'),
    path('addCron',views.addCron,name='addCron'),
    path('editCron/<int:cron_id>',views.editCron,name='editCron'),
    path('deleteCron/<int:cron_id>',views.deleteCron,name='deleteCron'),
    path('addRetention',views.addRetention,name='addRetention'),
    path('deleteRetention',views.deleteRetention,name='deleteRetention'),

]