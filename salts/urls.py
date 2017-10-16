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
	url('^hosts/upload_file$',upload_file,name='upload_file'),
	url('^hosts/code_deploy$',code_deploy,name='code_deploy'),
	url('^hosts/record/info$',get_record_from_id,name='record'),
	url('^hosts/record/delete$',delete_record_from_id,name='record_delete'),
	url('^hosts/record/modify$',modify_record_from_id,name='record_modify'),
	url('^hosts/record/audit$',audit_record_from_id,name='record_audit'),
	url('^hosts/record/deploy$',deploy_record_from_id,name='record_deploy'),
	]

