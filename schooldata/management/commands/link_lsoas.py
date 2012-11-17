import csv
from django.core.management.base import BaseCommand
from schooldata.models import Area, School, Pupil

class Command(BaseCommand):
    args = ''
    help = 'Link LSOAs with schools'

    def handle(self, *args, **options):
        for school in School.objects.all():
            lsoas = school.pupil_set.values_list('CEN_LSOA', flat=True)
            unique_lsoas = set(lsoas)
            print len(lsoas), len(unique_lsoas)
            areas = list(Area.objects.filter(lsoa__in=unique_lsoas))

            school.lsoas.add(*areas)
