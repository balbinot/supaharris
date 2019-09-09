import os
import sys
import gzip
import numpy
import logging
from io import StringIO
from matplotlib import pyplot
from astropy import units as u
from astropy import coordinates as coord

logger = logging.getLogger("console")
logger.logLevel = logging.DEBUG

BASEDIR = "/".join(__file__.split("/")[:-1]) + "/MW_StarClusters_Bica2019/"


def parse_bica_2019_refs(fname="{0}refs.dat".format(BASEDIR), debug=False,):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.debug("ERROR: file not found: {0}".format(fname))
        return

    # Byte-by-byte Description of file: refs.dat
    # --------------------------------------------------------------------------------
    #    Bytes Format Units   Label     Explanations
    # --------------------------------------------------------------------------------
    #    1-  7  A7    ---     Code      Reference code
    #    9-365  A357  ---     Ref       Complete reference (1)
    #  367-385  A19   ---     Bibcode   Bibcode of the reference
    #  387-396  A10   ---     Cat       Catalogue reference in VizieR
    # --------------------------------------------------------------------------------
    # Note (1): REF963 is related to the Asterism object type, and includes
    #   3 electronic addresses that are currently active.
    # --------------------------------------------------------------------------------


    nentries, entries = 0, dict()
    with open(fname, "r") as f:
        for line in f.readlines(): nentries += 1
    with open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            ref_code = line[0:7].strip()
            ref = line[8:365].strip()
            bib_code = line[366:385].strip()
            cat = line[386:396].strip()

            if debug:
                logger.debug("Entry {0}/{1}".format(i+1, nentries))
                logger.debug("  ref_code: {0}".format(ref_code))
                logger.debug("  ref: {0}".format(ref))
                logger.debug("  bib_code: {0}".format(bib_code))
                logger.debug("  cat: {0}".format(cat))

            entries[ref_code] = [ref, bib_code, cat]
    return entries


