# Generated by Django 2.2.4 on 2019-08-29 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0027_auto_20190829_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='journal',
            field=models.CharField(blank=True, choices=[('aj', 'Astronomical Journal'), ('actaa', 'Acta Astronomica'), ('ara', 'Arkiv for Astronomi'), ('araa', 'Annual Review of Astron and Astrophys'), ('arxiv', 'arXiv e-prints'), ('apj', 'Astrophysical Journal'), ('apjl', 'Astrophysical Journal: Letters'), ('apjs', 'Astrophysical Journal: Supplement'), ('ao', 'Applied Optics'), ('apss', 'Astrophysics and Space Science'), ('astl', 'Astronomy Letters'), ('atsir', 'Astronomicheskij Tsirkulyar'), ('aap', 'Astronomy and Astrophysics'), ('aapr', 'Astronomy and Astrophysics Reviews'), ('aaps', 'Astronomy and Astrophysics), Supplement'), ('azh', 'Astronomicheskii Zhurnal'), ('baas', 'Bulletin of the AAS'), ('baas', 'Bulletin of the American Astronomical Society'), ('caa', 'Chinese Astronomy and Astrophysics'), ('cjaa', 'Chinese Journal of Astronomy and Astrophysics'), ('icarus', 'Icarus'), ('iraj', 'Irish Astronomical Journal'), ('jcap', 'Journal of Cosmology and Astroparticle Physics'), ('jrasc', 'Journal of the RAS of Canada'), ('memras', 'Memoirs of the RAS'), ('mnras', 'Monthly Notices of the RAS'), ('msngr', 'The Messenger'), ('na', 'New Astronomy'), ('nar', 'New Astronomy Review'), ('obs', 'The Observatory'), ('pra', 'Physical Review A: General Physics'), ('prb', 'Physical Review B: Solid State'), ('prc', 'Physical Review C'), ('prd', 'Physical Review D'), ('pre', 'Physical Review E'), ('prl', 'Physical Review Letters'), ('pasa', 'Publications of the Astron. Soc. of Australia'), ('pasp', 'Publications of the ASP'), ('pasj', 'Publications of the ASJ'), ('rmxaa', 'Revista Mexicana de Astronomia y Astrofisica'), ('qjras', 'Quarterly Journal of the RAS'), ('skytel', 'Sky and Telescope'), ('solphys', 'Solar Physics'), ('sovast', 'Soviet Astronomy'), ('ssr', 'Space Science Reviews'), ('zap', 'Zeitschrift fuer Astrophysik'), ('nat', 'Nature'), ('iaucirc', 'IAU Cirulars'), ('aplett', 'Astrophysics Letters'), ('apspr', 'Astrophysics Space Physics Research'), ('bain', 'Bulletin Astronomical Institute of the Netherlands'), ('fcp', 'Fundamental Cosmic Physics'), ('gca', 'Geochimica Cosmochimica Acta'), ('grl', 'Geophysics Research Letters'), ('ibvs', 'Information Bulletin on Variable Stars'), ('jcp', 'Journal of Chemical Physics'), ('jgr', 'Journal of Geophysics Research'), ('jqsrt', 'Journal of Quantitiative Spectroscopy and Radiative Transfer'), ('memsai', 'Mem. Societa Astronomica Italiana'), ('nphysa', 'Nuclear Physics A'), ('pasau', 'Proceedings of the Astronomical Society of Australia'), ('physrep', 'Physics Reports'), ('physscr', 'Physica Scripta'), ('planss', 'Planetary Space Science'), ('procspie', 'Proceedings of the SPIE'), ('vizier', 'VizieR Online Data Catalog')], max_length=8, null=True),
        ),
    ]
