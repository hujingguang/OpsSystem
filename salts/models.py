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



class OnlineDeployModel(models.Model):
    type=models.CharField(max_length=50)
    version=models.CharField(max_length=50)
    project=models.CharField(max_length=1000)
    sql_name=models.CharField(max_length=1000,null=True)
    create_time=models.DateTimeField()
    modify_time=models.DateTimeField()
    audit_time=models.DateTimeField(null=True)
    publish_time=models.DateTimeField(null=True)
    proposer=models.CharField(max_length=100)
    auditor=models.CharField(max_length=100,null=True)
    publisher=models.CharField(max_length=100,null=True)
    status=models.CharField(max_length=100)
    deploy_status=models.CharField(max_length=20,null=True)
    active=models.CharField(max_length=10)
    comment=models.CharField(max_length=2000)
    command=models.CharField(max_length=1000,null=True)
    class Meta:
	db_table='ops_publish_record'


class DistributeFileRecordModel(models.Model):
    user=models.CharField(max_length=100)
    hostname=models.CharField(max_length=100)
    pattern=models.CharField(max_length=100)
    opttime=models.DateTimeField()
    path=models.CharField(max_length=200)
    filename=models.CharField(max_length=100)
    class Meta:
	db_table='ops_upload_file_record'

    


