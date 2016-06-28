from django.conf.urls import url
from views import *


urlpatterns=[url('^asset/overview$',overview,name='overview'),
	url('^asset/query_cmd_log$',query_cmd_log,name='query_cmd_log'),
	]
