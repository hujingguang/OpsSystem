# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponseNotAllowed,HttpResponse
from utils import *
import json
from salts.utils import SaltByLocalApi
@login_required(login_url='/')
def index(request):
    if request.method=='POST':
	return HttpResponseNotAllowed(request)
    local=SaltByLocalApi('/etc/salt/master')
    res=local.get_minions_key_status()
    key_status={'a_n':res[0],'r_n':res[1],'u_n':res[2]}
    minion_status=local.get_minions_status()
    minion_status=json.dumps(minion_status)
    key_status=json.dumps(key_status)
    sys_info_dict=get_system_info()
    return render_to_response('index.html', RequestContext(request,{'Dict': key_status,'info':minion_status,'info_dict':sys_info_dict}))

def login_view(request):
    if request.user.is_authenticated():
	return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_active:
	    login(request, user)
	    #return render_to_response('index.html',RequestContext(request))
	    return HttpResponseRedirect(reverse('index'))
        else:
	    return render_to_response('login_new.html',RequestContext(request,{'error':'Bad Username or Password'}))
    else:
	return render_to_response('login_new.html',RequestContext(request,{'error':''}))

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='/')
def change_password(request):
    if request.method=='POST':
	old_pwd=request.POST.get('old_pwd','')
	new_pwd=request.POST.get('new_pwd','')
	again_pwd=request.POST.get('again_pwd','')
	print old_pwd,new_pwd,again_pwd
	if new_pwd.replace(' ','') == '' or again_pwd.replace(' ','')=='' or old_pwd.replace(' ','')=='':
	    return HttpResponse(json.dumps({'code':400,'info':u'请输入所有选项'}))
	user=authenticate(username=request.user.username,password=old_pwd)
	if user is not None and  user.is_active:
	    print user.is_active,user
	    user.set_password(again_pwd)
	    try:
		user.save()
	    except Exception as e:
	        return HttpResponse(json.dumps({'code':400,'info':u'修改失败'}))
	    else:
	        return HttpResponse(json.dumps({'code':200,'info':u'修改成功'}))
	else:
	    return HttpResponse(json.dumps({'code':400,'info':u'原密码错误！'}))

