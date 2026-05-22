from django.db import models

# Create your models here.
class Detainee(models.Model):
    name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    mothers_name = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    age = models.IntegerField(null=True)
    nicknames = models.CharField(max_length=500, null=True)
    fake_names = models.CharField(max_length=500, null=True)
    marital_status = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255)
    sexual_preferences = models.CharField(max_length=255,null=True)
    ethnicity = models.CharField(max_length=255, null=True)
    schooling = models.CharField(max_length=255, null=True)
    occupation = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    origin_country = models.CharField(max_length=255, null=True)
    origin_state = models.CharField(max_length=255, null=True)
    origin_city = models.CharField(max_length=255, null=True)
    notes = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Phones(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    phone_number = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FakeNames(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    mothers_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class Nicknames(models.Model):
#     detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
#     discriminator = models.CharField(max_length=255)
#     nickname = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class VisitorsRegistry(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    mothers_name = models.CharField(max_length=255, null=True)
    visit_date = models.CharField(max_length=255)
    detainee_relationship = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentsRegistry(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    amount = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Addresses(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    discriminator = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    exterior_number = models.CharField(max_length=255, null=True)
    interior_number = models.CharField(max_length=255, null=True)
    street = models.CharField(max_length=255, null=True)
    colony = models.CharField(max_length=255, null=True)
    locality = models.CharField(max_length=255, null=True)
    municipality = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TattooClasifications(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    clasification = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DistinguishingMarks(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    tattoo_location = models.ForeignKey(TattooClasifications, on_delete=models.CASCADE, null=False)
    tattoo_clasification = models.CharField(default=True, max_length=255)
    tattoo_description = models.CharField(default=True, max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Photos(models.Model):
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, null=False)
    image_path = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


