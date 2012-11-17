from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from schooldata.models import School
from schooldata.operations import (prior_school, get_series_from_pupils,
        _try_float)

def json(func):
    def wrapper(*args, **kwargs):
        j_dict = func(*args, **kwargs)
        return HttpResponse(json.dumps(j_dict), content_type="application/json")
    return wrapper

@json
def plot_json(request):
    school = School.objects.all()[0]
    pupils = school.pupil_set.all()
    series = get_series_from_pupils(pupils, 'KS2_CVAAPS', 'KS4_GPTSPE')
    ks2, ks4 = series['KS2_CVAAPS'], series['KS4_GPTSPE']
    ks2 = map(_try_float, ks2)
    return {
        'x': ks2,
        'y': ks4
    }

def show_plot(request):
    return render_to_response('plot.html', {},
            context_instance=RequestContext(request))
