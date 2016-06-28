from __future__ import unicode_literals

from django.db import models

# Create your models here.

class CmdLogModel(models.Model):
    hostname=models.CharField(max_length=100)
    user=models.CharField(max_length=100)
    command=models.CharField(max_length=2000)
    login_ip=models.CharField(max_length=20)
    runtime=models.DateTimeField()
    
    class Meta:
	db_table='ops_cmd_opt_log'

