from django.db import models


class Problems(models.Model):
    problem_content_text = models.CharField(max_length=200)
    solution_content_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return f"Problem: {self.problem_content_text}, " \
               f"Solution: {self.solution_content_text}, " \
               f"Publish Date: {self.pub_date}"
