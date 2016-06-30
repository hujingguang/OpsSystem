from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import *
from models import *
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect 
from django.core.urlresolvers import reverse
Host=None
Begin=None
End=None


@login_required(login_url='/')
def overview(request):
    return render_to_response('asset_overview.html',RequestContext(request))
@login_required(login_url='/')
def query_cmd_log(request):
    global Host,Begin,End
    form=QueryCmdForm()
    if request.method == 'POST':
	form=QueryCmdForm(request.POST)
	if form.is_valid():
	    Host=form.cleaned_data['hostname']
	    Begin=datetime.strftime(form.cleaned_data['begin'],'%Y-%m-%d %H:%M:%S')
	    End=datetime.strftime(form.cleaned_data['end'],'%Y-%m-%d %H:%M:%S')
	    return HttpResponseRedirect(reverse('asset:list_cmd_opt_log')) 
    return render_to_response('query_host_cmd_log.html',RequestContext(request,{'form':form}))
@login_required(login_url='/')
def list_cmd_opt_log(request):
    global Host,Begin,End
    if not Host or not Begin or not End:
	return HttpResponseRedirect(reverse('asset:query_cmd_log')) 
    query_set=CmdLogModel.objects.filter(hostname=Host).filter(runtime__range=(Begin,End))
    for q in query_set:
	q.runtime=datetime.strftime(q.runtime,'%Y-%m-%d %H:%M:%S')
    paginator=Paginator(query_set,100)
    page=request.GET.get('page')
    try:
	query=paginator.page(page)
    except PageNotAnInteger:
	query=paginator.page(1)
    except EmptyPage:
	query=paginator.page(paginator.num_pages)
    return render_to_response('list_cmd_opt_log.html',RequestContext(request,{'cmd_set':query}))
    



