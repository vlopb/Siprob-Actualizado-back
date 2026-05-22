from django.db import models

# Create your models here.
class Shift(models.Model):
    is_active = models.BooleanField(default=True)
    start_hour = models.CharField(max_length=255)    
    end_hour = models.CharField(max_length=255)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
