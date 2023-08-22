from django.db import models
from ckeditor import fields


class Problems(models.Model):
    problem_id = models.IntegerField(default=None)
    problem_content_text = models.CharField(max_length=200)
    solution_content_richtext = fields.RichTextField(default="")
    pub_date = models.DateTimeField("date published")
    embeddings_json = models.JSONField(default=None)
    is_newest = models.BooleanField(default=False)

    def __str__(self):
        return f"Problem_ID: {self.problem_id}, " \
               f"Problem: {self.problem_content_text}, " \
               f"Publish Date: {self.pub_date}"

    def save(self, *args, **kwargs):
        if not self.problem_id:
            last_record = Problems.objects.order_by('-problem_id').first()
            if last_record:
                self.problem_id = last_record.problem_id + 1
            else:
                self.problem_id = 1
        super(Problems, self).save(*args, **kwargs)


class Images(models.Model):
    problems_fk = models.ForeignKey(Problems, on_delete=models.CASCADE)
    image_richtext = fields.RichTextField(default="")

    def __str__(self):
        return f"Key: {self.problems_fk.pk}, "


"""
class Users(models.Model):
    user_id = models.
    user_login = models.CharField(max_length=20)
    user_password = models.CharField(max_length=30)
    user_name = models.CharField(max_length=200)
    user_privileges = models.
"""
