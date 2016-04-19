# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from forms import *
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
	    print '----------------'
	    svn_is_ok,message=check_svn_validated(user=form.cleaned_data['repoUser'].strip(),password=form.cleaned_data['repoPassword'].strip(),url=form.cleaned_data['repoAddress'].strip())
	    if not svn_is_ok:
		form.errors['repoAddress']=message
		return render_to_response('add_svn_repo.html',RequestContext(request,{'form':form}))
	    addDate=datetime.now()
	    repo_dict={}
	    for items in form.cleaned_data:
		repo_dict[items]=form.cleaned_data[items].strip(' ')
	    repoinfo=RepoModel(repoName=repo_dict['repoName'],repoAddress=repo_dict['repoAddress'],repoUser=repo_dict['repoUser'],repoPassword=repo_dict['repoPassword'],wwwDir=repo_dict['wwwDir'],testDeployIP=repo_dict['testDeployIP'],preDeployIP=repo_dict['preDeployIP'],onlineDeployIP=repo_dict['onlineDeployIP'],excludeDir=repo_dict['excludeDir'],repoType='svn',localCheckoutDir=repo_dict['localCheckoutDir'],addDate=addDate)
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
	    addDate=datetime.now()
	    repo_dict={}
	    for items in form.cleaned_data:
		repo_dict[items]=form.cleaned_data[items].strip(' ')
	    repoinfo=RepoModel(repoName=repo_dict['repoName'],repoAddress=repo_dict['repoAddress'],wwwDir=repo_dict['wwwDir'],testDeployIP=repo_dict['testDeployIP'],preDeployIP=repo_dict['preDeployIP'],onlineDeployIP=repo_dict['onlineDeployIP'],excludeDir=repo_dict['excludeDir'],repoType='git',localCheckoutDir=repo_dict['localCheckoutDir'],addDate=addDate)
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
def deploy_project(request):
    form=DeployInputForm()
    return render_to_response('deploy_project.html',RequestContext(request,{'form':form}))
