from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'websiteManager'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('createWebsite/',views.createWebsite,name='createWebsite'),
    path('createProvision/',views.createProvision,name='createProvision'),
    path('',views.index,name='index'),
    path('listDomain/',views.listDomain,name='listDomain'),
    path('deleteProvision/',views.deleteProvision,name='deleteProvision'),
    path('cacheManager/',views.cacheManager,name='cacheManager'),
    path('sslManager/',views.sslManager,name='sslManager'),
    path('modal/',views.modal,name='modal'),
    path('websiteBuilder/<int:pro_id>',views.listTheme,name='websiteBuilder'),
    path('activeTheme/',views.activeTheme,name='activeTheme'),
    path('fileManager/',views.fileManager,name='fileManager'),
    path('listMysql/',views.listMysql,name='listMysql'),
    path('emailServer/',views.emailServer,name='emailServer'),
]