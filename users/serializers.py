from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from districts.models import District
from roles.models import Role
from shifts.models import Shift
from django.contrib.auth.hashers import make_password
from .models import UserDistricts
# from .models import Role

# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Role
#         fields=('id','name','color','created_at','updated_at')
#         read_only_fields=['created_at']

#     def create(self,validated_data):
#         return Role.objects.create(**validated_data)

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('id', 'start_hour','end_hour')
        ref_name = 'UserShift'

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id','color','name')
        ref_name = 'UserRole'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name')
        ref_name = 'UserDistricts'

class UserDistrictsSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    class Meta:
        model = UserDistricts
        fields = '__all__'
        ref_name = 'UserDistrictsDistricts'

    # def create(self, validated_data):
    #     district_data = validated_data.pop('district')
    #     district_instance = District.objects.get(pk=district_data['id'])
    #     user_districts_instance = UserDistricts.objects.create(district=district_instance, **validated_data)
    #     return user_districts_instance

class RetrieveUserSerializer(serializers.ModelSerializer):     

    class Meta:
        model = get_user_model()
        # fields =['id','employee_number','username','password', 'name', 'fathers_name','mothers_name', 'shift', 'role', 'is_active']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'districts': {'required': False},'temporary_password':{'write_only':True},'password_expiration':{'write_only':True}}
    # def update(self, instance, validated_data):
    #     # Clear existing many-to-many relations
        

    #     # Add new many-to-many relations from the 'districts' field in the request
    #     district_ids = validated_data.get('districts', [])
    #     instance.districts.add(*district_ids)

    #     # Continue with the regular update logic
    #     return super().update(instance, validated_data)
    

class AddUserSerializer(serializers.ModelSerializer):           
    district_default = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
      # Replace YourShiftModel with your actual model
    #districts = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), many=True)    
    class Meta:
        model = get_user_model()
        # fields =['id','employee_number','username','password', 'name', 'fathers_name','mothers_name', 'shift', 'role', 'is_active']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'districts': {'required': False}}

    
    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data.get('password'))        
        # Create and return the user instance
        return super().create(validated_data)    
    

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(style={'input_type':'password'})

    def validate(self,data):
        username=data.get('username')
        password=data.get('password')
        user=authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        if not user:
            raise serializers.ValidationError('Nombre de usuario y contraseña requeridas',code='authorization')
        data['user']=user
        return data


    

