import pandas as pd
from django.contrib.gis.db.models import Sum
from schooldata.models import Pupil, KeyValue, Area

TOP_X = 5

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
    y_series = map(_try_float, y_series)
    return _ols(x_series, y_series)

def run_model(coeff, intercept, pupils, x_attr, y_attr):
    underperforming, overperforming = [], []
    for pupil in pupils:
        x_val = _try_float(getattr(pupil, x_attr))
        y_val = _try_float(getattr(pupil, y_attr))
        if (x_val is not None) and (y_val is not None):
            predicted = (x_val * coeff) + intercept
            if predicted <= y_val:
                overperforming.append([x_val, y_val])
            else:
                underperforming.append([x_val, y_val])
    return underperforming, overperforming

class Operation(object):
    best_title = "Best Performing Schools"
    worst_title = "Worst Performing Schools"
    def __init__(self):
        self.results = []

    def _sorted(self, ascending=True):
        factor = 1 if ascending else -1
        return sorted(self.results, key=lambda r: factor * r['value'])

    def best(self):
        return (self._sorted(ascending=False))[:TOP_X]

    def worst(self):
        return self._sorted()[:TOP_X]

    def _schools(self, results):
        return [r['school'] for r in results]

    def best_schools(self):
        return self._schools(self.best())

    def worst_schools(self):
        return self._schools(self.worst())

    def get_schools(self):
        """Must be implemented by sublcass or use e.g. 
        CountyOperationMixin"""
        raise NotImplemented

class RegressionOperation(Operation):
    performance_title = "% outperforming expectations"
    template = 'dashboard/lea_regression.html'

    def __init__(self):
        super(RegressionOperation, self).__init__()
        self.coeff = _get_kv(self.COEFF_KEY).value
        self.intercept = _get_kv(self.INT_KEY).value

    def add_result(self, school, n_pupils, pupils, under, over):
        if not len(under) and not len(over):
            # haven't been able to determine anything
            return

        prop_over = (float(len(over)) / n_pupils) * 100 if n_pupils else None
        self.results.append({
            'school': school,
            'under': under,
            'over': over,
            'value': prop_over,
        })

    def annotate(self, pupil):
        """Hook to allow sublcasses to annotate pupil objects with 
        additional information."""
        return pupil

    def run(self):
        for school in self.get_schools():
            pupils = school.pupil_set.all()
            n_pupils = pupils.all().count()
            if n_pupils < 40:
                continue
            pupils = map(self.annotate, pupils)
            under, over = run_model(self.coeff, self.intercept, pupils,
                    self.x_axis, self.y_axis)
            self.add_result(school, n_pupils, pupils, under, over)


    def _combined(self, results):
        combined = []
        for result in results:
            combined.extend(result['under'])
            combined.extend(result['over'])
        return combined

    def combined_best(self):
        return self._combined(self.best())

    def combined_worst(self):
        return self._combined(self.worst())

    def _point_on_line(self, x):
        return (x * self.coeff) + self.intercept

    def regression_line(self):
        return [
            [self.r_line_min, self._point_on_line(self.r_line_min)],
            [self.r_line_max, self._point_on_line(self.r_line_max)],
        ]

    @classmethod
    def set_national_model(cls, coeff, intercept):
        kv_coeff = _get_kv(cls.COEFF_KEY)
        kv_coeff.value = coeff
        kv_coeff.save()

        kv_int = _get_kv(cls.INT_KEY)
        kv_int.value = intercept
        kv_int.save()


class CountyOperationMixin(object):
    def __init__(self, county):
        super(CountyOperationMixin, self).__init__()
        self.county = county

    def get_schools(self):
        return self.county.schools


class PredictedAttainment(CountyOperationMixin, RegressionOperation):
    description = "KS4 attainment relative to KS2 attainment"
    COEFF_KEY = 'predictedattainment_c'
    INT_KEY = 'predictedattainment_i'
    code = 'predictedattainment'
    title = 'Predicted Attainment'
    x_axis = 'KS2_CVAAPS'
    y_axis = 'KS4_GPTSPE'
    x_label = 'Key stage 2 attainment'
    y_label = 'Key stage 4 attainment'
    r_line_min = 0
    r_line_max = 40

    def __init__(self, county):
        super(PredictedAttainment, self).__init__(county)

    @staticmethod
    def national_model():
        coeff, intercept = create_model(Pupil.objects.all(),
                'KS2_CVAAPS', 'KS4_GPTSPE')
        PredictedAttainment.set_national_model(coeff, intercept)

