from django.conf.urls import url,include
from django.contrib import admin
from ops_system.views import index
from ops_system.views import login_view,logout_view,change_password
urlpatterns = [
    url(r'^$',login_view,name='login'),
    url(r'^changePasswd$',change_password,name='changePassword'),
    url(r'^admin/', admin.site.urls),
    url(r'^index/$',index,name='index'),
    url(r'^asset/', include('asset.urls',namespace='asset',app_name='asset')),
    url(r'^deploy-manage/',include('deploy.urls',namespace='deploy-manage',app_name='deploy')),
    url(r'^saltstack/',include('salts.urls',namespace='saltstack',app_name='salts')),
    url(r'^logout/$',logout_view,name='logout'),
    url(r'^api/',include('api.urls',namespace='api',app_name='api')),
    url(r'^user/',include('users.urls',namespace='users',app_name='users')),
    url(r'^auths/',include('auths.urls',namespace='auths',app_name='auths')),
	]



