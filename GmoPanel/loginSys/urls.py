from django.urls import path
from . import views
# SET THE NAMESPACE!
app_name = 'loginSys'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('',views.index,name='index'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('load_chart/',views.load_chart,name='load_chart'),
]