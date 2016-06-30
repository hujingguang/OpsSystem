# -*- coding=UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponseServerError,HttpResponseNotAllowed,HttpResponseForbidden,StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from datetime import datetime
from django.shortcuts import render_to_response
from models import *
from forms import CmdInputForm,DownloadFileForm
import time,commands,os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import SaltByLocalApi,parse_target_params,juge_danger_cmd
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
ALLOW_DOWNLOAD_DIR=['/logs']
@login_required(login_url='/')
def list_host_info(request):
    hosts=HostInfoModel.objects.all().order_by('group')
    total=len(hosts)
    paginator=Paginator(hosts,10)
    page=request.GET.get('page')
    try:
	host=paginator.page(page)
    except PageNotAnInteger:
	host=paginator.page(1)
    except EmptyPage:
	host=paginator.page(paginator.num_pages)
    return render_to_response('salt_hosts.html',RequestContext(request,{'hosts':host,'total':total}))

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
		        return HttpResponseServerError(request)
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
	if not request.user.is_superuser:
	    return HttpResponseForbidden(request)
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
	target=info
        client=SaltByLocalApi('/etc/salt/master')
	cmd='%s.install' %app
	output=client.client.cmd(target,'state.sls',[cmd],expr_form=mapping)
	if output is None or output == {}:
	    return render_to_response('salt_deploy_application.html',RequestContext(request,{'error':u'无效的目标主机'}))
	error_dict={}
	error_log=''
	ok_dict={}
	all_dict={}
	for k,v in output.iteritems():
	    if isinstance(v,list):
		return render_to_response('salt_deploy_application.html',RequestContext(request,{'error':v[0]}))
	    tmp_list=[]
	    for i,j in v.iteritems():
		if 'name' not in j or 'duration'  not in j or 'comment' not in j:
		    tmp_list.append([i,' ',0,j['result'],j['changes'],j['comment']])
		else:
		    tmp_list.append([i,j['name'],j['duration'],j['result'],j['changes'],j['comment']])
	    all_dict[k]=tmp_list
	for k ,v in all_dict.iteritems():
	    for i in v:
		if not i[3]:
		    error_dict[k]=v
		    break
	if len(error_dict)>0:
	    host_error_dict={}
            for k,v in error_dict.iteritems():
	        host_error_list=[]
	        for i in v:
		    if not i[3]:
		        host_error_list.append(i)
			break
	        host_error_dict[k]=host_error_list
	    for k,v in host_error_dict.iteritems():
		error_log=error_log+'''-----host name: %s error log -----\n''' %k
                for i in v:
		    if i[4] != {} and isinstance(i[4],dict):
			error_log=error_log+'''id:  %s   \n comment: %s \n name: %s  \n   %s \n''' %(i[0],i[5],i[1],i[4]['stderr'])
		    else:
			error_log=error_log+'''id:   %s   \n comment: %s \n name: %s  \n     %s \n''' %(i[0],i[5],i[1],i[4])
	all_key=all_dict.keys()
	for key in all_key:
	    if key not in error_dict.keys():
		ok_dict[key]=all_dict[key]
	head_txt='-'*10+'\n'
        head_txt=head_txt+''' total: %d , successed: %d  , failed: %d  \n''' %(len(all_dict),len(ok_dict),len(error_dict))
	head_txt=head_txt+'-'*10+'\n'
	success_txt='-'*10+'success'+'-'*10+'\n'
	error_txt=''
	total_error_spend_time=0
	total_ok_spend_time=0
	if len(ok_dict)>0:
	    for k,v in ok_dict.iteritems():
		ok_spend_time=0
		for i in v:
		    ok_spend_time=i[2]+ok_spend_time
		ok_spend_time=ok_spend_time/1000
		total_ok_spend_time=total_ok_spend_time+ok_spend_time
                success_txt=success_txt+''' Host: %s  | Spend time: %s Sec | Result: success \n''' %(k,str(ok_spend_time))
	success_txt=success_txt+'-----success-----\n'
	if len(error_dict)>0:
	   log=''
	   for k,v in error_dict.iteritems():
	       error_spend_time=0
	       for i in v:
		   if i[4] != {} and isinstance(i[4],dict):
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4]['stderr'])
		   else:
	               log=log+'''name: %s \n  --error_info--: %s \n ''' %(i[1],i[4])
		   error_spend_time=i[2]+error_spend_time
               error_spend_time=error_spend_time/1000
	       total_error_spend_time=total_error_spend_time+error_spend_time
	       error_txt=error_txt+''' Host: %s   | Spend time: %s Sec | Result: failed  \n ''' %(k,str(error_spend_time))
	       #error_txt=error_txt+'''-----------host: %s error log-----------\n''' %k
	       error_txt=error_txt+'''%s \n ----------\n''' %error_log
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
		log=head_txt+success_txt+error_txt,
		duration=str(total_error_spend_time+total_ok_spend_time)+' s')
	try:
	    deploylog.save()
	except:
	    pass
	f=open('/tmp/.app_deploy.log','w')
	f.write(head_txt+success_txt+error_txt)
	f.close()
	code,log=commands.getstatusoutput('cat /tmp/.app_deploy.log')
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
	     if not request.user.is_superuser:
		 flag=True
		 if command.startswith('ls'):
		     flag=False
		 if command.startswith('/root/deploy/deploy_test.sh'):
		     num,output=commands.getstatusoutput(command)
		     if num != 0 :
			 error='please checkout your command format !'
			 return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'cmd_error':error}))
                     cmd_info=CmdRunLogModel(user=request.user,
		         time=datetime.now(),
		         target=target,
		         mapping=mapping,
		         cmd=command,
		         hosts='self',
		         total=1)
		     cmd_info.save()
                     return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'result':output}))
		 if  ';' in command or r'&' in command or r'|' in command :
		     flag=True
                 if flag: 
		     error='Permission Denied ! '
		     return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'cmd_error':error}))
	     target=info
	     client=SaltByLocalApi('/etc/salt/master')
	     output=client.client.cmd(target,'cmd.run',[command],expr_form=mapping)
             if output is None or output == {}:
		 error='Bad Target Host !!!'
		 return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'error':error}))
	     result=''
	     hosts=[]
	     for k,v in output.iteritems():
		 hosts.append(k)
		 result=result+'\n\n------'+k+'-----\n\n'+v
	     f=open('/tmp/.cmd_run.out','w')
	     f.write(result)
	     f.close()
	     code,result=commands.getstatusoutput('cat /tmp/.cmd_run.out')
	     if target == '*':
	         cmd_info=CmdRunLogModel(user=request.user,
		         time=datetime.now(),
		         target=target,
		         mapping=mapping,
		         cmd=command,
		         hosts='all hosts',
		         total=len(hosts))
	     else:
	         cmd_info=CmdRunLogModel(user=request.user,
		         time=datetime.now(),
		         target=target,
		         mapping=mapping,
		         cmd=command,
		         hosts=','.join(hosts),
		         total=len(hosts))
	     try:
		 cmd_info.save()
	     except:
		 pass
	     return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form,'result':result}))
	else:
	    return render_to_response('salt_cmd_run.html',RequestContext(request,{'form':form}))
    else:
	return HttpResponseNotAllowed(request)

