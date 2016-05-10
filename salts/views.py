from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from models import *
import time
from utils import SaltByLocalApi
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
@login_required(login_url='/')
def list_host_info(request):
    hosts=HostInfoModel.objects.all().order_by('group')
    paginator=Paginator(hosts,10)
    page=request.GET.get('page')
    try:
	host=paginator.page(page)
    except PageNotAnInteger:
	host=paginator.page(1)
    except EmptyPage:
	host=paginator.page(paginator.num_pages)
    return render_to_response('salt_hosts.html',RequestContext(request,{'hosts':host}))

@login_required(login_url='/')
def refresh_host_info(request):
    salt=SaltByLocalApi('/etc/salt/master')
    host_info_dict=salt.get_host_info()
    for host,info_list in host_info_dict.iteritems():
	if HostInfoModel.objects.filter(hostname=host.strip('')).count() >0:
	    continue
	if HostInfoModel.objects.filter(hostname=host.strip('')).count()==0:
	    if info_list[5] != '' and info_list[6] !='' and info_list[7] != '':
	        host_info=HostInfoModel(hostname=host,ipaddress=info_list[1],cpuinfo=info_list[3],meminfo=info_list[4],group=info_list[5],osinfo=info_list[2],area=info_list[6],usage=info_list[7])
	        try:
		    host_info.save()
	        except Exception as e:
		    return 500
    all_host=HostInfoModel.objects.all()
    for host in all_host:
	if host.hostname not in host_info_dict:
	    host.delete()
    return  HttpResponseRedirect(reverse('salts:host_info'))

@login_required(login_url='/')
def deploy_application(request):
    if request.method=='POST':
	print request.POST
        time.sleep(10)
    return render_to_response('salt_deploy_application.html',RequestContext(request))



