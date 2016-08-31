from django.conf.urls import url
from views import * 
urlpatterns=[
	url(r'^add_svn_repo/$',add_svn_repo,name='add_svn_repo'),
	url(r'^add_git_repo/$',add_git_repo,name='add_git_repo'),
	url(r'^list_repo_info/$',list_repo_info,name='list_repo_info'),
	url(r'^list_deploy_info/$',list_deploy_info,name='list_deploy_info'),
	url(r'^deploy_project/$',deploy_project,name='deploy_project'),
	url(r'^rollback_project/$',rollback_project,name='rollback_project')
	]
