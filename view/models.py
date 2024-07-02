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
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user', null=True)
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
    journal = models.CharField(max_length=256, default='', blank=True)
    pub_date = models.CharField(max_length=64, default='', blank=True)
    pub_year = models.IntegerField(blank=True, null=True, default=None)
    title = models.CharField(max_length=4096, default='')
    authors = models.CharField(max_length=65536, default='', blank=True)
    institutes = models.CharField(max_length=65536, default='', blank=True)
    abstract = models.CharField(max_length=65536, default='', blank=True)
    keywords = models.CharField(max_length=65536, default='', blank=True)
    urls = models.CharField(max_length=65536, default='', blank=True)

    doi = models.CharField(max_length=128, default='', blank=True)
    pmid = models.CharField(max_length=128, default='', blank=True)
    arxiv_id = models.CharField(max_length=128, default='', blank=True)
    pmcid = models.CharField(max_length=128, default='', blank=True)
    cnki_id = models.CharField(max_length=128, default='', blank=True) # CNKI CJFD ID

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
    type = models.CharField(max_length=20, default='read') # keyword, author, institute, journal, cite
    value = models.CharField(max_length=100, default='', blank=True)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    memo = models.CharField(max_length=2000, default='', blank=True)

class Recommendation(models.Model): # recommended by system (daily automatically)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    delete_time = models.DateTimeField(null=True, default=None) # if not None, it means in Trash

class RecommendationDetails(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name='details')
    recommend_time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, default='read') # keyword, author, institute, journal, cite
    value = models.CharField(max_length=100, default='', blank=True)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    memo = models.CharField(max_length=2000, default='', blank=True)

class Review(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)

    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    delete_time = models.DateTimeField(null=True, default=None) # if not None, it means in Trash

    comments = models.CharField(max_length=65536, default='', blank=True)
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
