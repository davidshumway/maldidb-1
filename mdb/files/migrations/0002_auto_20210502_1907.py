# Generated by Django 3.1 on 2021-05-02 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spectra', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='spectra',
            field=models.ManyToManyField(blank=True, to='spectra.Spectra'),
        ),
    ]
