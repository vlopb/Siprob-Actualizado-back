from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

# Create your models here.
# class RoleManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_active=True)


class Role(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    