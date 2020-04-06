from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from plogical import hashPassword,website
import json
from .forms import CreateWebsiteForm
import urllib.request
import websiteManager.define as define
import bcrypt
import re,socket
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import mysql.connector as MySQLdb

def createWebsite(request):
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        form = CreateWebsiteForm(initial={'app_id': 1,'account_id': userId,'email': account.email,'db_password': hashPassword.generate_pass(10)})
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/create_website.html', {'form': form, 'account': account, 'page_title': 'Create Website'})

def createProvision(request):
    """
    create provision website ajax action
    :param request:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        if request.method == 'POST':
            data = request.POST.copy()
            form = CreateWebsiteForm(data)
            if form.is_valid():
                pro = form.save(commit=False)
                proName = generateProvision(data['domain'])
                # call Shell create Account
                ws = website.Website(proName)
                result = ws.createWebsite(data)
                if result['status']:
                    pro.username = account.login_id
                    pro.provision_name = proName
                    pro.account_id = userId
                    pro.save()
                    data_result['status'] = 1
                else:
                    raise KeyError(result['msg'])
            else:
                data_result['errors'] = form.errors
                data_result['msg'] = 'Params is validate! Please check value'
    except KeyError as msg:
        data_result['msg'] = str(msg)+' Key Error!'

    return HttpResponse(json.dumps(data_result))

def index(request):
    """
    list website
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/index.html', {'page_title': 'Website Setting'})

def listDomain(request):
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId, deactive_flg=0)
        count = provisions.count()
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/list_website.html',{'provisions':provisions,'count':count})

def deleteProvision(request):
    """
    Delete Provision
    :param request:
    :return:
    """
    data_result = {'status':0,'msg':''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        if request.POST:
            pro = Provision.objects.get(pk=request.POST['id'],account_id=userId,deactive_flg=0)
            if not pro:
                data_result['msg'] = 'Provision is not exits!'
                return HttpResponse(json.dumps(data_result))
            ws = website.Website(pro.provision_name)
            result = ws.deleteWebsite()
            if result['status']:
                pro.delete()
                data_result['status'] = 1
                data_result['msg'] = 'Delete provision {} is success!'.format(pro.provision_name)
            else:
                data_result['msg'] = result['msg']
        else:
            return HttpResponseRedirect('/websites/')
    except KeyError:
        return HttpResponseRedirect('/login')

    return HttpResponse(json.dumps(data_result))

def cacheManager(request):
    """
    list website action cache
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId,deactive_flg=0)
        count = provisions.count()
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/list_website_cache.html',{'provisions': provisions, 'count': count, 'page_title': 'Cache Manager'})

def sslManager(request):
    """
    list website action ssl
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId,deactive_flg=0)
        count = provisions.count()
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/list_website_ssl.html',{'provisions': provisions, 'count': count, 'page_title': 'SSL Manager'})

def listTheme(request,pro_id=None):
    """
        list website action ssl
        :param request:
        :return:
        """
    try:
        userId = request.session['userID']
        pro = Provision.objects.get(account_id=userId, deactive_flg=0, app_id__in=[1,2], pk=pro_id)
        data = urllib.request.urlopen(settings.BASE_URL_WB+'theme.json').read()
        data = json.loads(data)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return HttpResponseRedirect('/websites/')

    return render(request, 'websiteManager/list_theme.html',
                  {'pro': pro,'data': data.values(),'base_theme_url': settings.BASE_URL_WB,'page_title': 'Website Builder'})

def modal(request):
    """
    ajax load modal
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId,deactive_flg=0,app_id__in=[1,2])
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/modal.html',{'provisions': provisions})

def activeTheme(request):
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        if request.POST:
            try:
                pro = Provision.objects.get(id=request.POST['id'], app_id__in=[1, 2], account_id=account.id, deactive_flg=0)
                ws = website.Website(pro.provision_name)
                result = ws.activeTheme({'domain': pro.domain,'theme_id': request.POST['theme_id'],'email': pro.email})
                if result['status']:
                    data_result['status'] = 1
                    data_result['msg'] = '<p>Your website has been created successfully.</p><p><strong><span><i class="fa fa-link"></i> Login url: <a href="'+result['data']['url']+'" target="_blank">'+result['data']['url']+'</a></span></strong></p><p><span><i class="fa fa-user"></i> Account: <strong>'+result['data']['user']+'</strong></span></p><p><span><i class="fa fa-lock"></i> Password: <strong>'+result['data']['password']+'</strong></span></p><p><span><i class="fa fa-lightbulb-o"></i> Please save this information and change current password for more sercurity.</span></p>'
                else:
                    raise ValueError(result['msg'])
            except BaseException as e:
                data_result['msg'] = str(e)
                return HttpResponse(json.dumps(data_result))
        else:
            return HttpResponseRedirect('/websites/')
    except KeyError:
        return HttpResponseRedirect('/login')

    return HttpResponse(json.dumps(data_result))


def fileManager(request):
    """
    ajax create link filemanager
    :param request:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        password = hashPassword.generate_pass(16)
        pass_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode('utf-8').replace('$2b','$2y')
        db = MySQLdb.connect(host=define.DB_HOST_RUN, user=define.DB_USERNAME_RUN, passwd=define.DB_PASS_RUN, database=define.DB_NAME_RUN)
        cursor = db.cursor()
        cursor.execute("UPDATE df_users SET password='{}', username='kusanagi', require_password_change = 0 WHERE id = 1".format(pass_hash))
        cursor.execute("UPDATE df_users_permissions SET homefolder='/home/kusanagi' WHERE uid = 1")
        db.commit()
        db.close()
        ip = socket.gethostbyname(socket.gethostname())
        return HttpResponseRedirect("http://{}/FileManager/?page=login&action=login&nonajax=1&username=kusanagi&password={}".format(ip, password))
    except KeyError:
        return HttpResponseRedirect('/login')
    except ConnectionError:
        data_result['msg'] = 'Can not connect MYSQL'

    return HttpResponse(json.dumps(data_result))

def generateProvision(domain=None):
    """
    generate random provision name
    :param domain:
    :return:
    """
    if len(domain) > 24:
        pass
        pro = hashPassword.generate_pass(4)+domain[:20]
        cnt = Provision.objects.filter(provision_name=pro,deactive_flg=0).count()
        while cnt:
            pro = hashPassword.generate_pass(4) + domain[:20]
            cnt = Provision.objects.filter(provision_name=pro, deactive_flg=0).count()

        return pro.lower()
    else:
        return domain.lower()

def listMysql(request):
    """
    list info mysql manager
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId, deactive_flg=0)
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/list_mysql.html', {'data': provisions,'count': len(provisions),'page_title': 'Mysql Manager','ipServer': settings.GOOGLEAUTH})

def emailServer(request):
    """
    EmailServer
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        provisions = Provision.objects.filter(account_id=userId, deactive_flg=0)
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'websiteManager/email_server.html', {'data': provisions,'count': len(provisions),'page_title': 'Mysql Manager','ipServer': settings.GOOGLEAUTH})
