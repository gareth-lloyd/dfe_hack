from path import path
from schooldata.models import County
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.core.management.base import BaseCommand

def get_name(filename):
    _, name = filename.split('-')
    name = name[:-7]
    name = name.replace('_', ' ')
    print name
    return name

class Command(BaseCommand):
    args = ''
    help = 'Load the counties from textfiles'

    def handle(self, *args, **options):
        for filename in path('rawdata/counties').files():
            if 'ALL' not in filename:
                continue

            name = get_name(filename)
            polygons = []
            with open(filename) as f:
                this_poly = []
                for line in f.readlines():
                    if line.startswith('#'):
                        continue
                    try:
                        lat, lon = line.split(', ')
                    except ValueError:
                        polygons.append(Polygon(this_poly))
                        this_poly = []
                    else:
                        this_poly.append(Point(float(lon), float(lat)))
            County.objects.create(name=name, shape=MultiPolygon(polygons))


