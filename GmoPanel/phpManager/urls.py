from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'phpManager'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('php',views.php,name='php'),
    path('changePhp',views.changePhp,name='changePhp'),
    path('restartPhp',views.restartPhp,name='restartPhp'),
    path('listDomain',views.listDomain,name='listDomain'),
    path('nginx/<domain>',views.nginx,name='nginx'),
    path('configNginx',views.configNginx,name='configNginx'),

]