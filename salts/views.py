# -*- coding=UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponseServerError,HttpResponseNotAllowed,HttpResponseForbidden,StreamingHttpResponse,HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.db import connection
from datetime import datetime
from django.shortcuts import render_to_response
from models import *
from forms import CmdInputForm,DownloadFileForm,ProjectRecord,UploadFileForm
import time,commands,os
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import SaltByLocalApi,parse_target_params,juge_danger_cmd
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import json
import os
import commands
from salts.utils import PROJECT_DICT
from salts.utils import dowith_project_params,is_exist_minion
import sys
reload(sys)
sys.setdefaultencoding('utf8')



ALLOW_DOWNLOAD_DIR=['/logs']
LOG_FILE='/tmp/.ops_deploy.log'
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
def upload_file(request):
    error=None
    if request.method=='POST':
	upload_form=UploadFileForm(request.POST,request.FILES)
	if upload_form.is_valid():
	    client=SaltByLocalApi('/etc/salt/master')
	    target=upload_form.cleaned_data['target']
	    mapping=upload_form.cleaned_data['mapping']
	    upload_path=upload_form.cleaned_data['upload_path']
	    if not is_exist_minion(client,target,mapping) or not request.user.is_superuser:
		error='主机名中存在离线主机,请确认后再上传'
		return render_to_response('upload_file.html',RequestContext(request,{'form':upload_form,'error':error}))
	    else:
		f=request.FILES.get('upload_file',None)
		if not f:
		    return render_to_response('upload_file.html',RequestContext(request,{'form':upload_form,'error':'文件损坏'})) 
		tmp_path=os.path.join('/tmp/',f.name)
		with open(tmp_path,'wb+') as tmp_file:
		    for chunk in f.chunks():
			tmp_file.write(chunk)
		if not os.path.exists('/srv/salt/upload'):
		    os.system('mkdir -p /srv/salt/upload')
		cmd="mv {} /srv/salt/upload/".format(tmp_path)
		os.system(cmd)
		file_path=os.path.join(upload_path,f.name)
		bak_file_path=file_path+'.bak'
		bak_cmd='rm -f %s && cp  %s %s' %(bak_file_path,file_path,bak_file_path)
		client.client.cmd(target,'cmd.run',[bak_cmd],expr_form=mapping)
		output=client.client.cmd(target,'cp.get_file',['salt://upload/'+f.name,file_path,'makedirs=True'],expr_form=mapping)
		DistributeFileRecordModel.objects.create(user=request.user.username,hostname=target,pattern=mapping,path=file_path,filename=f.name,opttime=datetime.now())
		return render_to_response('upload_file.html',RequestContext(request,{'form':upload_form,'error':error,'result':output,'status':200}))
        else:
	    return render_to_response('upload_file.html',RequestContext(request,{'form':upload_form,'cmd_error':'请选择上传的文件!'}))
    upload_form=UploadFileForm()
    return render_to_response('upload_file.html',RequestContext(request,{'form':upload_form,'error':error}))


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



@login_required(login_url='/')
def code_deploy(request):
    all_record=OnlineDeployModel.objects.filter(active='Y').order_by('-create_time')
    for r in all_record:
	if not r.auditor:
	    r.auditor=''
	if not r.publisher:
	    r.publisher=''
	if not r.deploy_status:
	    r.deploy_status=''
	if r.sql_name.replace(' ','') == '':
	    r.sql_name=''
	r.create_time=datetime.strftime(r.create_time,'%Y-%m-%d %H:%M:%S')
    record_form=ProjectRecord()
    if request.method == 'POST':
	types=request.POST.get('type','').replace(' ','')
	version=request.POST.get('version','').replace(' ','')
	projects=request.POST.get('projects','')
	sql=request.POST.get('sql','')
	comment=request.POST.get('comment','')
	if types not in PROJECT_DICT or version == '' or  projects.replace(' ','') == '' or comment.replace(' ','') == '':
	    return HttpResponse('error')
	else:
	    create_time=datetime.now()
	    record=OnlineDeployModel(type=types,
		    version=version,
		    project=projects,
		    sql_name=sql,
		    create_time=create_time,
		    modify_time=create_time,
		    proposer=request.user.username,
		    publisher='',
		    status='waited',
		    active='Y',
		    comment=comment)
	    try:
		record.save()
	    except Exception as e:
	        return HttpResponse(u'internal_error')
	    return HttpResponse('ok')
    else:
        paginator=Paginator(all_record,7)
        page=request.GET.get('page')
	try:
	    all_record=paginator.page(page)
	except PageNotAnInteger:
	    all_record=paginator.page(1)
	except EmptyPage:
	    all_record=paginator.page(paginator.num_pages)
	return render_to_response('code_deploy.html',RequestContext(request,{'all_record':all_record,'records':record_form,'request':request}))

