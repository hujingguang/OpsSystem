# -*- coding=UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from forms import DbAuthForm
from datetime import datetime
from models import *
import json
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import time


@login_required(login_url='/')
def db_auth_info_list(request):
    if not request.user.is_superuser:
	return HttpResponse(403)
    db_list=DatabaseAuthInfoModel.objects.all().order_by('-createtime').order_by('envtype')
    for d in db_list:
	d.createtime=datetime.strftime(d.createtime,'%Y-%m-%d %H:%M:%S')
    paginator=Paginator(db_list,12)
    page=request.GET.get('page')
    try:
	db=paginator.page(page)
    except PageNotAnInteger:
	db=paginator.page(1)
    except EmptyPage:
	db=paginator.page(paginator.num_pages)
    db_auth_form=DbAuthForm()
    return render_to_response('db_info_list.html',RequestContext(request,{'db_list':db,'db_auth_form':db_auth_form}))

@login_required(login_url='/')
def db_auth_info_edit(request):
    if request.method=='POST' and request.user.is_superuser:
	auth_id=request.POST.get('userid','').replace(' ','')
	dbuser=request.POST.get('dbuser','').replace(' ','')
	accesshost=request.POST.get('accesshost','').replace(' ','')
	accessauth=request.POST.get('accessauth','').replace(' ','')
	accessdb=request.POST.get('accessdb','').replace(' ','')
	owner=request.POST.get('owner','').replace(' ','')
	envtype=request.POST.get('envtype','').replace(' ','')
	useperson=request.POST.get('useperson','').replace(' ','')
	comment=request.POST.get('comment','').replace(' ','')
        if not dbuser or not accesshost or not accessauth or not accessdb or not owner or not envtype or not useperson:
	    return HttpResponse(json.dumps({'code':403,'info':u'包含错误的提交参数!'}))
	else:
	    try:
	        db_info=DatabaseAuthInfoModel.objects.get(id=auth_id)
		db_info.username=dbuser
		db_info.accesshost=accesshost
		db_info.accessauth=accessauth
		db_info.accessdb=accessdb
		db_info.owner=owner
		db_info.envtype=envtype
		db_info.useperson=useperson
		db_info.comment=comment
		db_info.save()
	    except Exception as e:
		return HttpResponse(json.dumps({'code':500,'info':u'修改失败'}))
	    else:
		return HttpResponse(json.dumps({'code':200,'info':u'修改成功'}))
    return HttpResponse(json.dumps({'code':403,'info':u'非法提交参数'}))


@login_required(login_url='/')
def db_auth_info_query(request):
    if request.method=='POST':
	query_id=request.POST.get('id','')
	if query_id:
	    try:
	        db_info=DatabaseAuthInfoModel.objects.get(id=query_id)
	    except Exception as e:
		return HttpResponse(json.dumps({'code':403,'info':u'不存在该记录!'}))
	    else:
		db_info_ret={
			'username':db_info.username,
			'accesshost':db_info.accesshost,
			'accessdb':db_info.accessdb,
			'accessauth':db_info.accessauth,
			'owner':db_info.owner,
			'envtype':db_info.envtype,
			'useperson':db_info.useperson,
			'comment':db_info.comment,
			}
		return HttpResponse(json.dumps(db_info_ret))
    return HttpResponse(json.dumps({'code':403,'info':u'非法请求方法'}))


		
	    

@login_required(login_url='/')
def db_auth_info_delete(request):
    if request.method == 'POST':
	db_id=request.POST.get('id','')
	try:
	    db=DatabaseAuthInfoModel.objects.get(id=db_id);
	    db.delete()
	except Exception as e:
	    return HttpResponse(json.dumps({'code':403,'info':u'删除失败'}))
	return HttpResponse(json.dumps({'code':200,'info':u'已删除'}))
    else:
	return HttpResponse(json.dumps({'code':403,'info':u'删除失败'}))
@login_required(login_url='/')
def db_auth_info_add(request):
    if request.method=='POST':
	dbuser=request.POST.get('dbuser','').replace(' ','')
	accesshost=request.POST.get('accesshost','').replace(' ','')
	accessauth=request.POST.get('accessauth','').replace(' ','')
	accessdb=request.POST.get('accessdb','').replace(' ','')
	owner=request.POST.get('owner','').replace(' ','')
	envtype=request.POST.get('envtype','').replace(' ','')
	useperson=request.POST.get('useperson','').replace(' ','')
	comment=request.POST.get('comment','').replace(' ','')
	if not dbuser or not accesshost or not accessauth or not accessdb or not owner or not envtype or not useperson:
	    return HttpResponse(json.dumps({'code':403,'info':u'包含错误的提交参数!'}))
	else:
	    dbinfo=DatabaseAuthInfoModel(username=dbuser,
		    accesshost=accesshost,
		    accessdb=accessdb,
		    accessauth=accessauth,
		    owner=owner,
		    useperson=useperson,
		    envtype=envtype,
		    createtime=datetime.now(),
		    comment=comment)
	    try:
		dbinfo.save()
	    except Exception as e:
		return HttpResponse(json.dumps({'code':500,'info':u'提交失败'}))
	    return HttpResponse(json.dumps({'code':200,'info':u'添加成功'}))
    else:
	return HttpResponse(json.dumps({"code":403}))

@login_required(login_url='/')
def repo_auth_info_list(request):
    pass
@login_required(login_url='/')
def repo_auth_info_edit(request):
    pass
@login_required(login_url='/')
def repo_auth_info_delete(request):
    pass
@login_required(login_url='/')
def repo_auth_info_add(request):
    pass


