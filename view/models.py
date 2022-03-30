import datetime
from email.policy import default
from django.db import models
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    weixin_id = models.CharField(max_length=100)
    create_time = models.DateTimeField(default=timezone.now)
    last_login_time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.nickname

class Label(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Paper(models.Model):
    # creation info
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)

    # index id
    doi = models.CharField(max_length=100, default='')
    pmid = models.CharField(max_length=20, default='')
    arxiv_id = models.CharField(max_length=30, default='')
    pmcid = models.CharField(max_length=100, default='')
    cnki_id = models.CharField(max_length=100, default='') # CNKI CJFD ID

    # paper info
    journal = models.CharField(max_length=200, default='')
    pub_date = models.DateField(blank=True, default=None)
    title = models.CharField(max_length=500, default='')
    authors = models.CharField(max_length=4000, default='')
    abstract = models.CharField(max_length=4000, default='')
    keywords = models.CharField(max_length=1000, default='')
    urls = models.CharField(max_length=1000, default='')
    full_text = models.FileField(default='')
    is_preprint = models.BooleanField(default=False)
    is_review = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)

    # user comments
    is_private = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)
    comments = models.CharField(max_length=65536, default='')
    labels = models.ManyToManyField(Label)

    def pub_year(self):
        return self.pub_date.year if self.pub_date else ''

    def __str__(self):
        return self.creator.nickname + ': ' + str(self.pub_year()) + ' - ' + self.journal + ' - ' + self.title