@login_required(login_url='/')
def get_record_from_id(request):
    if request.method== 'POST':
	record_id=request.POST.get('record_id',0)
    else:
	record_id=request.GET.get('record_id',0)
    if not record_id:
	return HttpResponse(json.dumps({'code':'400','info':u'不存在该记录 !'}))
    record=OnlineDeployModel.objects.get(id=record_id)
    if not record:
	return HttpResponse(json.dumps({'code':'400','info':u'不存在该记录 !'}))
    create_time=datetime.strftime(record.create_time,'%Y-%m-%d %H:%M:%S')
    modify_time=datetime.strftime(record.modify_time,'%Y-%m-%d %H:%M:%S')
    return_record={
	    'type':record.type,
	    'version':record.version,
	    'projects':record.project,
	    'create_time':create_time,
	    'modify_time':modify_time,
	    'proposer':record.proposer,
	    'record_status':record.status,
	    'comment':record.comment,
	    'code':200,
	    }
    if not record.audit_time:
	return_record['audit_time']=''
    else:
        return_record['audit_time']=datetime.strftime(record.audit_time,'%Y-%m-%d %H:%M:%S')
    if not record.publish_time:
	return_record['publish_time']=''
    else:
        return_record['publish_time']=datetime.strftime(record.publish_time,'%Y-%m-%d %H:%M:%S')
    if not record.auditor:
	return_record['auditor']=''
    else:
	return_record['auditor']=record.auditor
    if not record.publisher:
	return_record['publisher']=''
    else:
	return_record['publisher']=record.publisher
    if not record.sql_name:
	return_record['sql']=''
    else:
	return_record['sql']=record.sql_name
    if not record.deploy_status:
	return_record['deploy_status']=''
    else:
	return_record['deploy_status']=record.deploy_status
    return HttpResponse(json.dumps(return_record))

@login_required(login_url='/')
def delete_record_from_id(request):
    if request.method== 'POST':
	record_id=request.POST.get('record_id',0)
    else:
	record_id=request.GET.get('record_id',0)
    if not record_id:
	return HttpResponse(json.dumps({'code':'400','info':u'错误的id !'}))
    record=OnlineDeployModel.objects.get(id=record_id)
    if not record:
	return HttpResponse(json.dumps({'code':'400','info':u'不存在该记录 !'}))
    if record.proposer != request.user.username:
	return HttpResponse(json.dumps({'code':'400','info':u'非申请人无法撤回'}))
    if (record.status == 'waited' and record.active == 'Y') or record.status== 'pass':
	record.status='cancled'
	try:
	    record.save()
	except Exception as e:
	    return HttpResponse(json.dumps({'code':'400','info':u'撤回失败'}))
	return HttpResponse(json.dumps({'code':'200','info':u'撤回成功'}))
    else:
	return HttpResponse(json.dumps({'code':'400','info':u'无法撤回'}))

@login_required(login_url='/')
def modify_record_from_id(request):
    info=''
    code=0
    if request.method == 'POST':
	record_id=request.POST.get('record_id',0);
	types=request.POST.get('type','');
	version=request.POST.get('version','');
	comment=request.POST.get('comment','');
	project=request.POST.get('projects','');
	sql_name=request.POST.get('sql','');
	if not version or not types or not comment or not project or not record_id or types not in PROJECT_DICT:
	    code=400
	    info='bad form data !!'
	else:
	    modify_record=OnlineDeployModel.objects.get(id=record_id)
	    if not modify_record:
		code=400
		info=u'修改失败'
	    elif modify_record.status != 'waited':
		code=400
		info=u'无法修改非待审核的数据'
	    elif modify_record.proposer != request.user.username:
		code=400
		info=u'非申请人无权修改！'
	    else:
		modify_record.type=types
		modify_record.version=version
		modify_record.comment=comment
		modify_record.project=project
		modify_record.sql_name=sql_name
		modify_record.modify_time=datetime.now()
		try:
		    modify_record.save()
		except Exception as e:
		    code=400
		    info=u'修改失败'
		code=200
		info='修改成功'
	return HttpResponse(json.dumps({'code':code,'info':info}))
    else:
	info=u'修改失败'
	return HttpResponse(json.dumps({'code':400,'info':info}))



