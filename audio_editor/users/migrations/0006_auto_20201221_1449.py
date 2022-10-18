# Generated by Django 3.1.3 on 2020-12-21 14:49

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20201215_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='avatar_placeholder.png', upload_to=users.models.get_user_avatars_path),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bg_picture',
            field=models.ImageField(blank=True, default='profile_bg_placeholder.jpeg', upload_to=users.models.get_user_profile_bg_img_path),
        ),
    ]
