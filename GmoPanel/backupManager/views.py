from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from .forms import BackupForm,AccessForm,CronJobForm,RetentionForm
from .models import BackupLog,CronJob
from plogical import hashPassword,website,backupSetting
import json,socket,os,subprocess
import urllib.request
import re
from crontab import CronTab
from django.utils import timezone
from django.core import serializers
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


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
        bk = backupSetting.BackupManager('ahihi.com')
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
                    BackupLog(
                        provision_id= pro_id,
                        status= 0,
                        backup_type= int(data['type'])
                    ).save()
                    bk = backupSetting.BackupManager(pro.provision_name)
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
    """
    Show list Cron and Retention
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        jobs = CronJob.objects.all()
        form = None
        forms = []
        shedu = []
        daily_retention = None
        weekly_retention = None
        monthly_retention = None
        cron_reten = CronTab(user=True).find_comment(re.compile('backup_((daily)|(weekly)|(monthly))_retention'))
        for job in cron_reten:
            if job.comment == 'backup_daily_retention':
                daily_retention = job.command.split(' ')[-1]
                shedu.append('daily')
            elif job.comment == 'backup_weekly_retention':
                weekly_retention = job.command.split(' ')[-1]
                shedu.append('weekly')
            elif job.comment == 'backup_monthly_retention':
                monthly_retention = job.command.split(' ')[-1]
                shedu.append('monthly')
        form_retention = RetentionForm(
            initial={
                'backup_daily_retention': daily_retention,
                'backup_weekly_retention': weekly_retention,
                'backup_monthly_retention': monthly_retention,
                'backup_schedu': shedu
            }
        )

        if jobs:
            for job in jobs:
                form = CronJobForm(initial={
                    'id': job.id,
                    'backup_schedu': str(job.backup_schedu).split(','),
                    'backup_day': str(job.backup_day).split(','),
                    'backup_week': job.backup_week,
                    'backup_type': job.backup_type,
                    'host': job.host,
                    'port': job.port,
                    'user': job.user,
                    'password': job.password,
                    'path': job.path,

                })
                forms.append(form)
        else:
            form = CronJobForm()
    except KeyError:
        return HttpResponseRedirect('/login')
    return render(request, 'backupManager/cron_job.html', {'page_title': 'Backup Manager','jobs': jobs,'form': form,'forms': forms,'form_retention': form_retention})

def addCron(request):
    """
    add cron tab
    :param request:
    :return:
    """
    data_result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        if request.POST:
            try:
                transaction.set_autocommit(False)
                data = request.POST.copy()
                form = CronJobForm(data)
                if form.is_valid():
                    data['backup_schedu'] = ','.join(data.getlist('backup_schedu'))
                    if data.getlist('backup_day'):
                        data['backup_day'] = ','.join(data.getlist('backup_day'))
                    else:
                        data['backup_day'] = 0
                    try:
                        week_cron = data['backup_week']
                    except KeyError:
                        week_cron = 0
                    # save record cronjob
                    crontab = CronJob(
                        backup_schedu=data['backup_schedu'],
                        backup_day=data['backup_day'],
                        backup_week=week_cron,
                        backup_type=data['backup_type'],
                    )
                    crontab.save()
                    if int(data['backup_type']) == 1:
                        # check connect ssh
                        cmd = 'sshpass -p {} ssh -o StrictHostKeyChecking=no -p {} -q {}@{} exit;echo $?'.format(data['password'],data['port'],data['user'],data['host'])
                        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
                        if str(res.stdout).replace('\n','') != '0':
                            raise ValueError('Remote connection failed')

                        crontab.host = data['host']
                        crontab.port = data['port']
                        crontab.user = data['user']
                        crontab.password = data['password']
                        crontab.path = data['path']
                        crontab.save()
                        pass
                    elif int(data['backup_type']) == 2:
                        # backup google drive
                        if not os.path.isfile('/root/.config/rclone/rclone.conf'):
                            raise ValueError('You can config access Google Drive!')
                        pass
                    else:
                        # backup localhost
                        pass
                else:
                    data_result['errors'] = form.errors
                    raise ValueError('Params is validate! Please check value')

                data_result['status'] = 1
                data_result['msg'] = 'Add Crontab Successfully!'
                data_result['data'] = {'id': crontab.pk}
                transaction.commit()
            except BaseException as e:
                transaction.rollback()
                data_result['msg'] = str(e)
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(data_result)

def editCron(request,cron_id=None):
    """
    edit cron tab
    :param request:
    :return:
    """
    data_result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        crontab = CronJob.objects.filter(pk=cron_id).first()
        if crontab is None:
            data_result['msg'] = 'CronJob js not exist!'
            return JsonResponse(data_result)
        if request.POST:
            try:
                transaction.set_autocommit(False)
                data = request.POST.copy()
                form = CronJobForm(data)
                if form.is_valid():
                    crontab = CronJob.objects.get(pk=cron_id)
                    crontab.delete()
                    jobs = CronTab().find_comment(cron_id)
                    for job in jobs:
                        jobs.remove(job)
                        jobs.write()

                    data['backup_schedu'] = ','.join(data.getlist('backup_schedu'))
                    if data.getlist('backup_day'):
                        data['backup_day'] = ','.join(data.getlist('backup_day'))
                    else:
                        data['backup_day'] = 0
                    try:
                        week_cron = data['backup_week']
                    except KeyError:
                        week_cron = 0
                    # save record cronjob
                    crontab = CronJob(
                        backup_schedu=data['backup_schedu'],
                        backup_day=data['backup_day'],
                        backup_week=week_cron,
                        backup_type=data['backup_type'],
                    )
                    crontab.save()
                    if int(data['backup_type']) == 1:
                        # check connect ssh
                        cmd = 'sshpass -p {} ssh -o StrictHostKeyChecking=no -p {} -q {}@{} exit;echo $?'.format(
                            data['password'], data['port'], data['user'], data['host'])
                        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
                        if str(res.stdout).replace('\n', '') != '0':
                            raise ValueError('Remote connection failed')
                        crontab.host = data['host']
                        crontab.port = data['port']
                        crontab.user = data['user']
                        crontab.password = data['password']
                        crontab.path = data['path']
                        crontab.save()
                        pass
                    elif int(data['backup_type']) == 2:
                        # backup google drive
                        pass
                    else:
                        # backup localhost
                        pass
                else:
                    data_result['errors'] = form.errors
                    raise ValueError('Params is validate! Please check value')

                data_result['status'] = 1
                data_result['msg'] = 'Add Crontab Successfully!'
                data_result['data'] = {'id': crontab.pk}
                transaction.commit()
            except BaseException as e:
                transaction.rollback()
                rollBackCron(cron_id)
                data_result['msg'] = str(e)
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(data_result)

def deleteCron(request,cron_id=None):
    """
    delete crontab
    :param request:
    :param cron_id:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        try:
            transaction.set_autocommit(False)
            crontab = CronJob.objects.get(pk=cron_id)
            crontab.delete()
            jobs = CronTab(user=True)
            jobs.remove_all(comment=cron_id)
            jobs.write()
            data_result['status'] = 1
            data_result['msg'] = 'Delete Crontab Successfully!'
            transaction.commit()
        except ObjectDoesNotExist:
            data_result['msg'] = "CronJob doesn't exist!"
            return JsonResponse(data_result)
        except BaseException as e:
            transaction.rollback()
            rollBackCron(cron_id)
            data_result['msg'] = str(e)
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(data_result)

