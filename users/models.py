from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.apps import apps
from roles.models import Role
from shifts.models import Shift
from districts.models import District

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        extra_fields.setdefault("is_active", True)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.save(using=self.db)
        return user

# class District(models.Model):
#     name = models.CharField(max_length=55)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class Role(models.Model):
#     name = models.CharField(max_length=255)
#     color = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Shift(models.Model):
#     start_hour = models.CharField(max_length=255)
#     end_hour = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
class User(AbstractBaseUser, PermissionsMixin):
    is_active = models.BooleanField(default=True)
    discriminator = models.CharField(max_length=255)
    #shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=False)
    #role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False)
    district_default = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    #districts = models.ManyToManyField(District, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    employee_number = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    fathers_name = models.CharField(max_length=255, null=True, blank=True)
    mothers_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True)
    medical_cedula = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    detainee_module = models.BooleanField(default=False, null=True)
    detainee_show = models.BooleanField(default=False, null=True)
    detainee_create = models.BooleanField(default=False, null=True)
    detainee_edit = models.BooleanField(default=False, null=True)
    detainee_delete = models.BooleanField(default=False, null=True)    
    detention_create = models.BooleanField(default=False, null=True)
    detention_edit = models.BooleanField(default=False, null=True)
    detention_delete = models.BooleanField(default=False, null=True)
    medic_show = models.BooleanField(default=False, null=True)
    medic_create = models.BooleanField(default=False, null=True)
    medic_edit = models.BooleanField(default=False, null=True)
    medic_delete = models.BooleanField(default=False, null=True)
    cell_show = models.BooleanField(default=False, null=True)
    cell_create = models.BooleanField(default=False, null=True)
    cell_edit = models.BooleanField(default=False, null=True)
    cell_delete = models.BooleanField(default=False, null=True)
    actions_show = models.BooleanField(default=False, null=True)
    actions_create = models.BooleanField(default=False, null=True)
    actions_edit = models.BooleanField(default=False, null=True)
    actions_delete = models.BooleanField(default=False, null=True)
    records_module = models.BooleanField(default=False, null=True)
    car_show = models.BooleanField(default=False, null=True)
    car_create = models.BooleanField(default=False, null=True)
    car_edit = models.BooleanField(default=False, null=True)
    car_delete = models.BooleanField(default=False, null=True)
    object_show = models.BooleanField(default=False, null=True)
    object_create = models.BooleanField(default=False, null=True)
    object_edit = models.BooleanField(default=False, null=True)
    object_delete = models.BooleanField(default=False, null=True)
    reports_module = models.BooleanField(default=False, null=True)
    report_detainee_show = models.BooleanField(default=False, null=True)
    report_detainee_create = models.BooleanField(default=False, null=True)
    report_detainee_edit = models.BooleanField(default=False, null=True)
    report_detainee_delete = models.BooleanField(default=False, null=True)
    report_car_show = models.BooleanField(default=False, null=True)
    report_car_create = models.BooleanField(default=False, null=True)
    report_car_edit = models.BooleanField(default=False, null=True)
    report_car_delete = models.BooleanField(default=False, null=True)
    report_agent_show = models.BooleanField(default=False, null=True)
    report_agent_create = models.BooleanField(default=False, null=True)
    report_agent_edit = models.BooleanField(default=False, null=True)
    report_agent_delete = models.BooleanField(default=False, null=True)
    report_cell_show = models.BooleanField(default=False, null=True)
    report_cell_create = models.BooleanField(default=False, null=True)
    report_cell_edit = models.BooleanField(default=False, null=True)
    report_cell_delete = models.BooleanField(default=False, null=True)
    users_module = models.BooleanField(default=False, null=True)
    user_show = models.BooleanField(default=False, null=True)
    user_create = models.BooleanField(default=False, null=True)
    user_edit = models.BooleanField(default=False, null=True)
    user_delete = models.BooleanField(default=False, null=True)
    temporary_password = models.CharField(max_length=128, blank=True, null=True)
    password_expiration = models.DateTimeField(blank=True, null=True)


    user_permissions = None
    groups = None
    is_superuser = None

    objects = UserManager()

    USERNAME_FIELD = "username"

class UserDistricts(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)