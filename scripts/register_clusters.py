#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catalogue.models import GlobularCluster

from .harris.parse_catalogue import cluster_list

for c in cluster_list.values():

    obj = GlobularCluster(cname=c.gid, altname=c.name)
    obj.save()
