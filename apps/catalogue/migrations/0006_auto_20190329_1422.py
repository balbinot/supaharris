# Generated by Django 2.1.5 on 2019-03-29 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20190225_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='ads_url',
            field=models.URLField(help_text="Please insert the ADS/arXiv url. All other paramters will automatically be retrieved on save!. For example: 'https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H'", max_length=254, unique=True, verbose_name='ADS url'),
        ),
    ]
