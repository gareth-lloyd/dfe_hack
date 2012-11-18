import json
from olwidget.widgets import InfoMap

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from schooldata.models import Pupil, County
from schooldata import operations as ops

STANDARD_MAP_OPTIONS = {
    'overlay_style': {
        'fill_color': '#DDDDDD', 
        'fill_opacity': .4,
        'stroke_color': '#AA0000', 
        'stroke_width': 2, 
    },
    'layers': ['google.satellite'],
    'default_lat': '18.520278', 
    'default_lon': '73.856667',
    'zoom_to_data_extent': True,
    'default_zoom': 10,
    'map_div_style': {'width': '100%', 'height': '400px'},
    'hide_textarea': False,
}

def return_json(func):
    def wrapper(*args, **kwargs):
        j_dict = func(*args, **kwargs)
        return HttpResponse(json.dumps(j_dict), content_type="application/json")
    return wrapper

@return_json
def plot_json(request):
    x, y = [], []
    for pupil in Pupil.objects.all()[:1000]:
        x.append(ops.get_deprivation(pupil))
        y.append(pupil.KS4_KS2MAT24P)
    data = zip(x, y)
    print data

    return {
        'data': data
    }

def show_plot(request):
    return render_to_response('dashboard/plot.html', {},
            context_instance=RequestContext(request))

STATS = {
    ops.PredictedAttainment.code: ops.PredictedAttainment,
    ops.PredictedScience.code: ops.PredictedScience,
    ops.SocioEcon.code: ops.SocioEcon,
    ops.FiveAC.code: ops.FiveAC,
    ops.Absentee.code: ops.Absentee,
}

def lea(request, id, stat=None):
    county = get_object_or_404(County, id=id)
    stat = stat or ops.PredictedAttainment.code
    op = STATS[stat](county)
    op.run()

    options = STANDARD_MAP_OPTIONS.copy()
    options['map_div_style'] = {'width': 'auto', 'height': '250px'}
    context = {
        'stats': {code: op.title for code, op in STATS.items()},
        'county': county,
        'op': op,
        'map': InfoMap([[county.shape, {}], ], options)
    }

    return render_to_response(op.template, context,
            context_instance=RequestContext(request))

def leas(request):
    return render_to_response('dashboard/leas.html',
            {'counties': County.objects.all()},
            context_instance=RequestContext(request))
