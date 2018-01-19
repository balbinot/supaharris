#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
#from django.contrib.auth.models import User

from schema import schema

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
    cluster_id = models.CharField(max_length=64)

    def __str__(self):
        return self.cluster_id

class Reference(models.Model):
    name     = models.CharField(max_length=256, null=True)
    doi      = models.CharField(max_length=256, null=True, blank=True)
    ads      = models.CharField(max_length=256, null=True, blank=True)
    pub_date = models.DateField('publication date', null=True)

    def __str__(self):
        s = ''
        if self.name:
            s += self.name
        return s

class Observation(models.Model):
    ref        = models.ForeignKey(Reference, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)

    # General fields
    name = models.CharField('Alternate Name', max_length=64, null=True,
                            blank=True)

    ## Float fields defined on schema.py

    ## This cannot be placed in a loop!
    for k,v in zip(schema.keys(), schema.values()):
        print k,v
        tmp = models.FloatField(k, null=True, blank=True, help_text=v)

    comment = models.CharField('Additional comments', max_length=64, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=VALIDATE)


    def __str__(self):
        s = '{} - Ref : {}'.format(str(self.cluster_id), str(self.ref))
        return s
