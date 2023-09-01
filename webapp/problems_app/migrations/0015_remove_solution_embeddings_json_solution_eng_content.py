# Generated by Django 4.2.4 on 2023-09-01 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems_app', '0014_alter_solution_embeddings_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='embeddings_json',
        ),
        migrations.AddField(
            model_name='solution',
            name='eng_content',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
