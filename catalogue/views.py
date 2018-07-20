from django.shortcuts import render, get_object_or_404, render_to_response

# Create your views here.
#
from django.http import HttpResponse
from catalogue.models import *
import django_tables2 as tables
from django_tables2.utils import A
from django_pandas.io import read_frame
from bs4 import BeautifulSoup
from django.db.models import QuerySet

import numpy as np
import pandas as pd
import json

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import mpld3
#mpld3 hack
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
from mpld3 import _display
_display.NumpyEncoder = NumpyEncoder


css = """
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family:Arial, Helvetica, sans-serif;
  border: 1px solid black;
  text-align: right;
}
"""

class ClickInfo(mpld3.plugins.PluginBase):
    """mpld3 Plugin for getting info on click        """

    JAVASCRIPT = """
    mpld3.register_plugin("clickinfo", ClickInfo);
    ClickInfo.prototype = Object.create(mpld3.Plugin.prototype);
    ClickInfo.prototype.constructor = ClickInfo;
    ClickInfo.prototype.requiredProps = ["id", "urls"];
    function ClickInfo(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    ClickInfo.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id);
        urls = this.props.urls;
        obj.elements().on("mousedown",
                          function(d, i){
                            window.open(urls[i], '_blank')});
    }
    """
    def __init__(self, points, urls):
        self.points = points
        self.urls = urls
        if isinstance(points, matplotlib.lines.Line2D):
            suffix = "pts"
        else:
            suffix = None
        self.dict_ = {"type": "clickinfo",
                      "id": mpld3.utils.get_id(points, suffix),
                      "urls": urls}




tblattr = {'class':'display compact', 'id': 'example', 'cellspacing':'0',
           'width':"100%"}


class ObservationTable(tables.Table):
    pname = tables.Column('pname', attrs={'td': {'style': 'font-weight:bold'}})
    quantity = tables.Column(accessor='render_val', verbose_name='Value')
    def render_pname(self, value):
        return '%s' % value
    class Meta:
        model = Observation
        attrs = tblattr
        attrs = {'class':'display', 'id': 'example', 'cellspacing':'0',
                 'width':"30%"}
        sequence = ('pname', 'quantity') # fields to display
        exclude = ('rname', 'val', 'sigup', 'sigdown', 'id', 'cname')

class ReferenceTable(tables.Table):
    doi = tables.URLColumn()
    ads = tables.URLColumn()
    name = tables.LinkColumn('ref_detail', args=[A('pk')])
    pub_date = tables.DateColumn()
    class Meta:
        model = Reference
        exclude = ('id',)


def obsummary(request):
    # Queryset should take some info from request to filter for reference and
    # parameters.
    r = Reference.objects.filter(rname='Harris')
    obj = Observation.objects.values('cname', 'pname', 'val', 'sigup', 'sigdown').order_by()
    pd.options.display.max_rows = 300
    t = read_frame(obj)
    vals = t.groupby(['cname', 'pname']).first().unstack()['val']
    sup = t.groupby(['cname', 'pname']).first().unstack()['sigup']
    sdown = t.groupby(['cname', 'pname']).first().unstack()['sigdown']

    # Table built column by column with model property as redering assessor.
    #table = ObservationTable(obj, attrs=tblattr, orderable=True)

    table = vals.fillna('--').to_html()
    soup = BeautifulSoup(table, "html.parser")
    soup.find('table')['id'] = 'example'
    for row in soup.findAll('table')[0].tbody.findAll('tr'):
        first_column = row.findAll('th')[0].contents
        row.findAll('th')[0] = '<a href={}>{}</a>'.format(first_column, first_column)

    return render(request, 'test.html', {'observations': soup})

def clsummary(request, cname):

    odict = {}

    ## Table with pars
    cl = GlobularCluster.objects.filter(cname__contains=cname)[0]
    query = Observation.objects.filter(cname=cl).query
    query.group_by = ['rname']
    obs = QuerySet(query=query, model=Observation).order_by('pname')

    obj = ObservationTable(obs)
    odict['observations'] = obj
    odict['cluster'] = cl

    # Profile plot
    data = Profile.objects.filter(cname=cl)
    if len(data) > 0:
        data = json.loads(data[0].profile)
        fig = plt.figure(1, figsize=(7,7))
        fig.clf()
        ax = plt.subplot(111)

        points = ax.scatter(data['log(r/arcmin)'], data['mu_V'], c='k', s=50,
                            alpha=0.5, cmap=plt.cm.jet)
        ax.grid(color='white', linestyle='solid')
        ax.set_title("Surface brightness profile", size=20)
        ax.set_xlabel('log(r/arcmin)', size=20)
        ax.set_ylabel('muV', size=20)
        ax.invert_yaxis()

        tooltip = mpld3.plugins.PointLabelTooltip(points, labels=data['label'])
        mpld3.plugins.connect(fig, tooltip)
        odict['figure']  = mpld3.fig_to_html(fig)

    else:
        odict['figure']  = "<center><h3>No profile available</h3></center>"



    esaurl = "http://sky.esa.int/?action=goto&target={}%20{}&hips=DSS2%20color&fov=0.50&cooframe=J2000".format(obs.filter(pname='RA')[0].val, obs.filter(pname='Dec')[0].val)
    odict['esaurl'] = esaurl

    return render(request, 'detail.html', odict)

