# Generated by Django 2.2.4 on 2019-08-23 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0014_remove_reference_astro_objects'),
    ]

    operations = [
        migrations.AddField(
            model_name='astroobject',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='astroobject',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='astroobject',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_astro_objects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='astroobjectclassification',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='astroobjectclassification',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='astroobjectclassification',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_astro_object_classifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auxiliary',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='auxiliary',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='auxiliary',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_auxiliaries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='observation',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='observation',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='observation',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_observations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='parameter',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parameter',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='parameter',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_parameters', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rank',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rank',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='rank',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_ranks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reference',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reference',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Last Changed'),
        ),
        migrations.AddField(
            model_name='reference',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='has_changed_references', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='auxiliary',
            name='astro_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auxiliaries', to='catalogue.AstroObject'),
        ),
        migrations.AlterField(
            model_name='auxiliary',
            name='reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auxiliaries', to='catalogue.Reference'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='astro_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='catalogue.AstroObject'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='parameter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='catalogue.Parameter'),
        ),
        migrations.AlterField(
            model_name='observation',
            name='reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='catalogue.Reference'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='astro_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='catalogue.AstroObject'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='catalogue.Reference'),
        ),
        migrations.AlterField(
            model_name='rank',
            name='observation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ranks', to='catalogue.Observation'),
        ),
    ]