def rollBackCron(cron_id=None):
    """
    rollback cronjob
    :param cron_id:
    :return:
    """
    job = CronJob.objects.get(pk=cron_id)
    pass

def addRetention(request):
    """
    add|edit retention backup
    :param request:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        form = RetentionForm(request.POST)
        data = request.POST.copy()
        if form.is_valid():
            del data['backup_schedu']
            jobs = CronTab(user=True)
            jobs.remove_all(comment=re.compile('backup_((daily)|(weekly)|(monthly))_retention'))
            jobs.write()
            for datum in data:
                if datum == 'backup_daily_retention':
                    job = jobs.new(command='/usr/src/retention_daily_setting -n {}'.format(data[datum]),comment=datum)
                elif datum == 'backup_weekly_retention':
                    job = jobs.new(command='/usr/src/retention_weekly_setting -n {}'.format(data[datum]), comment=datum)
                else:
                    job = jobs.new(command='/usr/src/retention_monthly_setting -n {}'.format(data[datum]), comment=datum)
                job.hour.on(23)
                job.minute.on(0)
                jobs.write()
            data_result['status'] = 1
            data_result['msg'] = 'Add Retention Successfully!'
        else:
            data_result['errors'] = form.errors
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(data_result)

def deleteRetention(request):
    """
    delete retention backup
    :param request:
    :return:
    """
    data_result = {'status': 0, 'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        jobs = CronTab(user=True)
        jobs.remove_all(comment=re.compile('backup_((daily)|(weekly)|(monthly))_retention'))
        jobs.write()
        data_result['status'] = 1
        data_result['msg'] = 'Delete Cronjob Successfully!'
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException:
        data_result['msg'] = 'Can not delete cronjob Retention!'

    return JsonResponse(data_result)
