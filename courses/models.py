from django.db import models
from django.contrib.auth import get_user_model
class Developer(models.Model):
    user = models.ForeignKey(get_user_model())
    primary_skill = models.CharField(max_length=10, blank=True)
    def __str__(self):
        return self.user.username


class Project(models.Model):
    name = models.CharField(max_length=100)
    summary = models.TextField()
    developers = models.ManyToManyField(Developer)

    def __str__(self):
        return self.name
