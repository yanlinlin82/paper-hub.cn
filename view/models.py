import datetime
from email.policy import default
from statistics import mode
from django.db import models
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=100, default='') # unique symbol, link to authorization table
    name = models.CharField(max_length=100, default='')
    nickname = models.CharField(max_length=100, default='')
    weixin_id = models.CharField(max_length=100, default='')
    create_time = models.DateTimeField(default=timezone.now)
    last_login_time = models.DateTimeField(null=True, default=None)
    def __str__(self):
        return self.nickname

class Label(models.Model):
    name = models.CharField(max_length=200, default='')
    desc = models.CharField(max_length=2000, default='')
    owner = models.CharField(max_length=100, default='') # link to User.username
    def __str__(self):
        return self.name

class Paper(models.Model):
    # creation info
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    delete_time = models.DateTimeField(null=True, default=None)

    # index id
    doi = models.CharField(max_length=100, default='')
    pmid = models.CharField(max_length=20, default='')
    arxiv_id = models.CharField(max_length=30, default='')
    pmcid = models.CharField(max_length=100, default='')
    cnki_id = models.CharField(max_length=100, default='') # CNKI CJFD ID

    # paper info
    journal = models.CharField(max_length=200, default='')
    pub_date = models.DateField(blank=True, null=True, default=None)
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

class CrossRefCache(models.Model):
    DOI = 'DOI'
    PMID = 'PMID'
    PMCID = 'PMCID'
    arXiv = 'arXiv'
    CNKI = 'CNKI'
    CROSS_REF_CHOICES = [
        (DOI, 'DOI'),
        (PMID, 'PMID'),
        (PMCID, 'PMCID'),
        (arXiv, 'arXiv'),
        (CNKI, 'CNKI'),
    ]
    type = models.CharField(max_length=10, choices=CROSS_REF_CHOICES, default=DOI)
    key = models.CharField(max_length=100, default='')
    value = models.CharField(max_length=100000)

    def __str__(self):
        return self.type + ': ' + self.value

class Collection(models.Model):
    name = models.CharField(max_length=100, default="")
    slug = models.CharField(max_length=200, default="")
    desc = models.CharField(max_length=50000, default="")
    parent = models.IntegerField(default=0)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)

    papers = models.ManyToManyField(Paper)
    order_fields = models.CharField(max_length=1000, default="")

    is_private = models.BooleanField(default=True)
    members = models.ManyToManyField(User, related_name='members')

    def __str__(self):
        return self.name + ' (with ' + str(self.papers.count()) + ' paper(s), owned by ' + str(self.owner) + ')'
