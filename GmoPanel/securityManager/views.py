from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from loginSys.models import Account
from websiteManager.models import Provision
from .models import Waf
from .forms import GoogleForm,AuthenRebaForm,IpRebiForm,ChangeAuthForm,ChangeIpForm
from plogical import phpSetting,settingManager,hashPassword
import pyotp,html
import urllib.request
import re,subprocess
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import datetime

def index(request):
    """
    config waf and retriction
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        provisions = Provision.objects.filter(account_id=userId, deactive_flg=0)
        count = provisions.count()
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'securityManager/index.html',{'page_title': 'WAF & Restrict','count': count,'data': provisions})


def authenGoogle(request):
    """
    config google authen
    :param request:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        qrCodeUrl = None
        if request.POST:
            data = request.POST.copy()
            try:
                if request.POST['security_status'] == 'on':
                    data['security_status'] = True
            except BaseException:
                data['security_status'] = False
            form = GoogleForm(data)
            if form.is_valid():
                qrCodeUrl = settings.URL_GOOGLE_AUTHEN + pyotp.totp.TOTP(data['security_code']).provisioning_uri(settings.GOOGLEAUTH + '-' + account.login_id)
                account.security_status = data['security_status']
                account.security_code = data['security_code']
                account.save()
                messages.success(request, "Change Google Authenticator success.")

            else:
                messages.error(request, "There was a problem submitting your form.")
        else:
            if account.security_code is not None:
                code = account.security_code
            else:
                code = pyotp.random_base32()
            form = GoogleForm(initial={'security_status': account.security_status,'security_code': code})
            qrCodeUrl = settings.URL_GOOGLE_AUTHEN+pyotp.totp.TOTP(code).provisioning_uri(settings.GOOGLEAUTH+'-'+account.login_id)
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'securityManager/authen_google.html', {'page_title': 'Google Authenticator','form': form,'qrCodeUrl': qrCodeUrl})

def getSecuriryCode(request):
    """
    ajax change security code
    :param request:
    :return:
    """
    result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        code = pyotp.random_base32()
        qrCodeUrl = settings.URL_GOOGLE_AUTHEN + pyotp.totp.TOTP(code).provisioning_uri(settings.GOOGLEAUTH + '-' + account.login_id)
        result['status'] = 1;
        result['securityCode'] = code
        result['qrCodeUrl'] = qrCodeUrl
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(result)

def action(request,domain=None):
    """
    render view action
    :param request:
    :param domain:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        try:
            provision = Provision.objects.get(account_id=account.id,domain=domain,deactive_flg=0)
            # check status Waf
            output = phpSetting.execute('kusanagi target {};kusanagi status | grep "*** WAF" -A1 | tail -n 1'.format(provision.provision_name))
            output = output.split('\n')
            try:
                onOff = output[-2]
            except BaseException:
                onOff = 'off'
            # get log waf
            listLog = []
            if onOff == 'on':
                outputLog = phpSetting.execute('/usr/src/get_naxsi_log -d {}'.format(provision.provision_name))
                outputLog = html.unescape(str(outputLog))
                arrOutput = outputLog.split("\n")
                for value in arrOutput:
                    temp = {}
                    value = value.split('error')
                    try:
                        temp['time'] = value[0]
                        val = value[1].split(':')
                        temp['attack_url'] = val[4].split(', request')[0]
                        attrack = val[5].split(', host')[0].split(' ')
                        temp['attack_content'] = attrack[1]
                        if re.search('HTTP/1.1',attrack[2]):
                            temp['attack_url'] = 'http://'+temp['attack_url']+temp['attack_content']
                        else:
                            temp['attack_url'] = 'https://'+temp['attack_url']+temp['attack_content']
                        temp['attack_ip'] = val[3].split(', server')[0]
                        listLog.append(temp)
                    except BaseException:
                        pass
            form_auth = AuthenRebaForm()
            form_ip = IpRebiForm()
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/securitys/index')

    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'securityManager/action.html',{'page_title': 'WAF & Restrict','provision': provision,'onOff': onOff,'listLog': listLog,'form_auth': form_auth,'form_ip': form_ip})

def changeStatus(request,pro_id=None):
    """
    change status waf website
    :param request:
    :return:
    """
    result = {'status': 0,'msg': ''}
    try:
        userId = request.session['userID']
        account = Account.objects.get(id=userId)
        provision = Provision.objects.get(pk=pro_id,account_id=account.id,deactive_flg=0)
        if request.POST:
            try:
                status = request.POST['status']
            except BaseException:
                status = 0
            if status:
                phpSetting.execute('kusanagi target {};kusanagi waf on'.format(provision.provision_name))
            else:
                phpSetting.execute('kusanagi target {};kusanagi waf off'.format(provision.provision_name))
            result['status'] = 1
            result['msg'] = 'You change status WAF success!'
    except KeyError:
        return HttpResponseRedirect('/login')
    except ObjectDoesNotExist:
        result['msg'] = 'Provision is not exits!'
    except BaseException:
        pass

    return JsonResponse(result)

def listReba(request,pro_id=None):
    """
    list Restrict access by authentication
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        provision = Provision.objects.get(pk=pro_id,account_id=account.id,deactive_flg=0)
        data = Waf.objects.filter(provision_id=provision.id,type=1)
    except ObjectDoesNotExist:
        return HttpResponse('<tr><td colspan="5" class="text-center">Invalid website. Please try again.</td></tr>')
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'securityManager/list_reba.html',{'page_title': 'WAF & Restrict','data': data,'count': len(data)})

