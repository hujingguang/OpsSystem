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
	if u.last_login:
	    u.last_login=datetime.strftime(u.last_login,'%Y-%m-%d %H:%M:%S')
	else:
	    u.last_login=''
	if u.date_joined:
	    u.date_joined=datetime.strftime(u.date_joined,'%Y-%m-%d %H:%M:%S')
	else:
	    u.date_joined=''
    return render_to_response('user_list.html',RequestContext(request,{'users':users}))

@login_required(login_url='/')
def add_user(request):
    if request.method=='POST':
	username=request.POST.get('username','').replace(' ','')
	password=request.POST.get('password','').replace(' ','')
	email=request.POST.get('email','').replace(' ','')
	isadmin=request.POST.get('isadmin','').replace(' ','')
	if not request.user.is_superuser:
	    return HttpResponse(json.dumps({'code':400,'info':'No Permission'}))
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




@login_required(login_url='/')
def change_user_api(request):
    if request.method=='POST':
	if not request.user.is_superuser:
	    return HttpResponse(json.dumps({'code':400,'info':'No Permission !'}))
	userid=request.POST.get('userid','').replace(' ','')
	opt=request.POST.get('opt','').replace(' ','')
	if not userid or not opt:
	    return HttpResponse(json.dumps({'code':400,'info':'Error Params !'}))
	u=User.objects.get(id=userid)
        if not u:
	    return HttpResponse(json.dumps({'code':400,'info':'User do not exist !'}))
	print dir(u)
	if opt == 'delete':
	    try:
		u.delete()
	    except Exception as e:
	        return HttpResponse(json.dumps({'code':400,'info':'Delete Failed'}))
	elif opt == 'active':
	    if not u.is_active:
		u.is_active=1
		try:
		    u.save()
		except Exception as e:
	            return HttpResponse(json.dumps({'code':400,'info':'Active Failed'}))
	elif opt == 'freeze':
	    if u.is_active:
		u.is_active=0
		try:
		    u.save()
		except Exception as e:
	            return HttpResponse(json.dumps({'code':400,'info':'Freeze Failed'}))
        else:
	    return HttpResponse(json.dumps({'code':400,'info':'Error Params'}))
	return HttpResponse(json.dumps({'code':200,'info':'Change User Status Success'}))
    else:
	return HttpResponse(json.dumps({'code':400,'info':'Error Http Method'}))
