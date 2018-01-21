from django.shortcuts import render, get_object_or_404, render_to_response

# Create your views here.

from django.http import HttpResponse
from catalogue.models import GlobularCluster, Observation, Reference
import django_tables2 as tables
from django_tables2.utils import A

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import mpld3
import json

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



tblattr = {'class':'display', 'id': 'example'}

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

def index(request):
    reference =  get_object_or_404(Reference, name__startswith='Harri')
    obj = Observation.objects.filter(ref=reference)
    table = ObservationTable(obj, attrs=tblattr)
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

    points = ax.scatter(l, b, c=dist, s=100, alpha=0.5, cmap=plt.cm.jet)
    ax.grid(color='white', linestyle='solid')
    ax.set_title("Globular clusters", size=20)
    ax.set_xlabel('l [deg]', size=20)
    ax.set_ylabel('b [deg]', size=20)

    mpld3.plugins.connect(fig, ClickInfo(points, urls))

    tooltip = mpld3.plugins.PointLabelTooltip(points, labels=names)
    mpld3.plugins.connect(fig, tooltip)

    #single_chart = dict()
    #single_chart['id'] = "fig_01"
    #single_chart['json'] = json.dumps(mpld3.fig_to_dict(fig))
    #result= {'single_chart': single_chart}
    result = mpld3.fig_to_html(fig)

    return render(request, 'landing.html', {'figure': result})

def detail(request, cid):
    cluster = get_object_or_404(GlobularCluster, pk=cid)
    table = ObservationTable(Observation.objects.filter(cluster_id=cluster))


    return render(request, 'detail.html', {'observations': table, 'cluster' : cluster})


#from django.template import RequestContext
#from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth import authenticate, logout
#from django.template.loader import get_template
#
#from catalogue.forms import *
#from django.contrib.auth import login as auth_login
#from django.contrib.auth.decorators import login_required
