import datetime
from django.db import models
from django.utils import timezone

# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Paper(models.Model):
    creator = models.CharField(max_length=100, default='')
    creator_weixin_id = models.CharField(max_length=100)
    create_time = models.DateTimeField('date published')
    doi = models.CharField(max_length=100, default='')
    pmid = models.CharField(max_length=20, default='')
    pmcid = models.CharField(max_length=100, default='')
    arxiv_id = models.CharField(max_length=100, default='')
    journal = models.CharField(max_length=200, default='')
    publish_year = models.CharField(max_length=10, default='')
    title = models.CharField(max_length=500, default='')
    comments = models.CharField(max_length=65536, default='')
    labels = models.ManyToManyField(Label)
    authors = models.CharField(max_length=65536, default='') # json format
    abstract = models.CharField(max_length=65536, default='')
    urls = models.CharField(max_length=65536, default='') # text of lines
    is_private = models.BooleanField(default=True)
    full_text = models.FileField(default='')
    def __str__(self):
        return self.creator + ' - ' + self.publish_year + ' - ' + self.journal + ' - ' + self.title
