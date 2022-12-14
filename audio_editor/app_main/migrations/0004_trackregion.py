# Generated by Django 3.1.3 on 2021-01-05 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0003_track'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_start', models.IntegerField()),
                ('time_end', models.IntegerField()),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_main.track')),
            ],
        ),
    ]
