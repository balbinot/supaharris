# Generated by Django 2.1.5 on 2019-02-13 18:31

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auxiliary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fpath', models.FilePathField(blank=True, null=True, path='/static')),
                ('furl', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GlobularCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, max_length=64, unique=True)),
                ('altname', models.CharField(blank=True, max_length=64, null=True, verbose_name='Alternative Name')),
            ],
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('val', models.FloatField(blank=True, null=True, verbose_name='Value')),
                ('sigup', models.FloatField(blank=True, null=True, verbose_name='Sigma up')),
                ('sigdown', models.FloatField(blank=True, null=True, verbose_name='Sigma down')),
                ('cname', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.GlobularCluster')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('pname', models.CharField(max_length=64, primary_key=True, serialize=False, unique=True, verbose_name='Parameter')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('unit', models.CharField(help_text='Must comply with astropy.unit', max_length=256, verbose_name='Unit')),
                ('scale', models.FloatField(help_text='Scale by which parameters must be multiplied by', max_length=256, verbose_name='Scale')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ptype', models.CharField(blank=True, max_length=256, null=True, verbose_name='Type of profile')),
                ('profile', jsonfield.fields.JSONField(default=dict, verbose_name='Profile')),
                ('modpars', jsonfield.fields.JSONField(default=dict, verbose_name='Model parameters')),
                ('mtype', models.CharField(blank=True, max_length=256, null=True, verbose_name='Model flavour')),
                ('cname', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.GlobularCluster')),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('comp', models.CharField(blank=True, max_length=64, null=True, verbose_name='Compilation name')),
                ('oid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Observation')),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ads_url', models.URLField(help_text="Please insert the ADS url. All other paramters will automatically be retrieved on save!. For example: 'http://adsabs.harvard.edu/abs/1996AJ....112.1487H'", max_length=256, unique=True, verbose_name='ADS url')),
                ('bib_code', models.CharField(blank=True, max_length=24, null=True, verbose_name='Bibliographic Code [ADS]')),
                ('slug', models.SlugField(blank=True, max_length=64, unique=True)),
                ('authors', models.TextField(blank=True, max_length=1024, null=True)),
                ('first_author', models.CharField(blank=True, max_length=128, null=True)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('journal', models.CharField(blank=True, max_length=128, null=True)),
                ('doi', models.CharField(blank=True, max_length=32, null=True, verbose_name='DOI')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Year of publication')),
                ('month', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], null=True, verbose_name='Month of publication')),
                ('volume', models.CharField(blank=True, max_length=8, null=True)),
                ('pages', models.CharField(blank=True, max_length=16, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='rname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Reference'),
        ),
        migrations.AddField(
            model_name='observation',
            name='pname',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.Parameter'),
        ),
        migrations.AddField(
            model_name='observation',
            name='rname',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.Reference'),
        ),
        migrations.AddField(
            model_name='auxiliary',
            name='cname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.GlobularCluster'),
        ),
        migrations.AddField(
            model_name='auxiliary',
            name='rname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Reference'),
        ),
    ]
