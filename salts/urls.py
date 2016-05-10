from django.conf.urls import url
from views import *


urlpatterns=[
	url('^hosts/host_info$',list_host_info,name='host_info'),
	url('^hosts/deploy/application$',deploy_application,name='deploy'),
	url('^hosts/refresh_host_info$',refresh_host_info,name='refresh_host_info'),
	]

