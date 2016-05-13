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
from forms import CmdInputForm
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import SaltByLocalApi,parse_target_params,juge_danger_cmd
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
	        host_info=HostInfoModel(hostname=host,
			ipaddress=info_list[1],
			cpuinfo=info_list[3],
			meminfo=info_list[4],
			group=info_list[5],
			osinfo=info_list[2],
			area=info_list[6],
			usage=info_list[7])
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
    app_list=['zabbix','mysql','memcached','nginx','tomcat','system','redis','php']
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
	    if isinstance(v,list):
		return render_to_response('salt_deploy_application.html',RequestContext(request,{'error':v[0]}))
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
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4]['stderr'])
		   else:
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4])
		   spend_time=i[2]+spend_time
               spend_time=str(spend_time/1000)
	       error_txt=error_txt+''' Host: %s   | Spend time: %s Sec | Result: failed  \n ''' %(k,spend_time)
	       error_txt=error_txt+'''-----------host: %s error log-----------\n''' %k
	       error_txt=error_txt+'''%s \n -------------------------\n''' %log
	if ok_dict.keys() == []:
	    success_hosts=''
	else:
	    success_hosts=','.join(ok_dict.keys())
	if error_dict.keys() == []:
	    failed_hosts=''
	else:
	    failed_hosts=','.join(error_dict.keys())
	total=len(all_key)
        deploylog=AppDeployLogModel(user=request.user,
		time=datetime.now(),
		target=target,
		application=app,
		mapping=mapping,
		success_hosts=success_hosts,
		failed_hosts=failed_hosts,
		total=total,
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


@login_required(login_url='/')
def cmd_run(request):
    if request.method=='GET':
        form=CmdInputForm()
        return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form}))
    elif request.method=='POST':
        form=CmdInputForm(request.POST)	
	if form.is_valid():
	     target=form.cleaned_data['target'].replace(' ','')
	     mapping=form.cleaned_data['mapping'].replace(' ','')
	     command=form.cleaned_data['cmdline'].lstrip(' ').rstrip(' ')
             result,info=parse_target_params(target,mapping)
	     if result is None:
		 return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'error':info}))
	     if juge_danger_cmd(command):
		 error='Danger Command !!!!'
		 return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'cmd_error':error}))
	     return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form}))
	else:
	    return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form}))
    else:
	return HttpResponseNotAllowed(request)
@login_required(login_url='/')
def list_app_deploy_info(request):
    app_deploy_info=AppDeployLogModel.objects.all().order_by('-time')
    paginator=Paginator(app_deploy_info,10)
    page=request.GET.get('page')
    try:
	info=paginator.page(page)
    except PageNotAnInteger:
	info=paginator.page(1)
    except EmptyPage:
	info=paginator.page(paginator.num_pages)
    return render_to_response('list_app_deploy_info.html',RequestContext(request,{'app_info':info}))
@login_required(login_url='/')
def list_cmd_run_info(request):
    return render_to_response('list_cmd_run_info.html',RequestContext(request))




