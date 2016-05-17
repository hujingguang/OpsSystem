from __future__ import unicode_literals

from django.db import models


class HostInfoModel(models.Model):
    hostname=models.CharField(max_length=100)
    ipaddress=models.CharField(max_length=200)
    cpuinfo=models.CharField(max_length=50)
    meminfo=models.CharField(max_length=50)
    group=models.CharField(max_length=50)
    osinfo=models.CharField(max_length=20)
    area=models.CharField(max_length=100)
    usage=models.CharField(max_length=200)
    class Meta:
	db_table='ops_host_info'
	
class AppDeployLogModel(models.Model):
    user=models.CharField(max_length=50)
    time=models.DateTimeField()
    target=models.CharField(max_length=100)
    application=models.CharField(max_length=100)
    mapping=models.CharField(max_length=20)
    success_hosts=models.CharField(max_length=500)
    failed_hosts=models.CharField(max_length=500)
    total=models.IntegerField()
    log=models.TextField()
    duration=models.CharField(max_length=500)
    class Meta:
	db_table='ops_app_deploy_log'

class CmdRunLogModel(models.Model):
    user=models.CharField(max_length=30)
    time=models.DateTimeField()
    target=models.CharField(max_length=100)
    mapping=models.CharField(max_length=50)
    cmd=models.CharField(max_length=500)
    hosts=models.CharField(max_length=500) 
    total=models.IntegerField()
    class Meta:
	db_table='ops_cmd_run_log'
