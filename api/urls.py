from django.conf.urls import url
from views import *
urlpatterns=[
        url('^project/version/current/$',get_project_current_version,name='get_procurversion'),
	]