@login_required(login_url='/')
def audit_record_from_id(request):
    if request.method == 'POST':
	record_id=request.POST.get('record_id',0)
	mark=request.POST.get('mark','')
	record=OnlineDeployModel.objects.get(id=record_id)
	if not record:
	    return HttpResponse(json.dumps({'code':400,'info':u'审核失败,不存在该记录'}))
	if record.status !='waited':
	    return HttpResponse(json.dumps({'code':400,'info':u'审核失败,非待审核状态不允许审核！'}))
        if not request.user.is_superuser:
	    return HttpResponse(json.dumps({'code':400,'info':u'审核失败,非管理员无法审核！'}))
	else:
	    if mark not in ['Y','N']:
		return HttpResponse(json.dumps({'code':400,'info':u'错误的数据格式'}))
	    if mark == 'Y':
		record.status='pass'
	    else:
		record.status='reject'
	    record.audit_time=datetime.now()
	    record.auditor=request.user.username
	    try:
		record.save()
	    except Exception as e:
		return HttpResponse(json.dumps({'code':400,'info':u'审核失败'}))
	    return HttpResponse(json.dumps({'code':200,'info':u'恭喜,审核成功'}))



@login_required(login_url='/')
def deploy_record_from_id(request):
    if request.method=='POST':
	record_id=request.POST.get('record_id',0)
	record=OnlineDeployModel.objects.get(id=record_id)
	if not record:
	    return HttpResponse(json.dumps({'code':400,'info':u'发布失败,无该条记录'}))
	if record.status !='pass':
	    return HttpResponse(json.dumps({'code':400,'info':u'发布失败,非通过审核状态'}))
	project_list=[p.replace(' ','') for p in record.project.split(' ')if p !='']
	Type=record.type.replace(' ','')
	if not dowith_project_params(Type,project_list):
	    return HttpResponse(json.dumps({'code':400,'info':u'错误的申请数据！请修改核对后再发布'}))
	if record.proposer == request.user.username or request.user.is_superuser :
	    record.active='N'
	    flag=False
	    try:
		record.save()
	    except Exception as e:
	        return HttpResponse(json.dumps({'code':400,'info':u'数据库错误'}))
	    try:
		if record.type in ['omp','appportal','ops']:
		    shell_script='/root/deploy/deploy_auto.sh'
		else:
		    shell_script='/root/deploy/deploy_node_auto.sh'
		if not os.path.exists(shell_script):
		    record_new.active='Y'
	            record_new.save()
	            return HttpResponse(json.dumps({'code':400,'info':u'发布脚本不存在'}))
		deploy_cmd=shell_script + ' -t '+record.type+' -p "'+' '.join(project_list)+'" >>' + LOG_FILE
		record.command=deploy_cmd
		record.save()
		cmd_write=''' echo '%s' > /tmp/.tmp.sh ''' %deploy_cmd
		os.system(cmd_write)
		date_str=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		str_cmd='''echo '**************************************************' >> '''+LOG_FILE
		os.system(str_cmd)
		str_cmd=' echo " %s id: %s " >> %s ' %(date_str,record.id,LOG_FILE)
		os.system(str_cmd)
		cmd_print=''' echo '%s' >> %s ''' %(deploy_cmd,LOG_FILE)
		os.system(cmd_print)
		str_cmd=''' echo '**************************************************' >>'''+LOG_FILE
		os.system(str_cmd)
		if record.type in ['appportal','ops']:
		    record_new.active='Y'
	            record_new.save()
	            return HttpResponse(json.dumps({'code':400,'info':u'未开放appportal工程发布'}))
		result=os.system('/bin/bash /tmp/.tmp.sh')
		print result
		if result == 512:
		    record.active='Y'
		    record.save()
	            return HttpResponse(json.dumps({'code':400,'info':u'Sorry,其他用户正在发布,请稍后再试!'}))
		if result == 0:
		    flag=True
		else:
		    flag=False
		record.publish_time=datetime.now()
		record.publisher=request.user.username
	    except Exception as e:
		record.deploy_status='failed'
		print e
	    connection.close()
            record_new=OnlineDeployModel.objects.get(id=record_id)
	    if flag:
		record_new.deploy_status='success'
		record_new.status='published'
		record_new.publish_time=datetime.now()
		record_new.publisher=request.user.username
	    else:
		record_new.deploy_status='failed'
	    record_new.active='Y'
	    record_new.save()
	    return HttpResponse(json.dumps({'code':200,'info':u'恭喜,发布成功'}))
        else:
	    return HttpResponse(json.dumps({'code':400,'info':u'Sorry,无权限'}))

	    





