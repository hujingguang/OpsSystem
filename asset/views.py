from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext


@login_required(login_url='/')
def overview(request):
    return render_to_response('asset_overview.html',RequestContext(request))
    




