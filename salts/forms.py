#-*- coding: utf-8 -*-
from django import forms
Choice=(('list','List'),('grain','Grain'),('pcre','Regex'),('nodegroup','NodeGroup'),('glob','Hostname'))
class CmdInputForm(forms.Form):
    target=forms.CharField(error_messages={'required':u'请输入目标主机！'},
	    label=u'Target',
	    max_length=100,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    mapping=forms.ChoiceField(required=True,
	    choices=(('list','List'),('grain','Grain'),('pcre','Regex'),('nodegroup','NodeGroup'),('glob','Hostname')),
	    widget=forms.RadioSelect(attrs={'checked':None}))
    cmdline=forms.CharField(error_messages={'required':u'请输入命令！'},
	    label=u'Command',
	    max_length=1000,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
class DownloadFileForm(forms.Form):
    target=forms.CharField(error_messages={'required':u'请输入目标主机！'},
	    label=u'Target',
	    max_length=100,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    file_path=forms.RegexField(regex=r'^/',
	    error_messages={'required':u'请输入文件绝对路径！','invalid':u'无效的路径，必须以/开头'},
	    label=u'FilePath',
	    max_length=1000,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
