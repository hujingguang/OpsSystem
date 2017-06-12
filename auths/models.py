from __future__ import unicode_literals

from django.db import models


class DatabaseAuthInfoModel(models.Model):
    username=models.CharField(max_length=50)
    accesshost=models.CharField(max_length=100)
    accessdb=models.CharField(max_length=100)
    accessauth=models.CharField(max_length=200)
    owner=models.CharField(max_length=20)
    useperson=models.CharField(max_length=100)
    envtype=models.CharField(max_length=20)
    createtime=models.DateTimeField()
    comment=models.CharField(max_length=1000)
    class Meta:
	db_table='ops_db_auth_info'


class CodeRepoAuthInfoModel(models.Model):
    username=models.CharField(max_length=50)
    reponame=models.CharField(max_length=50)
    accessauth=models.CharField(max_length=100)
    envtype=models.CharField(max_length=20)
    createtime=models.DateTimeField()
    comment=models.CharField(max_length=200)
    repotype=models.CharField(max_length=10)
    class Meta:
	db_table='ops_repo_auth_info'



