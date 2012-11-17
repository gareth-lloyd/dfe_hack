import csv
from schooldata.util import paged
from schooldata.models import Area
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Load the postcodes from csv'

    def handle(self, *args, **options):
        with open('rawdata/deprivation/J440310_2309_GeoPolicy_LSOA.CSV', 'r') as f:
            for _ in range(6):
                f.readline()
            reader = csv.reader(f)
            for page in paged(200, reader):
                areas = []
                for row in page:
                    areas.append(Area(
                        name=row[11],
                        msoa=row[8],
                        lsoa=row[10],
                        deprivation_score=row[14],
                        income_score=row[16],
                        employment_score=row[18],
                        health_score=row[20],
                        education_score=row[22],
                        housing_score=row[24],
                        crime_score=row[26],
                        environment_score=row[28],
                    ))
                Area.objects.bulk_create(areas)
