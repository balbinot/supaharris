# Generated by Django 2.2.4 on 2019-08-12 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20190507_1106'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GlobularCluster',
            new_name='AstroObject',
        ),
        migrations.RenameField(
            model_name='reference',
            old_name='clusters',
            new_name='astro_objects',
        ),
    ]
