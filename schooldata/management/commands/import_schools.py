import csv, pprint
from schooldata.models import PostCode, School
from django.core.management.base import BaseCommand

from schooldata.definitions import SCHOOL_FIELD_MAP

def get_postcode(longcode):
    code = longcode.replace(' ', '').upper().strip()
    code = longcode[:-3]
    code = code.strip()
    return PostCode.objects.get(coarse=code)

class Command(BaseCommand):
    args = ''
    help = 'Load the schools from tsv'

    def handle(self, *args, **options):
        seen = set()

        with open('rawdata/Appathon3_KS4_1011.txt', 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:

                kwargs = {attr_name: row.get(code)
                        for code, attr_name in SCHOOL_FIELD_MAP.items()}

                if kwargs['urn'] in seen:
                    continue
                else:
                    seen.add(kwargs['urn'])

                kwargs['postcode'] = get_postcode(kwargs['postcode'])
                School.objects.create(**kwargs)


