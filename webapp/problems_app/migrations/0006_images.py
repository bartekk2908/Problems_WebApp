# Generated by Django 4.2.4 on 2023-08-22 08:46

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problems_app', '0005_problems_is_newest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_richtext', ckeditor.fields.RichTextField(default='')),
                ('problems_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_app.problems')),
            ],
        ),
    ]
