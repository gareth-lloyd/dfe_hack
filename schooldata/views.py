import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from schooldata.models import School,Pupil
from schooldata.operations import (get_series_from_pupils,
        _try_float, get_deprivation)

def return_json(func):
    def wrapper(*args, **kwargs):
        j_dict = func(*args, **kwargs)
        return HttpResponse(json.dumps(j_dict), content_type="application/json")
    return wrapper

@return_json
def plot_json(request):
    x, y = [], []
    for pupil in Pupil.objects.all()[:1000]:
        x.append(get_deprivation(pupil))
        y.append(pupil.KS4_KS2MAT24P)
    data = zip(x, y)
    print data

    return {
        'data': data
    }

def show_plot(request):
    return render_to_response('dashboard/plot.html', {},
            context_instance=RequestContext(request))

