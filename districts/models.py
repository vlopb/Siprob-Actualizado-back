from django.db import models
# Create your models here.
class District(models.Model):
    name = models.CharField(default='', max_length=255)    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)