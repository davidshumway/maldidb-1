# Generated by Django 3.1 on 2021-05-12 00:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20210503_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='library',
            name='lab_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.labgroup'),
        ),
    ]
