# Generated by Django 4.2.4 on 2023-08-29 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems_app', '0010_solution_user_fk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='is_newest',
            field=models.BooleanField(),
        ),
    ]