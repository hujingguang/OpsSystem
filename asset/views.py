from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import *

@login_required(login_url='/')
def overview(request):
    return render_to_response('asset_overview.html',RequestContext(request))
@login_required(login_url='/')
def query_cmd_log(request):
    form=QueryCmdForm()
    return render_to_response('query_host_cmd_log.html',RequestContext(request,{'form':form}))




