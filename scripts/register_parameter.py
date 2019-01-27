#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")

from catalogue.models import Parameter

pars = { 'RA     ' : ['Right Ascension J2000        ', 'degree'      ],
         'Dec    ' : ['Declination J2000            ', 'degree'      ],
         'L      ' : ['Galactic Longitude           ', 'degree'      ],
         'B      ' : ['Galactic Latitude            ', 'degree'      ],
         'R_Sun  ' : ['Distance to the Sun          ', 'kpc'         ],
         '[Fe/H] ' : ['Metallicity                  ', 'dex'         ],
         '[Mg/Fe]' : ['Magnesium abundance          ', 'dex'         ],
         '[a/Fe] ' : ['Alpha-element abundance      ', 'dex'         ],
         'E(B-V) ' : ['Redenning                    ', 'mag'         ],
         'ellip  ' : ['Ellipticity                  ', ''            ],
         'V_r    ' : ['Radial velocity              ', 'km/s'        ],
         'pmRA   ' : ['RA proper motion             ', 'mas/yr'      ],
         'pmDec  ' : ['Dec proper motion            ', 'mas/yr'      ],
         'sig_v  ' : ['Radial velocity dispersion   ', 'km/s'        ],
         'c      ' : ['King concentration parameter ', ''            ],
         'r_c    ' : ['King core radius             ', 'arcmin'      ],
         'r_h    ' : ['Half-light radius            ', 'arcmin'      ],
         'mu_V   ' : ['Central surface brightness   ', 'mag/arcsec2' ],
         'ecc    ' : ['Orbital eccentricity         ', ''            ],
         'phase  ' : ['Orbital phase (1=apo; 0=peri)', ''            ],
         'R_apo  ' : ['Apocentre radius             ', 'kpc'         ],
         'R_peri ' : ['Pericentre radius            ', 'kpc'         ],
         'R_J    ' : ['Jacobii radius               ', 'pc'          ],
         'Mass   ' : ['Present day mass             ', 'Msun'        ],
         'Mass_i'  : ['Intial mass                  ', 'Msun'        ],
         'Age    ' : ['Age                          ', 'Gyr'         ]
        }


for p, v in pars.items():
    print(p, v)
    par = Parameter(pname=p.strip(), desc=v[0].strip(), unit=v[1], scale=1)
    par.save()






#dbnames = [o.cluster_id for o in GlobularCluster.objects.all()]
#r = Reference(name='Trager et al.', doi='10.1086/118116', ads='add later')
#r.save()
#
#def insert_into_django():
#    # Emptying the tables
#    for c in Profile.objects.all():
#        c.delete()
#
#    for query in dbnames:
#        b = process.extractOne(query, tragernames)
#        if b[-1] > 90: ## sucess theshold for fuzz matching
#            print('{} matched to {}; producing json'.format(b[0], query))
#            tbl = f.get_rp(name=b[0])
#            logr = tbl['logr']
#            muV = tbl['muV']
#            w = tbl['Weight']
#            dset = tbl['DataSet']
#
#            odict = {'log(r/arcmin)': logr.tolist(),
#                     'mu_V': muV.tolist(),
#                     'W': w.tolist(),
#                     'label': dset.tolist(),}
#
#
#
#            # Inserting a reference for the Harris Catalogue
#
#            print('Inserting into database :')
#            # Now add json to every matched cluster Profile model
#            do = Profile()
#            do.cluster_id = GlobularCluster.objects.filter(cluster_id=query)[0]
#            print do.cluster_id
#            do.ref = r
#            do.ptype = "Surface brightness profile"
#            do.profile = json.dumps(odict)
#            do.save()
#
#
#        #cluster_id = models.ForeignKey(GlobularCluster, on_delete=models.CASCADE)
#        #ptype      = models.CharField('Type of profile', max_length=256, null=True, blank=True)
#        #profile    = JSONField('Profile')
#        #modpars    = JSONField('Model parameters')
#        #mtype      = models.CharField('Model flavour', max_length=256, null=True, blank=True)
#
