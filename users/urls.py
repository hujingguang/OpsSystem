from django.conf.urls import url
from views import *


urlpatterns=[
	url(r'^userList/$',list_all_users,name='userList'),
	url(r'^userAdd/$',add_user,name='userAdd'),
	url(r'^changeUser/$',change_user_api,name='changeUser'),
	]
