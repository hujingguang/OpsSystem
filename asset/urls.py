from django.conf.urls import url
from views import *


urlpatterns=[url('^asset/overview$',overview,name='overview'),
	url('^asset/query_cmd_log$',query_cmd_log,name='query_cmd_log'),
	url('^asset/list_cmd_opt_log$',list_cmd_opt_log,name='list_cmd_opt_log'),
	]
