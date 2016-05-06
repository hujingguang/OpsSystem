from django.conf.urls import url,include
from django.contrib import admin
from ops_system.views import index
from ops_system.views import login_view,logout_view
urlpatterns = [
    url(r'^$',login_view,name='login'),
    url(r'^admin/', admin.site.urls),
    url(r'^index/$',index,name='index'),
    url(r'^host-manage/', include('hosts.urls',namespace='host-manage',app_name='hosts')),
    url(r'^deploy-manage/',include('deploy.urls',namespace='deploy-manage',app_name='deploy')),
    url(r'^saltstack/',include('salts.urls',namespace='saltstack',app_name='salt')),
    url(r'^logout/$',logout_view,name='logout'),
	]



