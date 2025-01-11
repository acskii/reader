from django.db import models
from django.contrib.auth.models import User

class VisitHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visited')
    title = models.CharField(max_length=100)
    series_url = models.CharField(max_length=400)
    preview_url = models.CharField(max_length=400)
    website_option = models.PositiveSmallIntegerField()
    logo = models.CharField(max_length=400)
    last_visited = models.DateTimeField(auto_now=True)
    last_read = models.CharField(max_length=100)