class PredictedScience(CountyOperationMixin, RegressionOperation):
    description = "KS4 science attainment relative to general KS4 attainment"
    COEFF_KEY = 'predictedscience_c'
    INT_KEY = 'predictedscience_i'
    code = 'scienceattainment'
    title = 'Science Attainment'
    x_axis = 'KS2_CVAAPS'
    y_axis = 'KS4_KS4SCI'
    x_label = 'Key stage 4 attainment'
    y_label = 'Science attainment'
    r_line_max = 40
    r_line_min = 10

    def __init__(self, county):
        super(PredictedScience, self).__init__(county)

    @staticmethod
    def national_model():
        x, y = [], []
        for pupil in Pupil.objects.all()[:100000]:
            # only consider pupils that took science
            if pupil.KS4_KS4SCI:
                x.append(pupil.KS4_GPTSPE)
                y.append(pupil.KS4_KS4SCI)
        coeff, intercept = _ols(x, y)
        PredictedScience.set_national_model(coeff, intercept)

DEPRIVATIONS = {}
class SocioEcon(CountyOperationMixin, RegressionOperation):
    description = "KS4 attainment against socio-economic deprivation"
    COEFF_KEY = 'socioecon_c'
    INT_KEY = 'socioecon_i'
    code = 'socioecon'
    title = 'Impact of Deprivation'
    x_axis = 'deprivation'
    y_axis = 'KS4_GPTSPE'
    x_label = 'Key stage 4 attainment'
    y_label = 'Socio-economic deprivation'
    r_line_max = 80
    r_line_min = 0

    def __init__(self, county):
        super(SocioEcon, self).__init__(county)

    def annotate(self, pupil):
        pupil.deprivation = self.get_deprivation(pupil)
        return pupil

    @staticmethod
    def get_deprivation(pupil):
        lsoa = pupil.CEN_LSOA
        if lsoa not in DEPRIVATIONS:
            try:
                depr = Area.objects.get(lsoa=lsoa).deprivation_score
            except Area.DoesNotExist:
                depr = None
            DEPRIVATIONS[lsoa] = depr
        return DEPRIVATIONS[lsoa]

    @staticmethod
    def national_model():
        x, y = [], []
        for pupil in Pupil.objects.all()[:100000]:
            # only consider pupils that took science
            if pupil.KS4_KS4SCI:
                x.append(SocioEcon.get_deprivation(pupil))
                y.append(pupil.KS4_GPTSPE)
        coeff, intercept = _ols(x, y)
        SocioEcon.set_national_model(coeff, intercept)

class SingleValueOperation(Operation):
    """Any Operation that describes a school with a single value,
    e.g. an average across students.
    """
    template = 'dashboard/lea_single_value.html'

    @classmethod
    def calculate(cls, pupils):
        raise NotImplemented

    @classmethod
    def national_average(cls):
        value = cls.calculate(Pupil.objects.all())
        kv = _get_kv(cls.KV_KEY)
        kv.value = value
        kv.save()

    def average_line(self):
        avg = _get_kv(self.KV_KEY).value
        return [avg for _ in range(TOP_X)]

    def add_result(self, school, value):
        self.results.append({
            'school': school,
            'value': value
        })

    def best_values(self):
        return [r['value'] for r in self.best()]

    def worst_values(self):
        return [r['value'] for r in self.worst()]

    def run(self):
        for school in self.get_schools():
            self.add_result(school, self.calculate(school.pupil_set.all()))

class PercentageOperation(SingleValueOperation):
    performance_title = "%"

    @classmethod
    def calculate(cls, pupils):
        kwargs = {cls.pupil_attr: True}
        num_true = pupils.all().filter(**kwargs).count()
        num_pupils = pupils.all().count()
        return (float(num_true) / num_pupils) * 100 if num_pupils else None


class AverageOperation(SingleValueOperation):
    performance_title = "Average"

    @classmethod
    def calculate(cls, pupils):
        num_pupils = pupils.all().count()
        if num_pupils:
            total = pupils.all().aggregate(Sum(cls.pupil_attr)).values()[0]
            return (float(total) / num_pupils)
        else:
            return None


class Absentee(CountyOperationMixin, PercentageOperation):
    best_title = "Worst Performing Schools"
    worst_title = "Best Performing Schools"
    description = "Percentage of students classified as persistently absent"
    pupil_attr = 'ABS_PersistentAbsentee_3Term'
    code = 'absentee'
    title = "Absenteeism"
    KV_KEY = 'absentee'

class FiveAC(CountyOperationMixin, PercentageOperation):
    description = "Percentage of students attaining five grades A* to C at GCSE"
    pupil_attr = 'KS4_FIVEAC'
    code = 'fiveac'
    title = "5 A*-C"
    KV_KEY = 'fiveac'

class EnglishProgress(CountyOperationMixin, AverageOperation):
    description = "A measure of Progress in English between key stages 2 and 4"
    code = 'englishprogress'
    title = "English Progress"
    KV_KEY = 'englishprogress'
    pupil_attr = 'KS4_KS2ENG24P'

class MathsProgress(CountyOperationMixin, AverageOperation):
    description = "A measure of Progress in Maths between key stages 2 and 4"
    code = 'mathsprogress'
    title = "Maths Progress"
    KV_KEY = 'mathsprogress'
    pupil_attr = 'KS4_KS2MAT24P'

