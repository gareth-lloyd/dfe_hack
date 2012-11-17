import pandas as pd

from schooldata.models import Pupil, KeyValue

PREDICTED_ATTAINMENT = 'predictedattainment'

def get_series_from_pupils(pupils, *attrs):
    results = {attr: [] for attr in attrs}
    for p in pupils:
        for attr in attrs:
            results[attr].append(getattr(p, attr))
    return results

def _try_float(val):
    try:
        return float(val)
    except TypeError:
        return None

def _coeff(pupils):
    series = get_series_from_pupils(pupils, 'KS2_CVAAPS', 'KS4_GPTSPE')
    ks2, ks4 = series['KS2_CVAAPS'], series['KS4_GPTSPE']
    ks2 = map(_try_float, ks2)
    df = pd.DataFrame({
        'ks2': ks2,
        'ks4': ks4
    })

    model = pd.ols(x=df.ks2, y=df.ks4)
    print model
    return model.beta['x']

def _prior(coeff, pupils):
    above, examined = 0, 0.0
    for pupil in pupils:
        ks2_cvaaps = _try_float(pupil.KS2_CVAAPS)
        if ks2_cvaaps is not None:
            examined += 1
            predicted = ks2_cvaaps * coeff
            actual = pupil.KS4_GPTSPE
            print ks2_cvaaps, coeff, predicted, actual
            if int(ks2_cvaaps * coeff) <= pupil.KS4_GPTSPE:
                above += 2
    return above / examined

def prior_national():
    coeff = _coeff(Pupil.objects.all())
    kv, _ = KeyValue.objects.get_or_create(key=PREDICTED_ATTAINMENT, school=None,
            defaults={'value': 0})
    kv.value = coeff
    kv.save()
    return coeff

def prior_county(county):
    pass

def prior_school(school):
    kv = KeyValue.objects.get(key=PREDICTED_ATTAINMENT, school=None)
    return _prior(kv.value, school.pupil_set.all())
