from django.conf.urls import url
from views import *


urlpatterns=[url('^asset/overview$',overview,name='overview'),
	]
