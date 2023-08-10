from django.db import models
from ckeditor import fields


class Problems(models.Model):
    problem_content_text = models.CharField(max_length=200)
    solution_content_richtext = fields.RichTextField(default="")
    pub_date = models.DateTimeField("date published")
    embeddings_json = models.JSONField(default=None)

    def __str__(self):
        return f"Problem: {self.problem_content_text}, " \
               f"Solution: {self.solution_content_richtext}, " \
               f"Publish Date: {self.pub_date}"

"""
class Users(models.Model):
    user_id = models.
    user_login = models.CharField(max_length=20)
    user_password = models.CharField(max_length=30)
    user_name = models.CharField(max_length=200)
    user_privileges = models.
"""
