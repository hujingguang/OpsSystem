from django.shortcuts import render
from deploy.models import RepoModel,DeployInfoModel
from django.http import HttpResponse
import json
def get_project_current_version(request):
    repos=[o.repoName for o in RepoModel.objects.all()]
    ret={}
    for repo in repos:
	try:
	    test_cur_version=DeployInfoModel.objects.filter(repoName=repo).filter(target='test').order_by('-date').first()
	    pre_cur_version=DeployInfoModel.objects.filter(repoName=repo).filter(target='pre').order_by('-date').first()
	    online_cur_version=DeployInfoModel.objects.filter(repoName=repo).filter(target='online').order_by('-date').first()
	    tmp_dict={}
	    if test_cur_version:
		tmp_dict['test']=test_cur_version.revision
	    else:
		tmp_dict['test']='' 
	    if pre_cur_version:
		tmp_dict['pre']=pre_cur_version.revision
	    else:
		tmp_dict['pre']=''
	    if online_cur_version:
		tmp_dict['online']=online_cur_version.revision
	    else:
		tmp_dict['online']=''
	    ret[repo]=tmp_dict
	except Exception as e:
	    ret={'status':'falied','error':'database connect timeout'}
    ret=json.dumps(ret)
    return HttpResponse(ret,content_type='application/json')
    
