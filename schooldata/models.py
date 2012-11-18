from django.contrib.gis.db import models
from collections import Counter

class County(models.Model):
    name = models.CharField(max_length=128, unique=True)
    shape = models.MultiPolygonField(blank=True, null=True)

    objects = models.GeoManager()

    @property
    def schools(self):
        postcodes = PostCode.objects.filter(centre__within=self.shape)
        return School.objects.filter(postcode__in=postcodes)

    def __unicode__(self):
        return self.name

class PostCode(models.Model):
    centre = models.PointField(blank=True, null=True)
    coarse = models.CharField(max_length=4, db_index=True)
    fine = models.CharField(max_length=4, blank=True, null=True)

    objects = models.GeoManager()

    class Meta:
        unique_together = ('coarse','fine')

    def __unicode__(self):
        return "{coarse} {fine}".format(coarse=self.coarse, fine=self.fine)


class Area(models.Model):
    lsoa = models.CharField(max_length=20, db_index=True, unique=True)
    msoa = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=60, db_index=True, unique=True)

    deprivation_score = models.FloatField()
    income_score = models.FloatField()
    health_score = models.FloatField()
    employment_score = models.FloatField()
    education_score = models.FloatField()
    housing_score = models.FloatField()
    crime_score = models.FloatField()
    environment_score = models.FloatField()

    def __unicode__(self):
        return self.name

class School(models.Model):
    urn = models.CharField(max_length=20, db_index=True, unique=True)

    name = models.CharField(max_length=200)
    town = models.CharField(max_length=200, blank=True)
    school_address_1 = models.CharField(max_length=100, blank=True)
    school_address_2 = models.CharField(max_length=100, blank=True)
    school_address_3 = models.CharField(max_length=100, blank=True)
    school_type = models.CharField(max_length=60)

    full_postcode = models.CharField(max_length=10)
    postcode = models.ForeignKey(PostCode)

    lsoas = models.ManyToManyField(Area)

    def _depr(self, attr):
        c = Counter(self.pupil_set.all().values_list('CEN_LSOA', flat=True))
        for lsoa, _ in c.most_common(): 
            try:
                return getattr(Area.objects.get(lsoa=lsoa), attr)
            except Area.DoesNotExist:
                continue

    @property
    def income_score(self):
        return self._depr('income_score')

    @property
    def deprivation_score(self):
        return self._depr('deprivation_score')

    @property
    def education_score(self):
        return self._depr('education_score')

    def _pupil_percentage(self, attr):
        num_pupils = self.pupil_set.count()
        if num_pupils:
            kwargs = {attr: True}
            num_true = float(self.pupil_set.filter(**kwargs).count())
            return  num_true / num_pupils
        else:
            return None

    def _pupil_average(self, attr):
        num_pupils = self.pupil_set.count()
        if num_pupils:
            return  float(self._pupil_total(attr)) / num_pupils
        else:
            return None

    def _pupil_total(self, attr):
        total = self.pupil_set.aggregate(models.Sum(attr))
        return total.values()[0] or 0

    @property
    def avg_exclusions(self):
        return self._pupil_average('EXC_PermanentExclusionCount')

    @property
    def percent_5ac(self):
        return self._pupil_percentage('KS4_FIVEAC') 

    @property
    def percent_fsm(self):
        return self._pupil_percentage('CEN_FSMEligible') 

    def __unicode__(self):
        return self.name


class Pupil(models.Model):
    school = models.ForeignKey(School)
    KS4_RECORDID = models.CharField(max_length=20, unique=True)
    KS4_GENDER = models.CharField(max_length=100, blank=True, null=True)

    KS4_LA = models.CharField(max_length=100, blank=True, null=True)
    KS4_URN = models.CharField(max_length=100, blank=True, null=True)
    KS4_TOE_CODE = models.CharField(max_length=100, blank=True, null=True)

    ABS_PersistentAbsentee15_3Term = models.BooleanField()
    ABS_PersistentAbsentee_3Term = models.BooleanField()
    ABS_AuthorisedAbsence_3Term = models.IntegerField(blank=True, null=True)
    ABS_OverallAbsence_3Term = models.IntegerField(blank=True, null=True)
    ABS_SessionsPossible_3Term = models.IntegerField(blank=True, null=True)
    ABS_UnauthorisedAbsence_3Term = models.IntegerField(blank=True, null=True)

    EXC_PermanentExclusionCount = models.IntegerField(blank=True, null=True)
    EXC_TotalFixedExclusions = models.IntegerField(blank=True, null=True)
    EXC_TotalFixedSessions = models.IntegerField(blank=True, null=True)

    CEN_FSMEligible = models.BooleanField()
    CEN_AgeAtStartOfAcademicYear = models.IntegerField(blank=True, null=True)
    CEN_EthnicGroupMinor = models.CharField(max_length=20, blank=True, null=True)
    CEN_LSOA = models.CharField(max_length=10, blank=True, null=True)
    CEN_LanguageGroupMinor = models.CharField(max_length=20, blank=True, null=True)
    CEN_SENProvision = models.CharField(max_length=2, blank=True, null=True)

    KS2_CVAAPS = models.CharField(max_length=10, blank=True, null=True)
    KS2_ENGLEV = models.CharField(max_length=10, blank=True, null=True)
    KS2_MATLEV = models.CharField(max_length=10, blank=True, null=True)
    KS2_SCILEV = models.CharField(max_length=10, blank=True, null=True)
    KS2_TOTPTS = models.CharField(max_length=10, blank=True, null=True)

    KS4_ENTRY_5 = models.BooleanField()
    KS4_ALLSCI = models.BooleanField()
    KS4_FIVEAC = models.BooleanField()
    KS4_FIVEAG = models.BooleanField()
    KS4_ANYLEV1 = models.BooleanField()
    KS4_LEVEL2_EM = models.BooleanField()
    KS4_LEVEL2EM_GCSE = models.BooleanField()
    KS4_GCSE_MATHATT = models.BooleanField()
    KS4_GCSE_SCIATT = models.BooleanField()
    KS4_GCSE_ENGATT = models.BooleanField()

    KS4_ENTRY_E = models.IntegerField(blank=True, null=True)
    KS4_GCSE_AA = models.IntegerField(blank=True, null=True)
    KS4_GCSE_AC = models.IntegerField(blank=True, null=True)
    KS4_GCSE_AG = models.IntegerField(blank=True, null=True)
    KS4_GCSE_DG = models.IntegerField(blank=True, null=True)
    KS4_GCSE_E = models.IntegerField(blank=True, null=True)
    KS4_PASS_AC_AAT = models.IntegerField(blank=True, null=True)
    KS4_PASS_AG = models.IntegerField(blank=True, null=True)
    KS4_KS4SCI = models.IntegerField(blank=True, null=True)
    KS4_HGMATH = models.CharField(max_length=2, blank=True, null=True)

    KS4_KS2ENG24P = models.IntegerField(blank=True, null=True)
    KS4_KS2MAT24P = models.IntegerField(blank=True, null=True)
    KS4_Flag24ENGPrg = models.IntegerField(blank=True, null=True)
    KS4_Flag24MATPrg = models.IntegerField(blank=True, null=True)

    KS4_GPTSPE = models.FloatField(blank=True, null=True)

class KeyValue(models.Model):
    key = models.CharField(unique=True, max_length=128)
    school = models.ForeignKey(School, blank=True, null=True)
    value = models.FloatField()

    class Meta:
        unique_together = ('key', 'school')

def poss_values(attr):
    pupils = School.objects.all()[0].pupil_set
    return set(pupils.values_list(attr, flat=True))


