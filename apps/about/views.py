from django.shortcuts import render

def index(request):
#     reference =  get_object_or_404(Reference, name__startswith="Harri")
#     obj = Observation.objects.filter(name=reference)
#     cs = GlobularCluster.objects.all()
#     obj = [Observation.objects.filter(name=reference, name=c) for c in cs]
#     names = np.array([o.name for o in cs]    )
#     ra =    np.array([o.filter(pname="RA")[0].val for o in obj]      )
#     dec =    np.array([o.filter(pname="Dec")[0].val for o in obj]      )
#     l =    np.array([o.filter(pname="L")[0].val for o in obj]      )
#     b =    np.array([o.filter(pname="B")[0].val for o in obj]      )
#     ra =    np.array([o.filter(pname="RA")[0].val for o in obj]      )
#     ra =    np.array([o.filter(pname="RA")[0].val for o in obj]      )
#     urls = ["cluster/"+o.name for o in cs]
#     l[l>180] = l[l>180]-360.
#
#     fig = plt.figure(2, figsize=(16,8))
#     ax = plt.subplot(111)
#
#     points = ax.scatter(l, b, c="r", s=100, alpha=0.5, cmap=plt.cm.jet)
#     ax.grid(color="white", linestyle="solid")
#     ax.set_title("Globular clusters", size=20)
#     ax.set_xlabel("l [deg]", size=20)
#     ax.set_ylabel("b [deg]", size=20)
#
#     mpld3.plugins.connect(fig, ClickInfo(points, urls))
#
#     labels = ["<table><tr>{}<td></tr></td>".format(n) for n in names]
#     tooltip = mpld3.plugins.PointHTMLTooltip(points, labels=labels, css=css)
#     mpld3.plugins.connect(fig, tooltip)
#
#     result = mpld3.fig_to_html(fig)
#
    result = None
    return render(request, "about/index.html", {"figure": result})

def info(request):
    return render(request, "about/info.html", {})

def privacy_policy(request):
    return render(request, "about/privacy_policy.html", {})
