from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import datetime
import json


@login_required(login_url='/')
def list_all_users(request):
    users=User.objects.all()
    for u in users:
	u.last_login=datetime.strftime(u.last_login,'%Y-%m-%d %H:%M:%S')
	u.date_joined=datetime.strftime(u.date_joined,'%Y-%m-%d %H:%M:%S')
    return render_to_response('user_list.html',RequestContext(request,{'users':users}))

@login_required(login_url='/')
def add_user(request):
    if request.method=='POST':
	username=request.POST.get('username','').replace(' ','')
	password=request.POST.get('password','').replace(' ','')
	email=request.POST.get('email','').replace(' ','')
	isadmin=request.POST.get('isadmin','').replace(' ','')
	if username == '' or password == '' or email== '' or isadmin == '':
	    return HttpResponse(json.dumps({'code':400,'info':'Error Form Params'}))
	if isadmin == 'Y':
	    user=User.objects.create_superuser(username=username,email=email,password=password)
	else:
	    user=User.objects.create_user(username=username,email=email,password=password)
	try:
	    user.save()
	except Exception as e:
	    return HttpResponse(json.dumps({'code':400,'info':'add user failed'}))
	return HttpResponse(json.dumps({'code':200,'info':'add user success'}))
    return HttpResponse(json.dumps({'code':400,'info':'error http method'}))
