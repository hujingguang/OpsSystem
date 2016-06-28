# -*- coding: utf-8 -*-

from django import forms 
from models import *
class QueryCmdForm(forms.Form):
    hostname=forms.ChoiceField(label=u'主机名',
	    choices=(),
	    widget=forms.Select(attrs={'class':'form-control','style':'width:300px'}))
    begin_datetime=forms.DateTimeField()
    
    def __init__(self,*arg,**kwargs):
	super(QueryCmdForm,self).__init__(*arg,**kwargs)
	self.fields['hostname'].choices=[(o.hostname,o.hostname) for o in CmdLogModel.objects.values('hostname').distinct()]