@login_required(login_url='/')
def list_app_deploy_info(request):
    app_deploy_info=AppDeployLogModel.objects.all().order_by('-time')
    for a in app_deploy_info:
	a.time=datetime.strftime(a.time,'%Y-%m-%d %H:%M:%S')
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
    cmd_list=CmdRunLogModel.objects.all().order_by('-time')
    for cmd in cmd_list:
	cmd.time=datetime.strftime(cmd.time,'%Y-%m-%d %H:%M:%S')
    paginator=Paginator(cmd_list,10)
    page=request.GET.get('page')
    try:
	cmd_info=paginator.page(page)
    except PageNotAnInteger:
	cmd_info=paginator.page(1)
    except EmptyPage:
	cmd_info=paginator.page(paginator.num_pages)
    return render_to_response('list_cmd_run_info.html',RequestContext(request,{'cmd_info':cmd_info}))

@login_required(login_url='/')
def download_file(request):
    global ALLOW_DOWNLOAD_DIR
    form=DownloadFileForm()
    if request.method == 'POST':
	form=DownloadFileForm(request.POST)
	if form.is_valid():
	    saltapi=SaltByLocalApi('/etc/salt/master')
	    target=form.cleaned_data['target'].replace(' ','')
	    file_path=form.cleaned_data['file_path'].replace(' ','')
	    if file_path.endswith('/'):
		file_path=file_path[:len(file_path)-1]
	    file_split=os.path.split(file_path)
	    file_parent_dir=file_split[0]
            default_dir='/var/cache/salt/master/minions'
	    output=saltapi.client.cmd(target,'cp.push',[file_path]) 
	    if target not in saltapi.connected_minions_list:
		form.errors['target']=u'无效的主机名！！！'
	        return render_to_response('download_file.html',RequestContext(request,{'form':form}))
	    output=saltapi.client.cmd(target,'cp.push',[file_path]) 
	    local_absolute_path=default_dir+'/'+target+'/files/'+file_path
	    print local_absolute_path
	    if not output.get(target,False):
		form.errors['file_path']=u'不存在该文件或输入的为目录！！'
	    elif not os.path.exists(local_absolute_path):
		form.errors['file_path']=u'下载失败！！！'
	    else:
		flag=False
		for allow_dir in ALLOW_DOWNLOAD_DIR:
		    if file_path.startswith(allow_dir):
			flag=True
			break
		if not request.user.is_superuser:
		    if not flag:
			form.errors['file_path']=u'该文件非管理员无法下载！！'
	                return render_to_response('download_file.html',RequestContext(request,{'form':form}))
		def file_iterator(local_file,chunk_size=512):
		    with open(local_file) as f:
			while True:
			    c=f.read(chunk_size)
			    if c:
				yield c
			    else:
				break
		file_name=file_split[1]
		response=StreamingHttpResponse(file_iterator(local_absolute_path))
		response['Content-Type'] = 'application/octet-stream'
		response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
	        return response
	    return render_to_response('download_file.html',RequestContext(request,{'form':form}))
	#return render_to_response('download_file.html',RequestContext(request,{'form':form,'file':file_path}))
    return render_to_response('download_file.html',RequestContext(request,{'form':form}))