def references(request):
    table = ReferenceTable(Reference.objects.all(), attrs=tblattr, orderable=False)
    return render(request, 'references.html', {'references': table})

def landing(request):
    reference =  get_object_or_404(Reference, rname__startswith='Harri')
    obj = Observation.objects.filter(rname=reference)
    cs = GlobularCluster.objects.all()
    obj = [Observation.objects.filter(rname=reference, cname=c) for c in cs]
    names = np.array([o.cname for o in cs]    )
    ra =    np.array([o.filter(pname='RA')[0].val for o in obj]      )
    dec =    np.array([o.filter(pname='Dec')[0].val for o in obj]      )
    l =    np.array([o.filter(pname='L')[0].val for o in obj]      )
    b =    np.array([o.filter(pname='B')[0].val for o in obj]      )
    ra =    np.array([o.filter(pname='RA')[0].val for o in obj]      )
    ra =    np.array([o.filter(pname='RA')[0].val for o in obj]      )
    urls = ['cluster/'+o.cname for o in cs]
    l[l>180] = l[l>180]-360.

    fig = plt.figure(2, figsize=(16,8))
    ax = plt.subplot(111)

    points = ax.scatter(l, b, c='r', s=100, alpha=0.5, cmap=plt.cm.jet)
    ax.grid(color='white', linestyle='solid')
    ax.set_title("Globular clusters", size=20)
    ax.set_xlabel('l [deg]', size=20)
    ax.set_ylabel('b [deg]', size=20)

    mpld3.plugins.connect(fig, ClickInfo(points, urls))

    labels = ['<table><tr>{}<td></tr></td>'.format(n) for n in names]
    tooltip = mpld3.plugins.PointHTMLTooltip(points, labels=labels, css=css)
    mpld3.plugins.connect(fig, tooltip)

    result = mpld3.fig_to_html(fig)

    return render(request, 'landing.html', {'figure': result})

def about(request):
    return render(request, 'about.html', {})





class ReferenceTable(tables.Table):
    doi = tables.URLColumn()
    ads = tables.URLColumn()
    name = tables.LinkColumn('ref_detail', args=[A('pk')])
    pub_date = tables.DateColumn()
    class Meta:
        model = Reference
        exclude = ('id',)

#class ObservationTable(tables.Table):
#    cluster_id = tables.LinkColumn('detail',  args=[A('pk')])
#    class Meta:
#        model = Observation
#        exclude = ('id', 'ref', 'comment', 'status')


class GeneralTable(tables.Table):
    class Meta:
        model = Observation
        exclude = ('id', 'ref')

def references(request):
    table = ReferenceTable(Reference.objects.all(), attrs=tblattr, orderable=False)
    return render(request, 'references.html', {'references': table})

def ref_detail(request, name_id):
    reference = get_object_or_404(Reference, pk=name_id)
    table = GeneralTable(Observation.objects.filter(ref=reference), orderable=False, attrs=tblattr)
    return render(request, 'ref_detail.html', {'references': table, 'reference' : reference})

def index(request):
    reference =  get_object_or_404(Reference, name__startswith='Harri')
    obj = Observation.objects.filter(ref=reference)
    table = ObservationTable(obj, attrs=tblattr, orderable=False)
    return render(request, 'index.html', {'observations': table, 'reference': reference})


def detail(request, cid):
    cluster = get_object_or_404(GlobularCluster, pk=cid)
    table = ObservationTable(Observation.objects.filter(cluster_id=cluster), orderable=False, attrs=tblattr)
    data = Profile.objects.filter(cluster_id=cluster)
    odict = {}
    odict['observations'] = table
    odict['cluster'] = cluster
    if len(data) > 0:
        data = data[0]
        data = json.loads(data.profile)

        fig = plt.figure(figsize=(7,7))
        ax = plt.subplot(111)

        points = ax.scatter(data['log(r/arcmin)'], data['mu_V'], c='k', s=50,
                            alpha=0.5, cmap=plt.cm.jet)
        ax.grid(color='white', linestyle='solid')
        ax.set_title("Surface brightness profile", size=20)
        ax.set_xlabel('log(r/arcmin)', size=20)
        ax.set_ylabel('muV', size=20)
        ax.invert_yaxis()

        tooltip = mpld3.plugins.PointLabelTooltip(points, labels=data['label'])
        mpld3.plugins.connect(fig, tooltip)
        odict['figure']  = mpld3.fig_to_html(fig)

    else:
        odict['figure']  = "<center><h3>No profile available</h3></center>"

    return render(request, 'detail.html', odict)



#from django.template import RequestContext
#from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth import authenticate, logout
#from django.template.loader import get_template
#
#from catalogue.forms import *
#from django.contrib.auth import login as auth_login
#from django.contrib.auth.decorators import login_required
