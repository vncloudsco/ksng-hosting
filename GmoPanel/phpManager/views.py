from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from .forms import PhpForm,NginxHttpForm,NginxSslForm
from plogical.phpSetting import phpManager
from plogical import settingManager
import urllib.request
import re,subprocess,shutil,os
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


def php(request):
    """
    show php manager
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        php_current = phpManager.get_current_ver()
        form = PhpForm(initial={'php_version': php_current})
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'phpManager/index.html',{'page_title': 'PHP Manager','form': form,'php_current': php_current})

def changePhp(request):
    """
    change php version
    :param request:
    :return:
    """
    data_result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        if request.POST:
            form = PhpForm(request.POST)
            if form.is_valid():
                if phpManager.get_current_ver() == request.POST['php_version']:
                    data_result['msg'] = 'Please select another version different from the current version.'
                elif phpManager.switch_php(request.POST['php_version']):
                    data_result['status'] = 1
                    data_result['msg'] = 'Successfully'
                else:
                    data_result['msg'] = "Can not change version PHP!"
            else:
                data_result['msg'] = 'Value is incorrect!'
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        data_result['msg'] = str(e)

    return JsonResponse(data_result)

def restartPhp(request):
    """
    restart php version
    :param request:
    :return:
    """
    data_result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        php_current = phpManager.get_current_ver()
        if phpManager.restart_php(php_current):
            data_result['status'] = 1
            data_result['msg'] = 'Successfully'
        else:
            data_result['msg'] = "Can not restart version PHP!"

    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        data_result['msg'] = str(e)

    return JsonResponse(data_result)

def listDomain(request):
    """
    list domain config nginx
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        provisions = Provision.objects.filter(account_id=account.id,deactive_flg=0)

    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'phpManager/list_domain.html',{'page_title': 'Nginx Manager','data': provisions,'count': provisions.count()})

def nginx(request,domain = None):
    """
    show nginx detail domain
    :param request:
    :param domain:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        try:
            provision = Provision.objects.get(domain=domain, deactive_flg=0, account_id=account.id)
            # create file backup and temp
            NginxSetting = settingManager.SettingManager(provision.provision_name)
            if NginxSetting.before_edit_nginx(provision.domain):
                # read file temp
                fileSsl = open(settings.URL_NGINX_TEMP + provision.provision_name + '_ssl.conf', 'r')
                fileHttp = open(settings.URL_NGINX_TEMP + provision.provision_name + '_http.conf', 'r')
                textSsl = fileSsl.read()
                textHttp = fileHttp.read()
                fileSsl.close()
                fileHttp.close()
                form_http = NginxHttpForm(initial={'domain': provision.domain,'type': 'http','config_content': textHttp})
                form_ssl = NginxSslForm(initial={'domain': provision.domain,'type': 'ssl','config_content': textSsl})
            else:
                form_ssl = NginxSslForm()
                form_http = NginxHttpForm()
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/settings/listDomain')
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'phpManager/nginx.html',{'page_title': 'Nginx Manager','provision': provision,'form_http': form_http,'form_ssl': form_ssl})

def configNginx(request):
    """
    Config nginx
    :param request:
    :return:
    """
    result = {'status': 0 ,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        if request.POST:
            form = NginxSslForm(request.POST)
            if form.is_valid():
                provision = Provision.objects.get(domain=request.POST['domain'],deactive_flg=0,account_id=account.id)
                fileConfig = open(settings.URL_NGINX_TEMP+provision.provision_name+'_'+request.POST['type']+'.conf','w')
                fileConfig.write(request.POST['config_content'])
                fileConfig.close()
                NginxSetting = settingManager.SettingManager(provision.provision_name)
                if NginxSetting.edit_nginx(provision.domain):
                    result['status'] = 1
                    result['msg'] = "Config nginx domain <b>{}</b> success!".format(provision.domain)
                else:
                    result['msg'] = "Can not change nginx!Please try again!"
            else:
                result['msg'] = "Params is validate! Please check value"
                result['errors'] = form.errors
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        result['msg']= str(e)

    return JsonResponse(result)