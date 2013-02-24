from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.

class Content(models.Model):
    
    path = models.CharField(max_length=1000, unique=True, db_index=True)
    html_content = models.TextField(blank=True)
    template = models.CharField(max_length=200, blank=True)
    allowed_groups = models.ManyToManyField(Group, blank=True)
    allowed_users = models.ManyToManyField(User, blank=True)
    public = models.BooleanField(default=False)
    creation_time = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, null=True, blank=True, related_name="author")
    
    def __unicode__(self):
        return "%s" % self.path 

    class Meta:
        verbose_name = "Content"
        ordering = ['path']
