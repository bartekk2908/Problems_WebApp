# Generated by Django 4.2.4 on 2023-08-21 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems_app', '0004_problems_problem_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='problems',
            name='is_newest',
            field=models.BooleanField(default=False),
        ),
    ]
