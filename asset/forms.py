# -*- coding: utf-8 -*-

from django import forms 
from models import *
class QueryCmdForm(forms.Form):
    hostname=forms.ChoiceField(label=u'主机名',
	    choices=(),
	    widget=forms.Select(attrs={'class':'form-control','style':'width:370px'}))
    begin=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class':'form-control','style':'width:340px','readonly':True}))
    end=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class':'form-control','style':'width:340px','readonly':True}))
    
    def __init__(self,*arg,**kwargs):
	super(QueryCmdForm,self).__init__(*arg,**kwargs)
	sql='select id,hostname from ops_cmd_opt_log GROUP BY hostname'
	self.fields['hostname'].choices=[(o.hostname,o.hostname) for o in CmdLogModel.objects.raw(sql)]
