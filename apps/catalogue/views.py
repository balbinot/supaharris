import json

import numpy as np
import pandas as pd
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
from bs4 import BeautifulSoup

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

import django_tables2 as tables
from django_tables2.utils import A
from django_pandas.io import read_frame

from catalogue.models import Reference
from catalogue.models import Observation
from catalogue.models import GlobularCluster


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
        exclude = ('name', 'val', 'sigup', 'sigdown', 'id', 'name')


def obsummary(request):
    # Queryset should take some info from request to filter for reference and
    # parameters.
    r = Reference.objects.filter(name='Harris')
    obj = Observation.objects.values('name', 'pname', 'val', 'sigup', 'sigdown').order_by()
    pd.options.display.max_rows = 300
    t = read_frame(obj)
    vals = t.groupby(['name', 'pname']).first().unstack()['val']
    sup = t.groupby(['name', 'pname']).first().unstack()['sigup']
    sdown = t.groupby(['name', 'pname']).first().unstack()['sigdown']

    # Table built column by column with model property as redering assessor.
    #table = ObservationTable(obj, attrs=tblattr, orderable=True)

    table = vals.fillna('--').to_html()
    soup = BeautifulSoup(table, "html.parser")
    soup.find('table')['id'] = 'example'
    for row in soup.findAll('table')[0].tbody.findAll('tr'):
        first_column = row.findAll('th')[0].contents
        row.findAll('th')[0] = '<a href={}>{}</a>'.format(first_column, first_column)

    return render(request, 'test.html', {'observations': soup})


def method(request, name):
    odict = {}

    ## Table with pars
    cl = GlobularCluster.objects.filter(name__contains=name)[0]
    query = Observation.objects.filter(name=cl).query
    query.group_by = ['name']
    obs = QuerySet(query=query, model=Observation).order_by('pname')

    obj = ObservationTable(obs)
    odict['observations'] = obj
    odict['cluster'] = cl

    # Profile plot
    data = Profile.objects.filter(name=cl)
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

def index(request):
    reference =  get_object_or_404(Reference, name__startswith='Harri')
    obj = Observation.objects.filter(ref=reference)
    table = ObservationTable(obj, attrs=tblattr, orderable=False)
    return render(request, 'index.html', {'observations': table, 'reference': reference})


def cluster_detail(request, name):
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


class ReferenceTable(tables.Table):
    doi = tables.URLColumn()
    ads_url = tables.URLColumn()
    name = tables.LinkColumn('ref_detail', args=[A('pk')])
    pub_date = tables.DateColumn()
    class Meta:
        model = Reference
        exclude = ('id',)


def reference_list(request):
    table = ReferenceTable(Reference.objects.all(), attrs=tblattr, orderable=False)
    return render(request, 'catalogue/reference_list.html', {'references': table})


class GeneralTable(tables.Table):
    class Meta:
        model = Observation
        exclude = ('id', 'ref')

def ref_detail(request, name_id):
    reference = get_object_or_404(Reference, pk=name_id)
    table = GeneralTable(Observation.objects.filter(ref=reference), orderable=False, attrs=tblattr)
    return render(request, 'ref_detail.html', {'references': table, 'reference' : reference})


def reference_detail(request, slug):
    reference = get_object_or_404(Reference, slug=slug)
    return render(request, 'catalogue/reference_detail.html',
        {"reference": reference})


def cluster_list(request):
    all_clusters = GlobularCluster.objects.all()
    return render(request, 'catalogue/cluster_list.html',
        {"all_clusters": all_clusters})


def cluster_detail(request, slug):
    globular_cluster = get_object_or_404(GlobularCluster, slug=slug)
    return render(request, 'catalogue/cluster_list.html',
        {"globular_cluster": globular_cluster})