def parse_bica_2019_table2(fname="{0}table2.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    # Byte-by-byte Description of file: table2.dat
    # --------------------------------------------------------------------------------
    #    Bytes Format Units Label   Explanations
    # --------------------------------------------------------------------------------
    #    1- 13 A13    ---   Class   Object type(s) (G1)
    #   15- 18 I4     ---   Nobj    [1/3784] Number of relevant objects in the
    #                                reference
    #   20- 38 A19    ---   Name    Designation(s) and/or object types as guidelines
    #   40- 46 A7     ---   Code    Reference code (REFNNNN, where NNNN is a random
    #                                number) (see refs.dat file) (1)
    # --------------------------------------------------------------------------------
    # Note (1): Reference code is the link between the objects in Tables 3, 4 and 5
    #   and their references in the present table.
    # --------------------------------------------------------------------------------

    nentries, entries = 0, dict()
    with open(fname, "r") as f:
        for line in f.readlines(): nentries += 1
    with open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            obj_class = line[0:13].strip()
            nobj = line[14:18].strip()
            name = line[19:38].strip()
            codes = line[39:46].strip()

            if debug:
                logger.debug("\nEntry {0}/{1}".format(i+1, nentries))
                logger.debug("  obj_class: {0}".format(obj_class))
                logger.debug("  nobj: {0}".format(nobj))
                logger.debug("  name: {0}".format(name))
                logger.debug("  codes: {0}".format(codes))

            for code in codes.split(","):
                entries[code] = [obj_class, nobj, name]
    return entries


def parse_bica_2019_table3(fname="{0}table3.dat.gz".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    # Byte-by-byte Description of file: table3.dat
    # --------------------------------------------------------------------------------
    #    Bytes Format Units  Label   Explanations
    # --------------------------------------------------------------------------------
    #    1-  6 F6.2   deg    GLON    Galactic longitude
    #    8- 13 F6.2   deg    GLAT    Galactic latitude
    #   15- 16 I2     h      RAh     Hour of Right Ascension (J2000)
    #   18- 19 I2     min    RAm     Minute of Right Ascension (J2000)
    #   21- 22 I2     s      RAs     Second of Right Ascension (J2000)
    #       24 A1     ---    DE-     Sign of the Declination (J2000)
    #   25- 26 I2     deg    DEd     Degree of Declination (J2000)
    #   28- 29 I2     arcmin DEm     Arcminute of Declination (J2000)
    #   31- 32 I2     arcsec DEs     Arcsecond of Declination (J2000)
    #   34- 40 F7.2   arcmin Diam-a  [0.01/4560] Major axis diameter
    #   42- 48 F7.2   arcmin Diam-b  [0.01/2400] Minor axis diameter
    #   50-161 A112   ---    Name    Chronologically ordered cross-identified
    #                                 designation(s)
    #  163-167 A5     ---    Class1  Object type (G1)
    #  169-173 A5     ---    Class2  Possible second object type (G1)
    #  175-206 A32    ---    Com     Comments
    #  208-254 A47    ---    Code    Reference code(s) (see Table 2)
    # --------------------------------------------------------------------------------

    nentries, entries = 0, dict()
    with gzip.open(fname, "r") as f:
        for line in f.readlines(): nentries += 1
    with gzip.open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            glon = line[0:6].strip().decode("ascii")
            glat = line[7:13].strip().decode("ascii")
            sky_coord = coord.SkyCoord(
                glon, glat, frame="galactic", equinox="J2000", unit=(u.deg, u.deg)
            )
            rah = line[14:16].strip().decode("ascii")
            ram = line[17:19].strip().decode("ascii")
            ras = line[20:22].strip().decode("ascii")
            de_sign = line[23:24].strip().decode("ascii")
            ded = line[24:26].strip().decode("ascii")
            dem = line[27:29].strip().decode("ascii")
            des = line[30:32].strip().decode("ascii")
            sky_coord2 = coord.SkyCoord(
                "{0} {1} {2} {3}{4} {5} {6}".format(
                    rah, ram, ras, "+" if de_sign != "-" else de_sign, ded, dem, des
                ), frame="icrs", equinox="J2000", unit=(u.hourangle, u.deg)
            )
            # sky_coord2.galactic should now match glon, glat ... :-)
            diama = line[33:40].strip().decode("ascii")
            diamb = line[41:48].strip().decode("ascii")
            name = line[49:161].strip().decode("ascii")
            obj_class1 = line[162:167].strip().decode("ascii")
            obj_class2 = line[168:173].strip().decode("ascii")
            comments = line[174:206].strip().decode("ascii")
            codes = line[207:254].strip().decode("ascii")

            if debug:
                logger.debug("\nEntry {0}/{1}".format(i+1, nentries))
                logger.debug("  glon: {0}".format(glon))
                logger.debug("  glat: {0}".format(glat))
                logger.debug("  sky_coord: {0}".format(sky_coord))
                logger.debug("  rah: {0}".format(rah))
                logger.debug("  ram: {0}".format(ram))
                logger.debug("  ras: {0}".format(ras))
                logger.debug("  de_sign: {0}".format(de_sign))
                logger.debug("  ded: {0}".format(ded))
                logger.debug("  dem: {0}".format(dem))
                logger.debug("  des: {0}".format(des))
                logger.debug("  sky_coord2: {0}".format(sky_coord2))
                logger.debug("  diama: {0}".format(diama))
                logger.debug("  diamb: {0}".format(diamb))
                logger.debug("  name: {0}".format(name))
                logger.debug("  obj_class1: {0}".format(obj_class1))
                logger.debug("  obj_class2: {0}".format(obj_class2))
                logger.debug("  comments: {0}".format(comments))
                logger.debug("  codes: {0}".format(codes))

            for code in codes.split(","):
                entries[code] = [
                    glon, glat, sky_coord,
                    rah, ram, ras, de_sign, ded, dem, des, sky_coord2,
                    diama, diamb,
                    name, obj_class1, obj_class2, comments
                ]
    return entries


def parse_bica_2019_table4(fname="{0}table4.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    # Byte-by-byte Description of file: table4.dat
    # --------------------------------------------------------------------------------
    #    Bytes Format Units Label   Explanations
    # --------------------------------------------------------------------------------
    #    1-  6 F6.1   km/s  U       [-322.7/80]? Heliocentric velocity component,
    #                                positive towards the Galactic anticenter
    #    8- 13 F6.1   km/s  V       [-322.6/164.9]? Heliocentric velocity component,
    #                                positive towards direction of Galactic rotation
    #   15- 20 F6.1   km/s  W       [-249.9/295]? Heliocentric velocity component,
    #                                positive towards the North Galactic Pole
    #   22- 27 F6.2   deg   GLON    [0.46/358.13]? Galactic longitude
    #   29- 34 F6.2   deg   GLAT    [-89.38/77.6]? Galactic latitude
    #   36- 41 F6.2   deg   Diam-a  [0.6/360]? Major diameter or length
    #   43- 48 F6.2   deg   Diam-b  [0.1/360]? Minor diameter or width
    #   50-102 A53    ---   Name    Designation(s)
    #  104-106 A3     ---   Class1  Object classification (G1)
    #  108-113 A6     ---   Class2  Additional object classification (G1)
    #  115-149 A35    ---   Note    Parameters note (1)
    #  151-195 A45    ---   Code    Reference code(s) (see Table 2)
    #  197-264 A68    ---   Com     Comments
    # --------------------------------------------------------------------------------
    # Note (1): The diversity of parameters and their availability precluded a sparse
    #   table format. We give them individually in the parameter field: N (members or
    #   sample), Dk (distance in kpc), a (age in Gyr, or old), f (iron metallity
    #   [Fe/H]) or m (metals [m/H]), Vr (radial velocity in km/s), XG, YG, ZG
    #   (Galactocentric coordinates in kpc), Mv (total absolute V magnitude), mass
    #   (value in solar masses).
    # --------------------------------------------------------------------------------

    nentries, entries = 0, dict()
    with open(fname, "r") as f:
        for line in f.readlines(): nentries += 1
    with open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            u = line[0:6].strip()
            v = line[7:13].strip()
            w = line[14:20].strip()
            glon = line[21:27].strip()
            glat = line[28:34].strip()
            # AttributeError: 'str' object has no attribute 'deg'
            # sky_coord = coord.SkyCoord(
            #     glon, glat, frame="galactic", equinox="J2000", unit=(u.deg, u.deg)
            # )
            diama = line[35:41].strip()
            diamb = line[42:48].strip()
            name = line[49:102].strip()
            obj_class1 = line[103:106].strip()
            obj_class2 = line[107:113].strip()
            note = line[114:149].strip()
            codes = line[150:195].strip()
            comments = line[196:264].strip()

            if debug:
                logger.debug("\nEntry {0}/{1}".format(i+1, nentries))
                logger.debug("  u: {0}".format(u))
                logger.debug("  v: {0}".format(v))
                logger.debug("  w: {0}".format(w))
                logger.debug("  glon: {0}".format(glon))
                logger.debug("  glat: {0}".format(glat))
                # logger.debug("  sky_coord: {0}".format(sky_coord))
                logger.debug("  diama: {0}".format(diama))
                logger.debug("  diamb: {0}".format(diamb))
                logger.debug("  name: {0}".format(name))
                logger.debug("  obj_class1: {0}".format(obj_class1))
                logger.debug("  obj_class2: {0}".format(obj_class2))
                logger.debug("  note: {0}".format(note))
                logger.debug("  codes: {0}".format(codes))
                logger.debug("  comments: {0}".format(comments))

            for code in codes.split(","):
                entries[code] = [
                    u, v, w, glon, glat, diama, diamb, name, obj_class1, obj_class2,
                    note, comments
                ]
    return entries


def parse_bica_2019_table5(fname="{0}table5.dat".format(BASEDIR), debug=False):
    if not os.path.isfile(fname) or not os.path.exists(fname):
        logger.error("ERROR: file not found: {0}".format(fname))
        return

    # Byte-by-byte Description of file: table5.dat
    # --------------------------------------------------------------------------------
    #    Bytes Format Units  Label  Explanations
    # --------------------------------------------------------------------------------
    #    1-  6 F6.2   deg    GLON   Galactic longitude
    #    8- 13 F6.2   deg    GLAT   Galactic latitude
    #   15- 16 I2     h      RAh    Hour of Right Ascension (J2000)
    #   18- 19 I2     min    RAm    Minute of Right Ascension (J2000)
    #   21- 22 I2     s      RAs    Second of Right Ascension (J2000)
    #       24 A1     ---    DE-    Sign of the Declination (J2000)
    #   25- 26 I2     deg    DEd    Degree of Declination (J2000)
    #   28- 29 I2     arcmin DEm    Arcminute of Declination (J2000)
    #   31- 32 I2     arcsec DEs    Arcsecond of Declination (J2000)
    #   34- 39 F6.1   arcmin Diam-a [0.3/1500]? Major axis diameter
    #   41- 45 F5.1   arcmin Diam-b [0.3/900]? Minor axis diameter
    #   47-102 A56    ---    Name   Designation(s)
    #  104-107 A4     ---    Class1 Object classification (G1)
    #  109-119 A11    ---    Class2 Second object classification (1)
    #  121-124 I4     kpc    Dist   [7/2951] Distance
    #  126-130 F5.1   mag    VMag   [-20.8/0]? Total absolute V magnitude (2)
    #  132-139 A8     ---    Memb   Galaxy group membership (3)
    #  141-185 A45    ---    Code   Reference code(s) (see Table 2)
    #  187-261 A75    ---    Com    Census of star clusters & associations,
    #                                and additional comments (4)
    # --------------------------------------------------------------------------------
    # Note (1): Morphological classification and/or UFG (ultra faint galaxy, Mv>-3.5);
    #   we suggest QFG (quite faint galaxies, -7.0<Mv<-3.6).
    # Note (2): MW value is the total absolute B magnitude.
    # Note (3): The MW group corresponds to members typically within 200 kpc from
    #   the Galactic center, while MW neighbors are beyond that, but not as isolated
    #   as Local Group members (see also REF1220).
    # Note (4): This field shows the number of star clusters, young/intermediate age
    #   clusters, globular clusters and associations, according to the reference
    #   code(s). Some galaxy parameters are given, following Table 4: metallicity
    #   [Fe/H] (f), age (a, Gyr), radial velocity (Vr, km/s) and number of studied
    #   stellar members (N).
    # --------------------------------------------------------------------------------

    nentries, entries = 0, dict()
    with open(fname, "r") as f:
        for line in f.readlines(): nentries += 1
    with open(fname, "r") as f:
        for i, line in enumerate(f.readlines()):
            glon = line[0:6].strip()
            glat = line[7:13].strip()
            sky_coord = coord.SkyCoord(
                glon, glat, frame="galactic", equinox="J2000", unit=(u.deg, u.deg)
            )
            rah = line[14:16].strip()
            ram = line[17:19].strip()
            ras = line[20:22].strip()
            de_sign = line[23:24].strip()
            ded = line[24:26].strip()
            dem = line[27:29].strip()
            des = line[30:32].strip()
            sky_coord2 = coord.SkyCoord(
                "{0} {1} {2} {3}{4} {5} {6}".format(
                    rah, ram, ras, "+" if de_sign != "-" else de_sign, ded, dem, des
                ), frame="icrs", equinox="J2000", unit=(u.hourangle, u.deg)
            )
            diama = line[33:39].strip()
            diamb = line[40:45].strip()
            name = line[46:102].strip()
            obj_class1 = line[103:107].strip()
            obj_class2 = line[108:119].strip()
            dist = line[120:124].strip()
            vmag = line[125:130].strip()
            memb = line[131:139].strip()
            codes = line[140:185].strip()
            comments = line[186:261].strip()

            if debug:
                logger.debug("\nEntry {0}/{1}".format(i+1, nentries))
                logger.debug("  glon: {0}".format(glon))
                logger.debug("  glat: {0}".format(glat))
                logger.debug("  sky_coord: {0}".format(sky_coord))
                logger.debug("  rah: {0}".format(rah))
                logger.debug("  ram: {0}".format(ram))
                logger.debug("  ras: {0}".format(ras))
                logger.debug("  de_sign: {0}".format(de_sign))
                logger.debug("  ded: {0}".format(ded))
                logger.debug("  dem: {0}".format(dem))
                logger.debug("  des: {0}".format(des))
                logger.debug("  sky_coord2: {0}".format(sky_coord2))
                logger.debug("  diama: {0}".format(diama))
                logger.debug("  diamb: {0}".format(diamb))
                logger.debug("  name: {0}".format(name))
                logger.debug("  obj_class1: {0}".format(obj_class1))
                logger.debug("  obj_class2: {0}".format(obj_class2))
                logger.debug("  dist: {0}".format(dist))
                logger.debug("  vmag: {0}".format(vmag))
                logger.debug("  memb: {0}".format(memb))
                logger.debug("  codes: {0}".format(codes))
                logger.debug("  comments: {0}".format(comments))

            for code in codes.split(","):
                entries[code] = [
                    glon, glat, sky_coord,
                    rah, ram, ras, de_sign, ded, dem, des, sky_coord2,
                    diama, diamb,
                    name, obj_class1, obj_class2, dist, vmag, memb, comments

                ]
    return entries


if __name__ == "__main__":
    refs = parse_bica_2019_refs(debug=True)

    print("\nTable 2")
    t2 = parse_bica_2019_table2(debug=True)
    for i, (k, v) in enumerate(t2.items()):
        print("{0:<15s}{1}".format(k, v))
        if i > 10: break

    print("\nTable 3")
    t3 = parse_bica_2019_table3(debug=True)
    for i, (k, v) in enumerate(t3.items()):
        print("{0:<15s}{1}".format(k, v))
        if i > 10: break

    print("\nTable 4")
    t4 = parse_bica_2019_table4(debug=True)
    for i, (k, v) in enumerate(t4.items()):
        print("{0:<15s}{1}".format(k, v))
        if i > 10: break

    print("\nTable 5")
    t5 = parse_bica_2019_table5(debug=True)
    for i, (k, v) in enumerate(t5.items()):
        print("{0:<15s}{1}".format(k, v))
        if i > 10: break
