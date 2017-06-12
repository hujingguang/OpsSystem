from django.conf.urls import url
from views import *

urlpatterns=[
	url('^db/list',db_auth_info_list,name='db_info_list'),
	url('^db/add',db_auth_info_add,name='db_info_add'),
	url('^db/delete',db_auth_info_delete,name='db_info_delete'),
	url('^db/edit',db_auth_info_edit,name='db_info_edit'),
	url('^db/query',db_auth_info_query,name='db_info_query'),
	]