def saveReba(request,pro_id=None):
    """
    Save Restrict access by authentication configuration
    :param request:
    :param pro_id:
    :return:
    """
    result = {'status': 0,'msg': ''}
    try:
        userID= request.session['userID']
        account = Account.objects.get(pk=userID)
        provision = Provision.objects.get(pk=pro_id,account_id=account.id,deactive_flg=0)
        if request.POST:
            try:
                transaction.set_autocommit(False)
                form = AuthenRebaForm(request.POST)
                if form.is_valid():
                    waf = form.save(commit=False)
                    waf.type = 1
                    waf.serial = int(datetime.datetime.now().timestamp())
                    waf.provision_id = provision.id
                    Retriction = settingManager.SettingManager(provision.provision_name)
                    if Retriction.add_authentication(waf.url,waf.user,waf.password,waf.serial):
                        waf.save()
                        result['msg'] = 'You create account access by authentication success!';
                    else:
                        raise ValueError('Can not create access by authentication. Please try again!')
                else:
                    for error in form.errors.values():
                        raise ValueError(str(error[0]))
                result['status'] = 1
                transaction.commit()
            except BaseException as e:
                result['msg'] = str(e)
                transaction.rollback()
    except ObjectDoesNotExist:
        result['msg'] = 'Provision is not exist!'
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(result)

def deleteReba(request,waf_id = None):
    """
    Delete Restrict access by authentication configuration
    :param request:
    :param waf_id:
    :return:
    """
    result = {'status': 0, 'msg': ''}
    try:
        transaction.set_autocommit(autocommit=False)
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id,type=1,provision__account_id=account.id,provision__deactive_flg=0)
        Retriction = settingManager.SettingManager(waf.provision.provision_name)
        if Retriction.delete_authentication(waf.url,waf.serial):
            waf.delete()
            transaction.commit()
            result['status'] = 1
            result['msg'] = 'Deleting configuration is completed successfully!'
        else:
            raise ValueError('An error occured while deleting configuration.!')
    except ObjectDoesNotExist:
        result['msg'] = 'Record is not exist!'
        transaction.rollback()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        result['msg'] = str(e)
        transaction.rollback()

    return JsonResponse(result)

def getChangePassword(request,waf_id=None):
    """
    get modal change password
    :param request:
    :param waf_id:
    :return:
    """
    try:
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id,type=1, provision__account_id=account.id,provision__deactive_flg=0)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        return HttpResponse('Invalid website. Please try again!')

    return render(request, 'securityManager/modal_change_password.html',{'page_title': 'WAF & Restrict','waf': waf,})

def changePassword(request,waf_id=None):
    """
    change password authen retric
    :param request:
    :param waf_id:
    :return:
    """
    result = {'status': 0, 'msg': ''}
    try:
        transaction.set_autocommit(autocommit=False)
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id,type=1, provision__account_id=account.id,provision__deactive_flg=0)
        Retriction = settingManager.SettingManager(waf.provision.provision_name)
        if request.POST:
            form = ChangeAuthForm(request.POST)
            if form.is_valid():
                waf.password = request.POST['new_password']
                waf.save()
                if Retriction.delete_authentication(waf.url,waf.serial):
                    if Retriction.add_authentication(waf.url, waf.user, waf.password, waf.serial):
                        result['status'] = 1
                        result['msg'] = 'New password has been updated for configuration.'
                    else:
                        raise ValueError('An error occured while trying to update new password.Can not add Rule new')
                else:
                    raise ValueError('An error occured while trying to update new password.Can not add Rule new!')
            else:
                raise ValueError('Params is validate! Please check value')
        transaction.commit()
    except ObjectDoesNotExist:
        result['msg'] = 'Record is not exist!'
        transaction.rollback()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        result['msg'] = str(e)
        transaction.rollback()

    return JsonResponse(result)

