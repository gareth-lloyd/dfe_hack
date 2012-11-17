from django.contrib.gis.db import models

class County(models.Model):
    name = models.CharField(max_length=128, unique=True)
    shape = models.PolygonField(blank=True, null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

class PostCode(models.Model):
    centre = models.PointField(blank=True, null=True)
    coarse = models.CharField(max_length=4)
    fine = models.CharField(max_length=4, blank=True, null=True)

    objects = models.GeoManager()

    class Meta:
        unique_together = ('coarse','fine')

    def __unicode__(self):
        return "{coarse} {fine}".format(coarse=self.coarse, fine=self.fine)
