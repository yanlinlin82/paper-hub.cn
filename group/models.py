from django.db import models
from django.utils import timezone

from view.models import User, Paper

class Group(models.Model):
    name = models.CharField(max_length=64, default='')
    display_name = models.CharField(max_length=128, default='')
    desc = models.CharField(max_length=2000, default='')
    create_time = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(User)
    papers = models.ManyToManyField(Paper)
    def __str__(self):
        return self.display_name + " (" + self.name + ")"
