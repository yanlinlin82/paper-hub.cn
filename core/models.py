from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid
from datetime import timedelta
from paperhub import settings
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_user_profile', null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=100, default='', blank=True)
    wx_openid = models.CharField(max_length=100, default='', blank=True)
    wx_unionid = models.CharField(max_length=100, default='', blank=True)
    debug_mode = models.BooleanField(default=False)

    def __str__(self):
        s = self.nickname
        if self.wx_openid:
            s += ' (openid:' + self.wx_openid + ')'
        if self.wx_unionid:
            s += ' (unionid:' + self.wx_unionid + ')'
        return s

class UserAlias(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='primary')
    alias = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='alias_for')

    class Meta:
        unique_together = ('user', 'alias')

    def clean(self):
        if self.user == self.alias:
            raise ValidationError("User cannot alias themselves.")
        if UserAlias.objects.filter(alias=self.user).exists():
            raise ValidationError("A primary user cannot be an alias to another user.")
        if UserAlias.objects.filter(user=self.alias).exists():
            raise ValidationError("An alias cannot be a primary user.")

    def save(self, *args, **kwargs):
        self.clean()
        super(UserAlias, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + ' <-> ' + str(self.alias)

class UserSession(models.Model):
    CLIENT_TYPES = (
        ('website', '网页端'),
        ('weixin', '微信小程序'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    client_type = models.CharField(max_length=10, choices=CLIENT_TYPES)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.nickname}: {self.token} - {self.get_client_type_display()}"

class Paper(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True, db_index=True)

    title = models.CharField(max_length=4096, default='', db_index=True)
    journal = models.CharField(max_length=256, default='', blank=True, db_index=True)
    pub_date = models.CharField(max_length=64, default='', blank=True)
    pub_year = models.IntegerField(blank=True, null=True, default=None, db_index=True)
    authors = models.CharField(max_length=1024*1024, default='', blank=True)
    affiliations = models.CharField(max_length=1024*1024, default='', blank=True)
    abstract = models.CharField(max_length=1024*1024, default='', blank=True)
    keywords = models.CharField(max_length=1024*1024, default='', blank=True)
    urls = models.CharField(max_length=1024*1024, default='', blank=True)

    doi = models.CharField(max_length=128, default='', blank=True, db_index=True)
    pmid = models.CharField(max_length=128, default='', blank=True, db_index=True)
    arxiv_id = models.CharField(max_length=128, default='', blank=True, db_index=True)
    pmcid = models.CharField(max_length=128, default='', blank=True, db_index=True)
    cnki_id = models.CharField(max_length=128, default='', blank=True, db_index=True) # CNKI CJFD ID

    language = models.CharField(max_length=20, default='eng') # eng, chi, etc.

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.pub_year}, {self.journal}, {self.title}'

class PaperTranslation(models.Model):
    paper = models.OneToOneField(Paper, on_delete=models.CASCADE, related_name='translation')
    title_cn = models.CharField(max_length=4096, default='', blank=True)
    abstract_cn = models.CharField(max_length=65536, default='', blank=True)

class Label(models.Model): # every user has his own labels
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default='')
    color = models.CharField(max_length=7, default='#B6CFF5') # light blue
    desc = models.CharField(max_length=2000, default='')

class PaperTracking(models.Model): # every user has his own paper tracking rules
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, default='read') # keyword, author, affiliation, journal, cite
    value = models.CharField(max_length=100, default='', blank=True)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    memo = models.CharField(max_length=2000, default='', blank=True)

class Recommendation(models.Model): # recommended by system (daily automatically)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    read_time = models.DateTimeField(null=True, default=None, db_index=True) # None means unread
    source = models.CharField(max_length=100, default='') # eg. 'pubmed24n1453.20240628'
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, db_index=True)
    labels = models.ManyToManyField(Label, blank=True, related_name='recommendations')

class Review(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)

    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now) # not using 'auto_now_add' because we need to update it, when admin adding reviews for users
    update_time = models.DateTimeField(default=timezone.now) # same as above
    delete_time = models.DateTimeField(null=True, default=None) # if not None, it means in Trash

    comment = models.CharField(max_length=1024*1024, default='', blank=True)
    labels = models.ManyToManyField(Label, blank=True, related_name='reviews')

    def __str__(self):
        return f'{self.creator.nickname}: {self.paper}'

class GroupProfile(models.Model):
    name = models.CharField(max_length=64, default='')
    display_name = models.CharField(max_length=128, default='')
    desc = models.CharField(max_length=2000, default='')
    create_time = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(UserProfile)
    reviews = models.ManyToManyField(Review)
    def __str__(self):
        return self.display_name + " (" + self.name + ")"

class CustomCheckInInterval(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    deadline = models.DateTimeField()

class PubMedIndex(models.Model):
    source = models.IntegerField()
    index = models.IntegerField()
    doi = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    pmid = models.BigIntegerField(unique=True, null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['doi'], name='core_doi_idx'),
            models.Index(fields=['pmid'], name='core_pmid_idx'),
        ]

    def __str__(self):
        return f'{self.source}-{self.index}: {self.doi} ({self.pmid})'
