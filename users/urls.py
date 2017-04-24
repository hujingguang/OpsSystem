from django.conf.urls import url
from views import *


urlpatterns=[
	url(r'^userList/$',list_all_users,name='userList'),
	]
