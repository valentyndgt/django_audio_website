# Generated by Django 3.1.3 on 2021-01-11 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0006_auto_20210110_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='duration',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='track',
            name='name',
            field=models.CharField(max_length=1024),
        ),
    ]
