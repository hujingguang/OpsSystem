from __future__ import unicode_literals

from django.db import models


class RepoModel(models.Model):
    repo_type_choice=(('svn','svn repo type'),('git','git repo type'))
    repoName=models.CharField(max_length=100)
    repoAddress=models.CharField(max_length=100)
    repoUser=models.CharField(max_length=50,blank=False)
    repoPassword=models.CharField(max_length=50,blank=True)
    wwwDir=models.CharField(max_length=50)
    testDeployIP=models.CharField(max_length=50)
    preDeployIP=models.CharField(max_length=50)
    onlineDeployIP=models.CharField(max_length=500)
    localCheckoutDir=models.CharField(max_length=100)
    excludeDir=models.CharField(max_length=500)
    repoType=models.CharField(max_length=5,choices=repo_type_choice)
    addDate=models.DateTimeField()
    class Meta:
	db_table='ops_repo_info'

class DeployInfoModel(models.Model):
    repoName=models.CharField(max_length=100)
    target=models.CharField(max_length=10)
    revision=models.CharField(max_length=100)
    person=models.CharField(max_length=50)
    date=models.DateTimeField()
    log=models.TextField()
    class Meta:
	db_table='ops_deploy_info'
