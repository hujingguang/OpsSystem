#-*- coding: utf-8 -*-
from django import forms
Choice=(('list','List'),('grain','Grain'),('pcre','Regex'),('glob','Hostname'),('nodegroup','NodeGroup'))
class CmdInputForm(forms.Form):
    target=forms.CharField(error_messages={'required':u'请输入目标主机！'},label=u'Target',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
    mapping=forms.ChoiceField(required=True,choices=(('list','List'),('grain','Grain'),('pcre','Regex'),('glob','Hostname'),('nodegroup','NodeGroup')),widget=forms.RadioSelect(attrs={'checked':None}))
    cmdline=forms.CharField(error_messages={'required':u'请输入命令！'},label=u'Command',max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control'}))
