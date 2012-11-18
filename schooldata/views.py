import json
from olwidget.widgets import Map, InfoLayer

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from schooldata.util import paged
from schooldata.models import Pupil, County
from schooldata import operations as ops

COUNTY_OPTIONS = {
    'overlay_style': {
        'fill_color': '#FFFFFF',
        'fill_opacity': .3,
        'stroke_color': '#000000',
        'stroke_opacity': .8,
        'stroke_width': 2,
    },
}
BEST_OPTIONS = {
    'overlay_style': {
        'stroke_color': '#00AA00',
        'fill_color': '#00AA00',
        'point_radius': 4,
    },
}
WORST_OPTIONS = {
    'overlay_style': {
        'stroke_color': '#AA0000',
        'fill_color': '#AA0000',
        'point_radius': 4,
    },
}
MAP_OPTIONS = {
    'layers': ['google.satellite'],
    'zoom_to_data_extent': True,
    'map_div_style': {'width': 'auto', 'height': '300px'},
    'hide_textarea': False,
}
LEAS_MAP_OPTIONS = {
    'overlay_style': {
        'fill_color': '#FFFFFF',
        'fill_opacity': .3,
        'stroke_color': '#000000',
        'stroke_opacity': .6,
        'stroke_width': 1,
    },
    'layers': ['google.physical'],
    'zoom_to_data_extent': False,
    'default_zoom': 6,
    'default_lon': -2.5,
    'default_lat': 54,
    'map_div_style': {'width': 'auto', 'height': '500px'},
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
    ops.MathsProgress.code: ops.MathsProgress,
    ops.EnglishProgress.code: ops.EnglishProgress,
}

def lea(request, id=None, stat=None):
    county = get_object_or_404(County, id=id)
    stat = stat or ops.PredictedAttainment.code
    op = STATS[stat](county)
    op.run()


    county_layer = InfoLayer([[county.shape, {}]], COUNTY_OPTIONS)
    best_layer = InfoLayer([[school.location, "<p>%s</p>" % school.name]
        for school in op.best_schools()], BEST_OPTIONS)
    worst_layer = InfoLayer([[school.location, "<p>%s</p>" % school.name]
        for school in op.worst_schools()], WORST_OPTIONS)
    map_ = Map([county_layer, best_layer, worst_layer], MAP_OPTIONS)

    context = {
        'stats': {code: op.title for code, op in STATS.items()},
        'county': county,
        'op': op,
        'map': map_
    }

    return render_to_response(op.template, context,
            context_instance=RequestContext(request))

def _link(county):
    url_kwargs={'id': county.id, 'stat': ops.PredictedAttainment.code}
    url = reverse('lea', kwargs=url_kwargs)
    return '<p><a href="{url}">{name}</a></p>'.format(url=url, name=county.name)

def leas(request):
    counties = County.objects.all().order_by('name')
    counties_per_col = counties.count() / 4

    county_layer = InfoLayer([[c.shape, _link(c)] for c in counties])
    map_ = Map([county_layer], LEAS_MAP_OPTIONS)

    context = {
        'counties_columns': paged(counties_per_col, counties),
        'map': map_,
    }

    return render_to_response('dashboard/leas.html',
            context,
            context_instance=RequestContext(request))
