# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import RepoModel
from datetime import datetime
from utils import * 
@login_required(login_url='/')
def add_svn_repo(request):
    if request.method == 'POST':
        form=SvnInfoForm(request.POST)
	if form.is_valid():
	    if RepoModel.objects.filter(repoName=form.cleaned_data['repoName']).count() == 1:
		form.errors['repoName']=u'已经存在该库名！请重新命名'
		return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    svn_is_ok,message=check_svn_validated(user=form.cleaned_data['repoUser'].strip(),
		    password=form.cleaned_data['repoPassword'].strip(),
		    url=form.cleaned_data['repoAddress'].strip())
	    if not svn_is_ok:
		form.errors['repoAddress']=message
		return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    if not check_ip_reachable(form.cleaned_data['testDeployIP']):
		form.errors['testDeployIP']=u'本机无法连接到此 IP: %s ！！！' %form.cleaned_data['testDeployIP']
		return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    if not check_ip_reachable(form.cleaned_data['preDeployIP']):
		form.errors['preDeployIP']=u'本机无法连接到此 IP: %s ！！！' %form.cleaned_data['preDeployIP']
		return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    for ip in form.cleaned_data['onlineDeployIP'].split(' '):
		if ip != '':
		    if not check_ip_reachable(ip):
		        form.errors['onlineDeployIP']=u'本机到IP：%s  无法连通！！！' %ip
		        return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    addDate=datetime.now()
	    repo_dict={}
	    for items in form.cleaned_data:
		repo_dict[items]=form.cleaned_data[items].strip(' ')
	    repoinfo=RepoModel(repoName=repo_dict['repoName'],
		    repoAddress=repo_dict['repoAddress'],
		    repoUser=repo_dict['repoUser'],
		    repoPassword=repo_dict['repoPassword'],
		    wwwDir=repo_dict['wwwDir'],
		    testDeployIP=repo_dict['testDeployIP'],
		    preDeployIP=repo_dict['preDeployIP'],
		    onlineDeployIP=repo_dict['onlineDeployIP'],
		    excludeDir=repo_dict['excludeDir'],
		    repoType='svn',
		    localCheckoutDir=repo_dict['localCheckoutDir'],
		    addDate=addDate)
	    try:
		repoinfo.save()
	    except e:
		return HttpResponse(u'添加库信息失败')
	    return HttpResponseRedirect(reverse('deploy:list_repo_info'))
	return  render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
    form=SvnInfoForm()
    return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))

@login_required(login_url='/')
def add_git_repo(request):
    if request.method == 'POST':
        form=GitInfoForm(request.POST)
	if form.is_valid():
	    if RepoModel.objects.filter(repoName=form.cleaned_data['repoName']).count() == 1:
		form.errors['repoName']=u'已经存在该库名！请重新命名'
		return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
	    git_is_ok,message=check_git_validated(form.cleaned_data['repoAddress'].strip())
	    if not git_is_ok:
		form.errors['repoAddress']=message
		return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
	    if not check_ip_reachable(form.cleaned_data['testDeployIP']):
		form.errors['testDeployIP']=u'本机无法连接到此 IP: %s ！！！' %form.cleaned_data['testDeployIP']
		return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
	    if not check_ip_reachable(form.cleaned_data['preDeployIP']):
		form.errors['preDeployIP']=u'本机无法连接到此 IP: %s ！！！' %form.cleaned_data['preDeployIP']
		return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
	    for ip in form.cleaned_data['onlineDeployIP'].split(' '):
		if ip != '':
		    if not check_ip_reachable(ip):
		        form.errors['onlineDeployIP']=u'本机到IP：%s  无法连通！！！' %ip
		        return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
	    addDate=datetime.now()
	    repo_dict={}
	    for items in form.cleaned_data:
		repo_dict[items]=form.cleaned_data[items].strip(' ')
	    repoinfo=RepoModel(repoName=repo_dict['repoName'],
		    repoAddress=repo_dict['repoAddress'],
		    wwwDir=repo_dict['wwwDir'],
		    testDeployIP=repo_dict['testDeployIP'],
		    preDeployIP=repo_dict['preDeployIP'],
		    onlineDeployIP=repo_dict['onlineDeployIP'],
		    excludeDir=repo_dict['excludeDir'],
		    repoType='git',
		    localCheckoutDir=repo_dict['localCheckoutDir'],
		    addDate=addDate)
	    try:
		repoinfo.save()
	    except e:
		return HttpResponse(u'添加库信息失败')
	    return HttpResponseRedirect(reverse('deploy:list_repo_info'))
	return  render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))
    form=GitInfoForm()
    return render_to_response('add_git_repo.html',RequestContext(request,{'form':form}))

@login_required(login_url='/')
def list_repo_info(request):
    repos_list=RepoModel.objects.all()
    return render_to_response('list_repo_info.html',RequestContext(request,{'repos_list':repos_list}))


@login_required(login_url='/')
def list_deploy_info(request):
    deploy_list=DeployInfoModel.objects.all().order_by('-date')
    for d in deploy_list:
	d.date=datetime.strftime(d.date,'%Y-%m-%d %H:%M:%S')
    paginator=Paginator(deploy_list,10)
    page=request.GET.get('page')
    try:
	deploy=paginator.page(page)
    except PageNotAnInteger:
	deploy=paginator.page(1)
    except EmptyPage:
	deploy=paginator.page(paginator.num_pages)
    return render_to_response('list_deploy_info.html',RequestContext(request,{'deploy_list':deploy}))

@login_required(login_url='/')
def deploy_project(request):
    if request.method=='POST':
	form=DeployInputForm(request.POST)
	if form.is_valid():
	    repoName=form.cleaned_data['repoName']
	    password=form.cleaned_data['password']
	    target=form.cleaned_data['target']
	    repoinfo=RepoModel.objects.get(repoName=repoName.strip())
	    if target== u'test':
		ip=repoinfo.testDeployIP.strip()
	    elif target== u'pre':
		ip=repoinfo.preDeployIP.strip()
	    else:
		ip=repoinfo.onlineDeployIP.strip()
	    if target != 'online':
	        if not check_ssh_passwd(password,ip):
		    form.errors['password']=u'发布密码错误！！！！'
		    return render_to_response('deploy_project.html',RequestContext(request,{'form':form}))
	    deploy_person=request.user
	    res,mess,log_file=deploy_project_func(repoName,password,target,deploy_person)
	    print repoName,password,target,deploy_person
	    log=[]
	    if log_file is not None:
		#f=open(log_file,'r')
		#log=f.readlines()
		#f.close()
		cmd='cat %s' %log_file
		r,log=commands.getstatusoutput(cmd)
		os.system('rm -f %s' %log_file)
	    if res:
		form.errors['password']=mess
		return render_to_response('deploy_project.html',RequestContext(request,{'form':form,'log':log,'res':res}))
	    else:
		form.errors['password']=mess
		return render_to_response('deploy_project.html',RequestContext(request,{'form':form,'log':log,'res':res}))
        return render_to_response('deploy_project.html',RequestContext(request,{'form':form}))
    form=DeployInputForm()
    return render_to_response('deploy_project.html',RequestContext(request,{'form':form}))
