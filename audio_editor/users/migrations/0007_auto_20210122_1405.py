# Generated by Django 3.1.3 on 2021-01-22 14:05

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20201221_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.get_user_avatars_path),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bg_picture',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.get_user_profile_bg_img_path),
        ),
    ]
