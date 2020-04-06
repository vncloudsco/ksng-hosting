from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'uploadManager'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('modal/<type>',views.modal,name='modal'),
    path('database/<domain>',views.database,name='database'),
    path('wordpress/<domain>',views.wordpress,name='wordpress'),
    path('source/<domain>',views.source,name='source'),
    path('uploadWordpress/<int:pro_id>',views.uploadWordpress,name='uploadWordpress'),
    path('uploadSource/<int:pro_id>',views.uploadSource,name='uploadSource'),
    path('uploadDatabase/<int:pro_id>',views.uploadDatabase,name='uploadDatabase'),
    path('execute/<int:pro_id>',views.execute,name='execute'),
    path('executeSource/<int:pro_id>',views.executeSource,name='executeSource'),
    path('executeDatabase/<int:pro_id>',views.executeDatabase,name='executeDatabase'),
]