from rest_framework import serializers
from detainees.models import *
# from .models import Role

# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Role
#         fields=('id','name','color','created_at','updated_at')
#         read_only_fields=['created_at']

#     def create(self,validated_data):
#         return Role.objects.create(**validated_data)



class DetaineesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detainee
        fields =['id', 'name','fathers_name', 'mothers_name', 'birth_date','age', 'nicknames','fake_names', 'marital_status', 'gender', 'sexual_preferences', 'ethnicity', 'schooling', 'occupation', 'nationality', 'origin_country', 'origin_state', 'origin_city', 'created_at', 'updated_at']

class PhonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phones
        fields =['detainee','phone_number', 'description', 'created_at','updated_at']
    
class FakeNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FakeNames
        fields =['detainee','name', 'fathers_name', 'mothers_name', 'created_at', 'updated_at']

# class NicknamesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Nicknames
#         fields =['detainee','discriminator', 'nickname', 'created_at', 'updated_at']

# class CallsRegistrySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CallsRegistry
#         fields =['detainee','name', 'fathers_name', 'mothers_name', 'phone_number', 'detainee_relationship', 'created_at', 'updated_at']

class VisitorsRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorsRegistry
        fields =['detainee','name', 'fathers_name', 'mothers_name', 'visit_date', 'detainee_relationship', 'created_at', 'updated_at']

class PaymentsRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentsRegistry
        fields =['detainee','amount', 'created_at', 'updated_at']

class AddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields =['detainee','discriminator','country','postal_code','exterior_number','interior_number','street','colony','locality','municipality','state','created_at','updated_at']

class TattooClasificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TattooClasifications
        fields =['detainee','clasification','created_at','updated_at']

class DistinguishingMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistinguishingMarks
        fields =['detainee','tattoo_location','tattoo_clasification','tattoo_description','created_at','updated_at']

class PhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields =['detainee','image_path', 'created_at','updated_at']
