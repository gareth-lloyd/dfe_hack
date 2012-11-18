import pandas as pd

from schooldata.models import Pupil, KeyValue, Area, School

PREDICTED_ATTAINMENT_C = 'predictedattainment_c'
PREDICTED_ATTAINMENT_I = 'predictedattainment_i'

DEPRIVATION_C = 'deprivation_c'
DEPRIVATION_I = 'deprivation_i'

SCIENCE_C = 'deprivation_c'
SCIENCE_I = 'deprivation_i'

def _get_kv(key):
    kv, _ = KeyValue.objects.get_or_create(key=key, school=None,
            defaults={'value': 0})
    return kv

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

def _ols(x_series, y_series):
    df = pd.DataFrame({
        'x': x_series,
        'y': y_series
    })
    model = pd.ols(x=df['x'], y=df['y'])
    print model
    return model.beta['x'], model.beta['intercept']

def create_model(pupils, x_attr, y_attr):
    series = get_series_from_pupils(pupils, x_attr, y_attr)
    x_series, y_series = series[x_attr], series[y_attr]

    x_series = map(_try_float, x_series)
    y_series = map(_try_float, x_series)
    return _ols(x_series, y_series)

def create_national_prior_attainment_model():
    kv_coeff = _get_kv(PREDICTED_ATTAINMENT_C)
    kv_int = _get_kv(PREDICTED_ATTAINMENT_I)

    kv_coeff.value, kv_int.value = create_model(Pupil.objects.all(),
            'KS2_CVAAPS', 'KS4_GPTSPE')
    kv_coeff.save()
    kv_int.save()

def _run_model(coeff, intercept, pupils, x_attr, y_attr):
    above, examined = 0, 0.0
    for pupil in pupils:
        x_val = _try_float(getattr(pupil, x_attr))
        y_val = _try_float(getattr(pupil, y_attr))
        if (x_val is not None) and (y_val is not None):
            examined += 1
            predicted = (x_val * coeff) + intercept
            if predicted <= y_val:
                above += 1
    return above / examined

def prior_attainment(school):
    coeff = _get_kv(PREDICTED_ATTAINMENT_C).value
    intercept = _get_kv(PREDICTED_ATTAINMENT_I).value
    return _run_model(coeff, intercept, school.pupil_set.all(),
            'KS2_CVAAPS', 'KS4_GPTSPE')

DEPRIVATIONS = {}
def get_deprivation(pupil):
    lsoa = pupil.CEN_LSOA
    if lsoa not in DEPRIVATIONS:
        try:
            depr = Area.objects.get(lsoa=lsoa).deprivation_score
        except Area.DoesNotExist:
            depr = None
        DEPRIVATIONS[lsoa] = depr
    return DEPRIVATIONS[lsoa]

def create_national_socioecon_model():
    kv_coeff = _get_kv(DEPRIVATION_C)
    kv_int = _get_kv(DEPRIVATION_I)

    x, y = [], []
    pupils = Pupil.objects.all()[:10000]
    for pupil in pupils:
        depr = get_deprivation(pupil)
        if depr and pupil.CEN_FSMEligible:
            depr *= 1.5
        x.append(depr)
        y.append(pupil.KS4_GPTSPE)

    kv_coeff.value, kv_int.value = _ols(x, y)
    kv_coeff.save()
    kv_int.save()

def socioecon(school):
    coeff = _get_kv(DEPRIVATION_C).value
    intercept = _get_kv(DEPRIVATION_I).value

    pupils = school.pupil_set.all()
    def annotate(p):
        p.deprivation = get_deprivation(p)
        return p
    pupils = map(annotate, pupils)
    return _run_model(coeff, intercept, pupils, 'deprivation', 'KS6_GPTSPE')

def create_national_school_level_socio():
    deprs, acs = [], []
    for school in School.objects.all()[:1000]:
        deprs.append(school.percent_fsm * 100)
        acs.append(school.percent_5ac * 100)
    print deprs[:10], acs[:10]
    return _ols(deprs, acs)

def create_scimat_model():
    x, y = [], []
    for pupil in Pupil.objects.all()[:100000]:
        x.append(pupil.KS4_GPTSPE)
        y.append(pupil.KS4_KS4SCI)

    kv_coeff = _get_kv(SCIENCE_C)
    kv_int = _get_kv(SCIENCE_I)
    kv_coeff.value, kv_int.value = _ols(x, y)
    kv_coeff.save()
    kv_int.save()

def create_progress_model():
    x, y = [], []
    for pupil in Pupil.objects.all()[:100000]:
        x.append(get_deprivation(pupil))
        y.append(pupil.KS4_KS2MAT24P)
    _ols(x, y)

