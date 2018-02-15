from django.shortcuts import render, get_object_or_404, render_to_response

# Create your views here.
#
from django.http import HttpResponse
from catalogue.models import GlobularCluster, Observation, Reference, Profile
import django_tables2 as tables
from django_tables2.utils import A

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import mpld3
import json

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


tblattr = {'class':'display compact', 'id': 'example', 'cellspacing':'0', 'width':"100%"}

class ReferenceTable(tables.Table):
    doi = tables.URLColumn()
    ads = tables.URLColumn()
    name = tables.LinkColumn('ref_detail', args=[A('pk')])
    pub_date = tables.DateColumn()
    class Meta:
        model = Reference
        exclude = ('id',)

class ObservationTable(tables.Table):
    cluster_id = tables.LinkColumn('detail',  args=[A('pk')])
    class Meta:
        model = Observation
        exclude = ('id', 'ref', 'comment', 'status')

class ReferenceTable(tables.Table):
    doi = tables.URLColumn()
    ads = tables.URLColumn()
    name = tables.LinkColumn('ref_detail', args=[A('pk')])
    pub_date = tables.DateColumn()
    class Meta:
        model = Reference
        exclude = ('id',)

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

def landing(request):
    reference =  get_object_or_404(Reference, name__startswith='Harri')
    obj = Observation.objects.filter(ref=reference)
    names = np.array([o.cluster_id.cluster_id for o in obj]    )
    ra =    np.array([o.ra for o in obj]      )
    dec =   np.array([o.dec for o in obj]     )
    l =     np.array([o.gallon for o in obj]  )
    b =     np.array([o.gallat for o in obj]  )
    dist =  np.array([o.dfs for o in obj]     )
    urls = ['GCID'+str(o.pk) for o in obj]
    l[l>180] = l[l>180]-360.

    fig = plt.figure(figsize=(16,8))
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
        print data

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

def about(request):
    return render(request, 'about.html', {})


#from django.template import RequestContext
#from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth import authenticate, logout
#from django.template.loader import get_template
#
#from catalogue.forms import *
#from django.contrib.auth import login as auth_login
#from django.contrib.auth.decorators import login_required
