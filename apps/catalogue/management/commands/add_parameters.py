#-*- coding: utf-8 -*-
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from catalogue.models import Parameter


def add_parameters():
    parameters = [
        # Coordinates
        ['RA     ', 'Right Ascension J2000                   ', 'degree'      ],
        ['Dec    ', 'Declination J2000                       ', 'degree'      ],
        ['L      ', 'Galactic Longitude                      ', 'degree'      ],
        ['B      ', 'Galactic Latitude                       ', 'degree'      ],
        ['R_Sun  ', 'Distance to the Sun                     ', 'kpc'         ],
        ['R_Gal  ', 'Distance to the Galactic Center         ', 'kpc'         ],
        ['X      ', 'Galactic distance component X           ', 'kpc'         ],
        ['Y      ', 'Galactic distance component Y           ', 'kpc'         ],
        ['Z      ', 'Galactic distance component Z           ', 'kpc'         ],

        # Orbital parameters
        ['R_apo  ', 'Apocentre radius                        ', 'kpc'         ],
        ['R_peri ', 'Pericentre radius                       ', 'kpc'         ],
        ['ecc    ', 'Orbital eccentricity                    ', ''            ],
        ['phase  ', 'Orbital phase (1=apo; 0=peri)           ', ''            ],

        # Metallicity
        ['[Fe/H] ', 'Metallicity                             ', 'dex'         ],
        ['[Mg/Fe]', 'Magnesium abundance                     ', 'dex'         ],
        ['[a/Fe] ', 'Alpha-element abundance                 ', 'dex'         ],

        # Photometry
        ['E(B-V) ', 'Foreground redenning                    ', 'mag'         ],
        ['V_HB   ', 'V magnitude level of the HB             ', 'mag'         ],
        ['(m-M)V ', 'Apparent visual distance modulus        ', 'mag'         ],
        ['V_t    ', 'Integrated V magnitude                  ', 'mag'         ],
        ['M_V,t  ', 'Cluster luminosity, M_V,t = V_t - (m-M)V', 'mag'         ],
        ['U-B    ', 'U-B                                     ', 'mag'         ],
        ['B-V    ', 'B-V                                     ', 'mag'         ],
        ['V-R    ', 'V-R                                     ', 'mag'         ],
        ['V-i    ', 'V-i                                     ', 'mag'         ],
        ['spt    ', 'Spectral Type                           ', '   '         ],
        ['ellip  ', 'Projected ellipticity of isophotes, e = 1-(b/a)', ''     ],

        # Velocities
        ['v_r    ', 'Heliocentric radial velocity            ', 'km/s'        ],
        ['c_LSR  ', 'Radial velocity relative to solar neighbourhood', 'km/s' ],
        ['pmRA   ', 'RA proper motion                        ', 'mas/yr'      ],
        ['pmDec  ', 'Dec proper motion                       ', 'mas/yr'      ],
        ['sig_v_r', 'Central velocity dispersion             ', 'km/s'        ],

        # Structural parameters
        ['sp_c   ',  'King concentration parameter c=log(r_t/r_c)', ''         ],
        ['sp_r_c ',  'King core radius                        ', 'arcmin'      ],
        ['sp_r_h ',  'Half-light radius                       ', 'arcmin'      ],
        ['sp_mu_V',  'Central surface brightness in V band    ', 'mag/arcsec2' ],
        ['sp_rho_0', 'Central luminosity density, log10(solar_lum/pc^3)', ''   ],
        ['sp_lg_tc', 'Core relaxation time t(r_c) in log10(yr)', 'log10(yr)'   ],
        ['sp_lg_th', 'Mean relaxation time t(r_h) in log10(yr)', 'log10(yr)'   ],
        ['sp_R_J ',  'Jacobii radius                          ', 'pc'          ],

        # Mass and age
        ['Mass   ', 'Present day mass                        ', 'Msun'        ],
        ['Mass_i',  'Intial mass                             ', 'Msun'        ],
        ['Age    ', 'Age                                     ', 'Gyr'         ]
    ]

    nParameters = len(parameters)
    for i, parameter in enumerate(parameters):
        k, v = parameter[0], parameter[1:]  # to have pk ordered hehe
        print("Adding {0} / {1}".format(i+1, nParameters))
        par, created = Parameter.objects.get_or_create(
            name=k.strip(), description=v[0].strip(), unit=v[1], scale=1
        )
        print("  {0}, created = {1}".format(par, created))



class Command(BaseCommand):
    help = "Add initial parameters to the database (one-off, required to"
    help += " add the Harris 1996, ed. 2010 database)"

    def handle(self, *args, **options):
        add_parameters()
