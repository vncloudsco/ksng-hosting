from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'securityManager'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('index',views.index,name='index'),
    path('authenGoogle',views.authenGoogle,name='authenGoogle'),
    path('getSecuriryCode',views.getSecuriryCode,name='getSecuriryCode'),
    path('action/<domain>',views.action,name='action'),
    path('changeStatus/<int:pro_id>',views.changeStatus,name='changeStatus'),
    path('listReba/<int:pro_id>',views.listReba,name='listReba'),
    path('saveReba/<int:pro_id>',views.saveReba,name='saveReba'),
    path('deleteReba/<int:waf_id>',views.deleteReba,name='deleteReba'),
    path('getChangePassword/<int:waf_id>',views.getChangePassword,name='getChangePassword'),
    path('changePassword/<int:waf_id>',views.changePassword,name='changePassword'),
    path('listRebi/<int:pro_id>',views.listRebi,name='listRebi'),
    path('saveRebi/<int:pro_id>',views.saveRebi,name='saveRebi'),
    path('deleteRebi/<int:waf_id>',views.deleteRebi,name='deleteRebi'),
    path('getChangeIp/<int:waf_id>',views.getChangeIp,name='getChangeIp'),
    path('changeIp/<int:waf_id>',views.changeIp,name='changeIp'),

]