from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from plogical import website
from .forms import UploadForm
import json,socket,os,subprocess
import urllib.request
import re
from crontab import CronTab
from django.utils import timezone
from django.core import serializers
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

def modal(request,type='wordpress'):
    """
    ajax load modal
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        if type == 'database' or type == 'source':
            provisions = Provision.objects.filter(account_id=account.id, deactive_flg=0)
        else:
            provisions = Provision.objects.filter(account_id=account.id,deactive_flg=0,app_id__in=[1, 2])
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'uploadManager/modal.html',{'provisions': provisions,'type': type})

def database(request,domain=None):
    """
    template upload database
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(domain=domain,deactive_flg=0,account_id=account.id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/')

    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'uploadManager/database.html', {'provision': provision,'page_title': 'Database Upload'})

def source(request,domain=None):
    """
    template upload source code
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(domain=domain, deactive_flg=0, account_id=account.id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/')

    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'uploadManager/source.html', {'provision': provision,'page_title': 'Source Code Upload'})

def wordpress(request,domain=None):
    """
    template upload source code
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(domain=domain, deactive_flg=0, account_id=account.id,app_id__in=[1,2])
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/')

    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'uploadManager/wordpress.html', {'provision': provision,'page_title': 'Wordpress Upload'})

def uploadWordpress(request,pro_id=None):
    """
    upload source wordpress
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id,app_id__in=[1,2])
        except ObjectDoesNotExist:
            return JsonResponse({'status': 0, 'msg': 'Upload failed!Provision is not exist!'})
        path_upload = "/home/kusanagi/{}/Up".format(provision.provision_name)
        os.makedirs(path_upload, mode=0o777, exist_ok=True)
        if request.POST:
            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                f = upload_form.cleaned_data["file"]
                handle_uploaded_file(f,path_upload+'/'+f.name)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return JsonResponse({'status': 0, 'msg': 'Upload failed!'})

    return JsonResponse({'status': 1, 'msg': ''})

def uploadSource(request,pro_id=None):
    """
    upload Source Code
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 0, 'msg': 'Upload failed!Provision is not exist!'})
        path_upload = "/home/kusanagi/{}/Up".format(provision.provision_name)
        os.makedirs(path_upload, mode=0o777, exist_ok=True)
        if request.POST:
            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                f = upload_form.cleaned_data["file"]
                handle_uploaded_file(f,path_upload+'/'+f.name)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return JsonResponse({'status': 0, 'msg': 'Upload failed!'})

    return JsonResponse({'status': 1, 'msg': ''})

def uploadDatabase(request,pro_id=None):
    """
    upload Database
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 0, 'msg': 'Upload failed!Provision is not exist!'})
        path_upload = "/home/kusanagi/Up"
        os.makedirs(path_upload, mode=0o777, exist_ok=True)
        if request.POST:
            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                f = upload_form.cleaned_data["file"]
                handle_uploaded_file(f,path_upload+'/'+f.name)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return JsonResponse({'status': 0, 'msg': 'Upload failed!'})

    return JsonResponse({'status': 1, 'msg': ''})


def handle_uploaded_file(file,filename):
    """
    write file into path
    :param file: request file
    :param filename: path file
    :return:
    """
    with open(filename, 'ab') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def execute(request,pro_id=None):
    """
    execute source wordpress
    :param request:
    :param pro_id:
    :return:
    """
    data_result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id, app_id__in=[1, 2])
        except ObjectDoesNotExist:
            data_result['msg'] = 'Provision is not exist!'
            return JsonResponse(data_result)
        ws = website.Website(provision.provision_name,'kusanagi')
        data_result = ws.migration_wp()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        data_result['msg'] = str(e)
        return JsonResponse(data_result)

    return JsonResponse(data_result)

def executeSource(request,pro_id=None):
    """
    execute source Another PHP
    :param request:
    :param pro_id:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id)
        except ObjectDoesNotExist:
            data_result['msg'] = 'Provision is not exist!'
            return JsonResponse(data_result)
        ws = website.Website(provision.provision_name, 'kusanagi')
        data_result = ws.resource_up()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return JsonResponse(data_result)

    return JsonResponse(data_result)

def executeDatabase(request,pro_id=None):
    """
    execute database 
    :param request:
    :param pro_id:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        try:
            provision = Provision.objects.get(pk=pro_id, deactive_flg=0, account_id=account.id)
        except ObjectDoesNotExist:
            data_result['msg'] = 'Provision is not exist!'
            return JsonResponse(data_result)
        ws = website.Website(provision.provision_name, 'kusanagi')
        data_result = ws.mysqldb_up(provision.db_user,provision.db_password,provision.db_name)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        return JsonResponse(data_result)

    return JsonResponse(data_result)
