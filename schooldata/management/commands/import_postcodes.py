import csv
from schooldata.models import PostCode
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Load the postcodes from csv'

    def handle(self, *args, **options):
        with open('rawdata/postcodes.csv', 'r') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader):
                # skip labels
                if row_num == 0:
                    continue
                _, coarse, lat, lon = row
                centre = Point(float(lon), float(lat))
                PostCode.objects.create(coarse=coarse, centre=centre)

