# Generated by Django 5.1.4 on 2024-12-09 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_apmo', '0004_playlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='user',
        ),
    ]
