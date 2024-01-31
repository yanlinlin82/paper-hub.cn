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
    debug_mode = models.BooleanField(default=False)

    def __str__(self):
        s = self.nickname
        if self.wx_openid:
            s += ' (openid:' + self.wx_openid + ')'
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
    # creation info
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
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

class GroupProfile(models.Model):
    name = models.CharField(max_length=64, default='')
    display_name = models.CharField(max_length=128, default='')
    desc = models.CharField(max_length=2000, default='')
    create_time = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(UserProfile)
    papers = models.ManyToManyField(Paper)
    def __str__(self):
        return self.display_name + " (" + self.name + ")"

class CustomCheckInInterval(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    deadline = models.DateTimeField()
