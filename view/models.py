import datetime
from django.db import models
from django.utils import timezone

# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Paper(models.Model):
    creator = models.CharField(max_length=100)
    creator_weixin_id = models.CharField(max_length=100)
    create_time = models.DateTimeField('date published')
    doi = models.CharField(max_length=100)
    pmid = models.CharField(max_length=20)
    pmcid = models.CharField(max_length=100)
    arxiv_id = models.CharField(max_length=100)
    journal = models.CharField(max_length=200)
    publish_year = models.CharField(max_length=10)
    title = models.CharField(max_length=500)
    comments = models.CharField(max_length=65536)
    labels = models.ManyToManyField(Label)
    def __str__(self):
        return self.creator + ' - ' + self.publish_year + ' - ' + self.journal + ' - ' + self.title
