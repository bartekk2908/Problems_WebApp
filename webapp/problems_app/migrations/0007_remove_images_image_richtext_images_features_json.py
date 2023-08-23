# Generated by Django 4.2.4 on 2023-08-23 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems_app', '0006_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='images',
            name='image_richtext',
        ),
        migrations.AddField(
            model_name='images',
            name='features_json',
            field=models.JSONField(default=None),
        ),
    ]
