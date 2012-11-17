import csv
from schooldata.models import School, Pupil
from django.core.management.base import BaseCommand

from schooldata.definitions import SCHOOL_FIELD_MAP, PUPIL_FIELD_MAP
PAGE_SIZE = 200
TRUE_VALS = ('1', 'Y', 'y', 'True', 'true')
ACTUAL_TRUE_VALS = set()

SCHOOL_CACHE = {}
def get_school(urn):
    if urn in SCHOOL_CACHE:
        return SCHOOL_CACHE[urn]

    SCHOOL_CACHE[urn] = School.objects.get(urn=urn)
    return SCHOOL_CACHE[urn]

def paged(page_size, iterable):
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    yield page

def convert(_type, val):
    if _type == bool:
        ACTUAL_TRUE_VALS.add(val)
        return val in TRUE_VALS
    else:
        return _type(val)

def row_to_pupil(row):
    urn = row.pop('KS4_URN')
    row['school'] = get_school(urn)
    for key in SCHOOL_FIELD_MAP.keys():
        del row[key]

    for _type in (int, bool, float):
        for field_name in PUPIL_FIELD_MAP.get(_type):
            row[field_name] = convert(_type, row[field_name])

    return Pupil(**row)

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
                print done
                break

        print ACTUAL_TRUE_VALS
