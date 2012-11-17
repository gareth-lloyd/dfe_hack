from django.core.management.base import BaseCommand
from schooldata.operations import prior
from schooldata.models import School

class Command(BaseCommand):
    args = ''
    help = 'run an op - for testing'

    def handle(self, *args, **options):
        school = School.objects.all()[0]
        prior(school)
