from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from .forms import BackupForm,AccessForm
from .models import BackupLog
from plogical import hashPassword,website,backupManager
import json,socket,os,subprocess
import urllib.request
import re
from django.utils import timezone
from django.core import serializers
from django.conf import settings
from django.db import transaction

def index(request):
    """
    list website backup
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        pros = Provision.objects.filter(account_id=account.id,deactive_flg=0)
        form = BackupForm()
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'backupManager/index.html', {'data': pros, 'account': account,'count': pros.count(),'form': form , 'page_title': 'BackUp Manager'})

def action(request,pro_id=None):
    """
    process backup
    :param requrest:
    :param pro_id:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    listType = {
        0 : 'Localhost',
        1 : 'Remote SSH',
        2 : 'Google Drive'
    }
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        pro = Provision.objects.filter(pk=pro_id,account_id=account.id,deactive_flg=0).first()
        if pro is None:
            data_result['msg'] = 'Provision is not exits!'
            return HttpResponse(json.dumps(data_result))
        if request.POST:
            try:
                transaction.set_autocommit(False)
                data = request.POST.copy()
                form = BackupForm(data)
                if form.is_valid():
                    logBackup = BackupLog.objects.filter(provision_id=pro_id,backup_type=int(data['type']),status=0).order_by('-id').first()
                    if logBackup is not None:
                        data_result['msg'] = 'Website Backup is process... !You can not Backup type '+listType[int(data['type'])]+' with website '+pro.domain
                        return HttpResponse(json.dumps(data_result))
                    bk = backupManager.backupManager(pro.provision_name)
                    BackupLog(
                        provision_id= pro_id,
                        status= 0,
                        backup_type= int(data['type'])
                    ).save()
                    if int(data['type']) == 0:
                        # backup localhost
                        data_result = bk.local_backup()
                    elif int(data['type']) == 1:
                        # backup remote
                        data_result = bk.remote_backup(data['user'],data['host'],data['port'],data['password'],data['path'])
                    else:
                        #backup drive
                        data_result = bk.drive_backup(data['path_drive'])

                    if not data_result['status']:
                        raise ValueError(data_result['msg'])

                else:
                    data_result['errors'] = form.errors
                    data_result['msg'] = 'Params is validate! Please check value'
                transaction.commit()
            except BaseException as e:
                data_result['msg'] = str(e)
                transaction.rollback()
        else:
            return HttpResponseRedirect('/backups/')

    except KeyError:
        return HttpResponseRedirect('/login')

    return HttpResponse(json.dumps(data_result))

def logs(request):
    """
    manager list backup logs provision
    :param request:
    :param pro_id:
    :return:
    """
    try:
        flgLog = False
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        data = Provision.objects.filter(account_id=account.id,deactive_flg=0)
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'backupManager/logs.html',
                  {'data': data, 'account': account, 'count': data.count(),'flgLog': False,'page_title': 'BackUp Manager'})

def log(request,pro_id=None):
    """
    detail logs backup provision
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        pro = Provision.objects.filter(account_id=account.id, deactive_flg=0,pk=pro_id)
        if pro:
            data = BackupLog.objects.filter(provision_id=pro_id)
        else:
            return HttpResponseRedirect('/backups/logs')
    except KeyError:
        return HttpResponseRedirect('/login')
    return render(request, 'backupManager/logs.html',
                  {'data': data, 'account': account, 'count': data.count(), 'flgLog': True,
                   'page_title': 'BackUp Manager'})

def config(request):
    """
    config access google Drive
    :param request:
    :return:
    """
    flgConfig = os.path.isfile('/root/.config/rclone/rclone.conf')
    message = False
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        if request.POST:
            form = AccessForm(request.POST)
            if form.is_valid():
                cmd = '/usr/src/drive_connect_config {}'.format(request.POST['token'])
                res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                if not re.findall('Failed',res.stdout):
                    message = 'Access Google Drive success'
                else:
                    form.add_error('token','Token Access is not correct!')
        else:
            form = AccessForm()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        form.add_error('token', 'Token Access is not correct!')
    return render(request, 'backupManager/config.html',{'page_title': 'Backup Config','form': form,'flgConfig': flgConfig,'message': message})

def getTokenGoogle(request):
    """
    get authen google drive
    :param request:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        res = subprocess.run('/usr/src/drive_get_authen_link', shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
        res = str(res.stdout).replace('\n','')
        if res == 'Done':
            f = open(settings.PATH_LOG_AUTHEN_GG, 'r')
            dataText = f.read()
            url = dataText.split('link: ')[1].split('Log in')[0]
            return HttpResponseRedirect(url)
        else:
            raise ValueError('Can not get url Authenticate Google Drive!')
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        data_result['msg'] = str(e)
    return JsonResponse(data_result)

def cronJob(request):
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)

    except KeyError:
        return HttpResponseRedirect('/login')
    return render(request, 'backupManager/cron_job.html', {'page_title': 'Backup Config'})
