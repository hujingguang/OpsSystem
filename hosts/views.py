from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import json
# Create your views here.
@login_required(login_url='/')
def host_list(request):
    minion_status_dict={'accept_num':12,'reject_num':123,'unaccept_num':12}
    res=json.dumps(minion_status_dict)
    return render_to_response('host_list.html',RequestContext(request,{'nums':res}))
