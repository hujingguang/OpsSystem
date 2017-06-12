#-*- coding: utf-8 -*-
from django import forms


class DbAuthForm(forms.Form):
    dbuser=forms.CharField(label=u'登陆用户名',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    accesshost=forms.CharField(label=u'登陆主机',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    accessdb=forms.CharField(label=u'数据库名',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    accessauth=forms.CharField(label=u'库权限',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    owner=forms.CharField(label=u'所有者',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    envtype=forms.ChoiceField(label=u'使用环境',choices=(('test',u'测试环境'),('online',u'正式环境')),widget=forms.Select(attrs={'class':'form-control'}))
    useperson=forms.CharField(label=u'使用者',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    comment=forms.CharField(label=u'备注',max_length=100,required=True,widget=forms.Textarea(attrs={'class':'form-control'}))
    createtime=forms.DateTimeField(label='',widget=forms.HiddenInput())

