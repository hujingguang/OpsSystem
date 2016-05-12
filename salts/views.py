# -*- coding=UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from datetime import datetime
from django.shortcuts import render_to_response
from models import *
import time
from utils import SaltByLocalApi,parse_target_params
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
    match_list=['list','grain','nodegroup','pcre','glob']
    app_list=['zabbix','mysql','memcached','nginx','tomcat','init','redis','php']
    if request.method=='POST':
	mapping=request.POST.get('map','').replace(' ','')
	target=request.POST.get('target','').replace(' ','')
	app=str(request.POST.get('app','').replace(' ',''))
	if app == '' or target == '' or mapping == '':
	    return HttpResponseNotAllowed(request)
	if mapping not in match_list or app not in app_list:
	    return HttpResponseNotAllowed(request)
	result,info=parse_target_params(target,mapping)
	if result is None:
	    return render_to_response('salt_deploy_application.html',RequestContext(request,{'error':info}))
        client=SaltByLocalApi('/etc/salt/master')
	cmd='%s.install' %app
	output=client.client.cmd(target,'state.sls',[cmd],expr_form=mapping) 
	if output is None or output == {}:
	    return render_to_response('salt_deploy_application.html',RequestContext(request,{'error':u'无效的目标主机'}))
	error_dict={}
	ok_dict={}
	all_dict={}
	for k,v in output.iteritems():
	    tmp_list=[]
	    for i,j in v.iteritems():
		if 'name' not in j or 'duration'  not in j:
		    tmp_list.append([i,' ',0,j['result'],j['changes']])
		else:
		    tmp_list.append([i,j['name'],j['duration'],j['result'],j['changes']])
	    all_dict[k]=tmp_list 
	for k ,v in all_dict.iteritems():
	    for i in v:
		if not i[3]:
		    error_dict[k]=v
		    break
	all_key=all_dict.keys()
	for key in all_key:
	    if key not in error_dict.keys():
		ok_dict[key]=all_dict[key]
	head_txt='----------------------------\n'
        head_txt=head_txt+''' total: %d , successed: %d  , failed: %d  \n''' %(len(all_dict),len(ok_dict),len(error_dict))
	head_txt=head_txt+'------------------------------\n'
	success_txt='---------------success-------------\n'
	error_txt=''
	if len(ok_dict)>0:
	    for k,v in ok_dict.iteritems():
		spend_time=0
		for i in v:
		    spend_time=i[2]+spend_time
		spend_time=str(spend_time/1000)
                success_txt=success_txt+''' Host: %s  | Spend time: %s Sec | Result: success \n''' %(k,spend_time)
	success_txt=success_txt+'--------------success-------------\n'
	if len(error_dict)>0:
	   log=''
	   for k,v in error_dict.iteritems():
	       spend_time=0
	       for i in v:
		   if v[4] != {} and isinstance(v[4],dict):
		       print type(i[4]['stderr'])
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4]['stderr'])
		   else:
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4])
		   spend_time=i[2]+spend_time
               spend_time=str(spend_time/1000)
	       error_txt=error_txt+''' Host: %s   | Spend time: %s Sec | Result: failed  \n ''' %(k,spend_time)
	       error_txt=error_txt+'''-----------host: %s error log-----------\n''' %k
	       error_txt=error_txt+'''%s \n -------------------------\n''' %log
        deploylog=AppDeployLogModel(user=request.user,
		time=datetime.now(),
		target=target,
		application=app,
		mapping=mapping,
		log=head_txt+success_txt+error_txt)
	try:
	    deploylog.save()
	except:
	    pass
	f=open('/tmp/.app_deploy.log','w')
	f.write(head_txt+success_txt+error_txt)
	f.close()
        f=open('/tmp/.app_deploy.log','r')
	log=f.readlines()
	f.close()
	return render_to_response('salt_deploy_application.html',RequestContext(request,{'log':log}))
    return render_to_response('salt_deploy_application.html',RequestContext(request))



