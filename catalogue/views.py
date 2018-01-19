from django.shortcuts import render, get_object_or_404, render_to_response

# Create your views here.

from django.http import HttpResponse
from catalogue.models import GlobularCluster, Observation, Reference
import django_tables2 as tables
from django_tables2.utils import A

tblattr = {'class':'table table-striped'}

## Move this to a tables.py file
class ObservationTable(tables.Table):
    class Meta:
        model = Observation
        exclude = ('id', 'cluster_id')

def index(request):
    table = ObservationTable(Observation.objects.all(), attrs=tblattr)
    return render(request, 'index.html', {'observations': table})


#from django.template import RequestContext
#from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth import authenticate, logout
#from django.template.loader import get_template
#
#from catalogue.forms import *
#from django.contrib.auth import login as auth_login
#from django.contrib.auth.decorators import login_required
