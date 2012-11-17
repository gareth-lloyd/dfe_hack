import csv, pprint
from django.core.management.base import BaseCommand

from schooldata.models import School, Pupil
from schooldata.util import paged
from schooldata.definitions import SCHOOL_FIELD_MAP, PUPIL_FIELD_MAP
PAGE_SIZE = 200
TRUE_VALS = ('1', 'Y', 'y', 'True', 'true')

SCHOOL_CACHE = {}
def get_school(urn):
    if urn in SCHOOL_CACHE:
        return SCHOOL_CACHE[urn]

    SCHOOL_CACHE[urn] = School.objects.get(urn=urn)
    return SCHOOL_CACHE[urn]

def convert(_type, val, field_name):
    if _type == bool:
        return val in TRUE_VALS
    elif val:
        if _type == int:
            return int(float(val))
        elif _type == float:
            return float(val)
        else:
            return val

def row_to_pupil(row):
    urn = row.get('KS4_URN')
    for key in SCHOOL_FIELD_MAP.keys():
        del row[key]

    kwargs = {}
    for _type in (int, bool, float, str):
        for field_name in PUPIL_FIELD_MAP.get(_type):
            kwargs[field_name] = convert(_type, row[field_name], field_name)
    kwargs['school'] = get_school(urn)

    return Pupil(**kwargs)

class Command(BaseCommand):
    args = ''
    help = 'Load the schools from tsv'

    def handle(self, *args, **options):
        with open('rawdata/Appathon3_KS4_1011.txt', 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            done = 0
            for page in paged(PAGE_SIZE, reader):
                pupils = [row_to_pupil(row) for row in page]
                Pupil.objects.bulk_create(pupils)
                done += PAGE_SIZE
                pprint.pprint(done)

