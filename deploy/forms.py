# -*- coding: utf-8 -*-
from django import forms
from models import RepoModel


class SvnInfoForm(forms.Form):
    repoName=forms.CharField(error_messages={'required':u'请输入版本库名!'},
	    label=u'版本库名',
	    max_length=20,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control',
		'placeholder':'以英文字符命名'}))
    repoAddress=forms.CharField(error_messages={'required':u'请输入库地址'},
	    label=u'SVN库地址',
	    max_length=40,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'svn://192.168.16.1/repo/trunk'}))
    repoUser=forms.CharField(error_messages={'required':u'请输入库用户'},
	    label=u'库用户名',
	    max_length=20,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    repoPassword=forms.CharField(error_messages={'required':u'请输入密码'},
	    label=u'库密码',
	    max_length=20,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    wwwDir=forms.RegexField(regex=r'^/',
	    error_messages={'required':'请输入网站根目录','invalid':u'无效的路径,必须以/开头'},
	    label=u'网站根目录',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    testDeployIP=forms.RegexField(error_messages={'required':u'请输入测试环境IP地址','invalid':u'不合法的IP地址'},
	    regex=r'^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$',
	    label=u'测试服务器IP',
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    preDeployIP=forms.RegexField(error_messages={'required':u'请输入预生产环境IP地址','invalid':u'不合法的IP地址'},
	    regex=r'^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$',
	    label=u'预生产服务器IP',
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    onlineDeployIP=forms.CharField(error_messages={'required':u'请输入生产环境IP组'},
	    label=u'生产服务器IP组',
	    max_length=100,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'多个IP以空格相隔'}))
    localCheckoutDir=forms.RegexField(regex='^/',
	    error_messages={'required':u'请输入本地checkout目录',
		'invalid':'无效的路径,必须以/开头'},
	    label=u'本地checkout目录',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    excludeDir=forms.CharField(error_messages={'required':u'请输入排除的目录或文件'},
	    label=u'排除更新目录或文件',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'多个文件或目录以分号相隔'}))






class GitInfoForm(forms.Form):
    repoName=forms.CharField(error_messages={'required':u'请输入版本库名!'},
	    label=u'版本库名',
	    max_length=20,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'以英文字符命名'}))
    repoAddress=forms.CharField(error_messages={'required':u'请输入库地址'},label=u'Git库地址',
	    max_length=40,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'git@192.168.1.1:reponame'}))
    wwwDir=forms.RegexField(regex=r'^/',error_messages={'required':'请输入网站根目录','invalid':u'无效的路径,必须以/开头'},
	    label=u'网站根目录',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    testDeployIP=forms.RegexField(error_messages={'required':u'请输入测试环境IP地址','invalid':u'不合法的IP地址'},
	    regex=r'^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$',
	    label=u'测试服务器IP',
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    preDeployIP=forms.RegexField(error_messages={'required':u'请输入预生产环境IP地址',
	'invalid':u'不合法的IP地址'},
	regex=r'^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$',
	label=u'预生产服务器IP',
	required=True,
	widget=forms.TextInput(attrs={'class':'form-control'}))
    onlineDeployIP=forms.CharField(error_messages={'required':u'请输入生产环境IP组'},
	    label=u'生产服务器IP组',
	    max_length=100,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'多个IP以空格相隔'}))
    localCheckoutDir=forms.RegexField(regex='^/',
	    error_messages={'required':u'请输入本地checkout目录',
		'invalid':'无效的路径,必须以/开头'},
	    label=u'本地checkout目录',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control'}))
    excludeDir=forms.CharField(error_messages={'required':u'请输入排除的目录或文件'},
	    label=u'排除更新目录或文件',
	    max_length=50,
	    required=True,
	    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'多个文件或目录以分号相隔'}))


class DeployInputForm(forms.Form):
    target=forms.ChoiceField(label=u'发布环境',
	    choices=(('test',u'测试环境'),('pre',u'预生产环境'),('online',u'生产环境')),
	    widget=forms.Select(attrs={'class':'form-control','style':'width:300px'}))
    repoName=forms.ChoiceField(label=u'项目名称',
	    choices=(),
	    widget=forms.Select(attrs={'class':'form-control','style':'width:300px'}))
    password=forms.CharField(label=u'发布密码',
	    error_messages={'required':u'请输入发布密码!!!'},
	    max_length=100,
	    widget=forms.PasswordInput(attrs={'class':'form-control','style':'width:300px'}))
    def __init__(self,*args,**kwargs):
	super(DeployInputForm,self).__init__(*args,**kwargs)
        self.fields['repoName'].choices=[(ob.repoName,ob.repoName) for ob in RepoModel.objects.all()]



if __name__=='__main__':
    svninfo=SvnInfoForm()
    print(svninfo)