def listRebi(request,pro_id=None):
    """
    list Restrict access by ip filter
    :param request:
    :param pro_id:
    :return:
    """
    try:
        userId = request.session['userID']
        account = Account.objects.get(pk=userId)
        provision = Provision.objects.get(pk=pro_id, account_id=account.id, deactive_flg=0)
        data = Waf.objects.filter(provision_id=provision.id, type=0)
    except ObjectDoesNotExist:
        return HttpResponse('<tr><td colspan="5" class="text-center">Invalid website. Please try again.</td></tr>')
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'securityManager/list_rebi.html', {'page_title': 'WAF & Restrict','data': data,'count': len(data)})

def saveRebi(request,pro_id=None):
    """
    Save Restrict access by ip filer configuration
    :param request:
    :param pro_id:
    :return:
    """
    result = {'status': 0, 'msg': ''}
    try:
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        provision = Provision.objects.get(pk=pro_id, account_id=account.id, deactive_flg=0)
        if request.POST:
            try:
                transaction.set_autocommit(False)
                form = IpRebiForm(request.POST)
                if form.is_valid():
                    waf = form.save(commit=False)
                    waf.type = 0
                    waf.serial = int(datetime.datetime.now().timestamp())
                    waf.provision_id = provision.id
                    Retriction = settingManager.SettingManager(provision.provision_name)
                    if Retriction.add_filterip(waf.url, waf.ip, waf.serial):
                        waf.save()
                        result['msg'] = 'You create account access by IP success!'
                        result['status'] = 1
                        transaction.commit()
                    else:
                        raise ValueError('Can not create access by IP. Please try again!')
                else:
                    for error in form.errors.values():
                        raise ValueError(str(error[0]))
            except BaseException as e:
                result['msg'] = str(e)
                transaction.rollback()
    except ObjectDoesNotExist:
        result['msg'] = 'Provision is not exist!'
    except KeyError:
        return HttpResponseRedirect('/login')

    return JsonResponse(result)

def deleteRebi(request,waf_id=None):
    """
    Delete Restrict access by ip filter configuration
    :param request:
    :param waf_id:
    :return:
    """
    result = {'status': 0, 'msg': ''}
    try:
        transaction.set_autocommit(autocommit=False)
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id,type=0, provision__account_id=account.id,provision__deactive_flg=0)
        Retriction = settingManager.SettingManager(waf.provision.provision_name)
        if Retriction.delete_filterip(waf.url, waf.serial):
            waf.delete()
            transaction.commit()
            result['status'] = 1
            result['msg'] = 'Deleting configuration is completed successfully!'
        else:
            raise ValueError('An error ocured while deleting configuration.!')
    except ObjectDoesNotExist:
        result['msg'] = 'Record is not exist!'
        transaction.rollback()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        result['msg'] = str(e)
        transaction.rollback()

    return JsonResponse(result)

def getChangeIp(request,waf_id=None):
    """
    Render view change ip
    :param request:
    :param waf_id:
    :return:
    """
    try:
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id,type=0 ,provision__account_id=account.id ,provision__deactive_flg=0)
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        return HttpResponse('Invalid website. Please try again!')

    return render(request, 'securityManager/modal_change_ip.html',{'page_title': 'WAF & Restrict','waf': waf,})

def changeIp(request,waf_id=None):
    """
    change rule allow IP
    :param request:
    :param waf_id:
    :return:
    """
    result = {'status': 0, 'msg': ''}
    try:
        transaction.set_autocommit(autocommit=False)
        userID = request.session['userID']
        account = Account.objects.get(pk=userID)
        waf = Waf.objects.select_related('provision').get(pk=waf_id, type=0, provision__account_id=account.id,provision__deactive_flg=0)
        Retriction = settingManager.SettingManager(waf.provision.provision_name)
        if request.POST:
            form = ChangeIpForm(request.POST)
            if form.is_valid():
                waf.ip = request.POST['new_ip']
                waf.save()
                if Retriction.delete_filterip(waf.url, waf.serial):
                    if Retriction.add_filterip(waf.url, waf.ip, waf.serial):
                        result['status'] = 1
                        result['msg'] = 'New IP has been updated for configuration.'
                    else:
                        raise ValueError('An error occured while trying to update new IP.Can not add Rule new')
                else:
                    raise ValueError('An error occured while trying to update new IP.Can not add Rule new')
            else:
                for error in form.errors.values():
                    raise ValueError(str(error[0]))
        transaction.commit()
    except ObjectDoesNotExist:
        result['msg'] = 'Record is not exist!'
        transaction.rollback()
    except KeyError:
        return HttpResponseRedirect('/login')
    except BaseException as e:
        result['msg'] = str(e)
        transaction.rollback()

    return JsonResponse(result)

