# Generated by Django 5.1.4 on 2024-12-19 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_apmo', '0008_devotion_events_bookmark_download_favourite'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='images/category/'),
        ),
    ]