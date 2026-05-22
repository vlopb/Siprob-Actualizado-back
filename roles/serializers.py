from rest_framework import serializers
from .models import Role
from django.contrib.auth import get_user_model, authenticate


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields= '__all__'
        read_only_fields=['created_at']
        ref_name = 'Role'

    # def create(self,validated_data):
    #     return Role.objects.create(**validated_data)

