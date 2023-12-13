from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser

class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE,
                                     related_name='custom_user', null=True)
    create_time = models.DateTimeField(default=timezone.now)
    nickname = models.CharField(max_length=100, default='', blank=True)
    wx_openid = models.CharField(max_length=100, default='', blank=True)
    def __str__(self):
        return self.nickname

class Paper(models.Model):
    # creation info
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    delete_time = models.DateTimeField(null=True, default=None) # if not None, it means in Trash

    # paper info
    journal = models.CharField(max_length=200, default='', blank=True)
    pub_year = models.IntegerField(blank=True, null=True, default=None)
    title = models.CharField(max_length=500, default='')
    authors = models.CharField(max_length=4000, default='', blank=True)
    abstract = models.CharField(max_length=4000, default='', blank=True)
    urls = models.CharField(max_length=1000, default='', blank=True)

    # paper id
    doi = models.CharField(max_length=100, default='', blank=True)
    pmid = models.CharField(max_length=20, default='', blank=True)
    arxiv_id = models.CharField(max_length=30, default='', blank=True)
    pmcid = models.CharField(max_length=100, default='', blank=True)
    cnki_id = models.CharField(max_length=100, default='', blank=True) # CNKI CJFD ID

    # user comments
    comments = models.CharField(max_length=65536, default='', blank=True)

    def __str__(self):
        return self.creator.nickname + ': ' + str(self.pub_year) + ' - ' + self.journal + ' - ' + self.title
