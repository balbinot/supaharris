#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.db.models import CASCADE
from jsonfield import JSONField
#from django.contrib.auth.models import User

UNIT_LENGTH = 32
VALIDATE = 1
ACCEPTED = 2
REJECTED = 3

STATUS_CHOICES = (
    (VALIDATE, 'To be validated'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
)

class GlobularCluster(models.Model):
    cname      = models.CharField('Name', max_length=64, unique=True,
                                  primary_key=True)
    altname    = models.CharField('Alternative Name', max_length=64, null=True,
                                  blank=True)

    def __str__(self):
        return self.cluster_id

class Reference(models.Model):
    rname  = models.CharField("Reference", max_length=256, null=True,
                                unique=True)
    doi      = models.CharField("DOI", max_length=256, null=True, blank=True)
    ads      = models.CharField("ADS", max_length=256, null=True, blank=True)
    pub_date = models.DateField('Publication date', null=True)

    def __str__(self):
        return self.refname



class Parameter(models.Model):
    pname   = models.CharField("Parameter", max_length=64, unique=True,
                               primary_key=True)
    desc    = models.TextField("Description", null=True, blank=True)
    unit    = models.CharField("Unit", max_length=256, null=False, blank=False,
                               help_text="Must comply with astropy.unit")

    def __str__(self):
        return 'Parameter {} [{}]'.format(self.pname, self.unit)


class Profile(models.Model):
    rname      = models.ForeignKey(Reference, on_delete=CASCADE)
    cname      = models.ForeignKey(GlobularCluster, on_delete=CASCADE)
    ptype      = models.CharField('Type of profile', max_length=256, null=True, blank=True)
    profile    = JSONField('Profile')
    modpars    = JSONField('Model parameters')
    mtype      = models.CharField('Model flavour', max_length=256, null=True, blank=True)

    def __str__(self):
        s = '{} - Ref : {}'.format(str(self.cluster_id), str(self.ref))
        return s

class Auxiliary(models.Model):
    rname      = models.ForeignKey(Reference, on_delete=CASCADE)
    cname      = models.ForeignKey(GlobularCluster, on_delete=CASCADE)
    fpath      = models.FilePathField(path='/static', blank=True, null=True)
    furl       = models.URLField(blank=True, null=True)

    def __str__(self):
        s = '{} - Ref : {} {}'.format(str(self.cluster_id), str(self.ref))
        return s

class ObsManager(models.Manager):
    """ Assemble string with val +- sigma """
    def valsig(self):
        qs = super().get_queryset()
        vals = ['{} +- {}'.format(i.val, i.sigup) for i in qs]

        return vals

class Observation(models.Model):
    rname   = models.ForeignKey(Reference, on_delete=CASCADE)
    cname   = models.ForeignKey(GlobularCluster, on_delete=CASCADE)
    pname   = models.ForeignKey(Parameter, on_delete=CASCADE)

    val     = models.FloatField("Value")
    sigup   = models.FloatField("Sigma up", null=True, blank=True)
    sigdown = models.FloatField("Sigma down", null=True, blank=True)

    dstr    = ObsManager()

    ## FIXME: not sure how to call units from Parameter model to print here
    def __str__(self):
        s = '{}: {} = {:.3f} + {:.3f} - {:.3f} ({})'.format(self.cname,
                                                            self.pname,
                                                            self.val,
                                                            self.sigup,
                                                            self.sigdown,
                                                            self.rname)
        return s


class Rank(models.Model):
    oid        = models.ForeignKey(Observation, on_delete=CASCADE)
    rank       = models.IntegerField()


