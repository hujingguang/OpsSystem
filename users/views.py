from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from datetime import datetime



@login_required(login_url='/')
def list_all_users(request):
    users=User.objects.all()
    for u in users:
	u.last_login=datetime.strftime(u.last_login,'%Y-%m-%d %H:%M:%S')
	u.date_joined=datetime.strftime(u.date_joined,'%Y-%m-%d %H:%M:%S')
    return render_to_response('user_list.html',RequestContext(request,{'users':users}))
