from django.conf.urls import url
from views import *


urlpatterns=[
	url('^hosts/host_info$',list_host_info,name='host_info'),
	url('^hosts/deploy/application$',deploy_application,name='deploy'),
	url('^hosts/refresh_host_info$',refresh_host_info,name='refresh_host_info'),
	url('^hosts/list_app_deploy_info$',list_app_deploy_info,name='list_app_deploy_info'),
	url('^hosts/list_cmd_run_info$',list_cmd_run_info,name='list_cmd_run_info'),
	url('^hosts/cmd_run$',cmd_run,name='cmd_run'),
	url('^hosts/download_file$',download_file,name='download_file'),
	]

