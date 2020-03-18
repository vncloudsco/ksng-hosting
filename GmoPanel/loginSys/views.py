from django.shortcuts import render

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from loginSys.models import Account
from plogical import hashPassword
import psutil
import math
import subprocess

def index(request):
    try:
        userId = request.session['userID']
        context = {
            'userId': userId,
            'ipServer': request.META.get('REMOTE_ADDR'),
            'CpuPer': psutil.cpu_percent(),
            'CpuCore': psutil.cpu_count(),
            'MemToltal': math.ceil(float(psutil.virtual_memory()[0])/float(1024*1024)),
            'MemPer': psutil.virtual_memory()[2],
            'SwapTotal': math.ceil(float(psutil.swap_memory()[0])/float(1024*1024)),
            'SwapPer': psutil.swap_memory()[3],
            'DiskTotal': math.ceil(float(psutil.disk_usage('/')[0])/float(1024*1024*1000)),
            'DiskPer': math.ceil(psutil.disk_usage('/')[3]),
        }
    except KeyError:
        return HttpResponseRedirect('/login')
    return render(request, 'index.html',context)

def login(request):
    try:
        userId = request.session['userID']
        return HttpResponseRedirect('/')
    except KeyError:
        try:
            if request.method == 'POST':
                username = request.POST.get('login_id')
                password = request.POST.get('login_password')
                account = Account.objects.get(login_id=username)
                if account.is_active == False:
                    return HttpResponse("Account is suppend!")
                if hashPassword.check_password(account.password, password):
                    request.session['userID'] = account.pk
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponse("wrong-password!")
        except BaseException as msg:
            return HttpResponse(str(msg))

    return render(request,'loginSys/login.html')

def logout(request):
    try:
        del request.session['userID']
        return HttpResponseRedirect('/login')
    except:
        return HttpResponseRedirect('/login')

def load_chart(request):
    try:
        userId = request.session['userID']
        context = {
            'userId': userId,
            'ipServer': request.META.get('REMOTE_ADDR'),
            'CpuPer': psutil.cpu_percent(),
            'CpuCore': psutil.cpu_count(),
            'MemToltal': math.ceil(float(psutil.virtual_memory()[0])/float(1024*1024)),
            'MemPer': psutil.virtual_memory()[2],
            'SwapTotal': math.ceil(float(psutil.swap_memory()[0])/float(1024*1024)),
            'SwapPer': psutil.swap_memory()[3],
            'DiskTotal': math.ceil(float(psutil.disk_usage('/')[0])/float(1024*1024*1024)),
            'DiskPer': math.ceil(psutil.disk_usage('/')[3]),
        }
    except KeyError:
        return HttpResponseRedirect('/login')

    return render(request, 'chart.html',context)
