import random
import string
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, authentication, permissions, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from users.serializers import AddUserSerializer, AuthTokenSerializer, RetrieveUserSerializer, RolesSerializer, ShiftSerializer,UserDistrictsSerializer
from users.models import User, UserDistricts
from shifts.models import Shift
from roles.models import Role
from districts.models import District
from drf_yasg import openapi
from django.forms.models import model_to_dict
import json
import jwt
from datetime import datetime, timedelta, timezone
from django.utils import timezone
import os
from dotenv import load_dotenv
from django.conf import settings
load_dotenv()
# from users.hashers import XorPasswordHasher

from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = AddUserSerializer
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset
        self.check_object_permissions(self.request, obj)
        return obj
    
    @swagger_auto_schema(
        operation_summary="Lists all users",
        manual_parameters=[
            openapi.Parameter(
                "discriminator",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="User type or avoid it to get all users",
            ),
        ],
        operation_description="This endpoint lists all the users stored on database.",
        tags=["Users"],
    )
    def get(self, request, *args, **kwargs):        
        users = User.objects.filter(is_active=True)        
        discriminator = request.GET.get('discriminator', None)
        if discriminator:
            users = users.filter(discriminator=discriminator)

        # Retrieve distinct district_default values from filtered users
        district_default_values = users.values_list('district_default__id', flat=True).distinct()

        # Convert district_default_values to a list of integers
        district_default_values = list(map(int, district_default_values))

        # Filter districts based on the distinct district_default values
        filtered_districts = District.objects.filter(id__in=district_default_values)
        users = users.order_by('fathers_name')
        formatted_results=[]
        for user in users:
            new_object={                
                'username': user.username,                
                'is_active':user.is_active,
                'discriminator': user.discriminator,
                'name': user.name,
                'fathers_name': user.fathers_name,
                'mothers_name': user.mothers_name,
                'email': user.email,
                'employee_number': user.employee_number,
                # 'district_default': user.district_default,
                # 'detainee_module':user.detainee_module,
                # 'detainee_show':user.detainee_show,
                # 'detainee_create':user.detainee_create,
                # 'detainee_edit':user.detainee_edit,
                # 'detainee_delete':user.detainee_delete,
                # 'detention_create':user.detention_create,
                # 'detention_edit':user.detention_edit,
                # 'detention_delete':user.detention_delete,
                # 'medic_show':user.medic_show',
                # 'medic_create':user.medic_create,
                # 'medic_edit':user.medic_edit,
                # 'medic_delete':user.medic_delete,
                # 'cell_show':user.cell_show,
                # 'cell_create':user.cell_create,
                # 'cell_edit':user.cell_edit,
                # 'cell_delete':user.cell_delete,
                # 'actions_show':user.actions_show,
                # 'actions_create':user.actions_create,
                # 'actions_edit':user.actions_edit,
                # 'actions_delete':user.actions_delete,
                # 'records_module':user.records_module,
                # 'car_show':user.car_show,
                # 'car_create':user.car_create,
                # 'car_edit':user.car_edit,
                # 'car_delete':user.car_delete,
                # 'object_show':user.object_show,
                # 'object_create':user.object_create,
                # 'object_edit':user.object_edit,
                # 'object_delete':user.object_delete,
                # 'reports_module':user.reports_module,
                # 'report_detainee_show':user.report_detainee_show,
                # 'report_detainee_create':user.report_detainee_create,
                # 'report_detainee_edit':user.report_detainee_edit,
                # 'report_detainee_delete':user.report_detainee_delete,
                # 'report_car_show':user.report_car_show,
                # 'report_car_create':user.report_car_edit,
                # 'report_car_edit':user.report_car_edit,
                # 'report_car_delete':user.report_car_delete,
                # 'report_agent_show':user.report_car_show,
                # 'report_agent_create':user.report_agent_create,
                # 'report_agent_edit':user.report_agent_edit,
                # 'report_agent_delete':user.report_agent_delete,
                # 'report_cell_show':user.report_cell_show,
                # 'report_cell_create':user.report_cell_create,
                # 'report_cell_edit':user.report_cell_edit,
                # 'report_cell_delete':user.report_cell_delete,
                # 'users_module':user.users_module,
                # 'user_show':user.user_show,
                # 'user_create':user.user_create,
                # 'user_edit':user.user_edit,
                # 'user_delete':user.user_delete
            }
            district_id = user.district_default_id
            district = filtered_districts.filter(id=district_id).first()            
            if district:
                print(f'District id: {district.id}, name: {district.name}')
                new_object['district_default']= {
                    "id":district.id,
                    "name":district.name

                }
            formatted_results.append(new_object)


        serializer = RetrieveUserSerializer(users, many=True)
        return Response({'status': 'success', 'data': formatted_results})

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'medical_cedula': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'fathers_name': openapi.Schema(type=openapi.TYPE_STRING),
                'mothers_name': openapi.Schema(type=openapi.TYPE_STRING),
                'discriminator': openapi.Schema(type=openapi.TYPE_STRING),
                'employee_number': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),                
                'district_default': openapi.Schema(type=openapi.TYPE_INTEGER),
                'districts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
                'detainee_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),                
                'detention_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detention_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detention_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'records_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'reports_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'users_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False)

                # Add other properties as needed
            },
            required=['username','district_default','districts' ],
        ),
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=RetrieveUserSerializer,
            ),
            400: "Bad Request",
        },
        operation_summary="Create a new user with districts",
        operation_description="This endpoint creates a new user along with the specified districts.",
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        user_data = request.data.copy()
        user_serializer = self.get_serializer(data=user_data)

        if user_serializer.is_valid():            
            user_instance = user_serializer.save()          
            district_ids = request.data.get('districts', [])            
            
            for district_id in district_ids:
                district_instance = get_object_or_404(District, pk=district_id)
                users_districts_data = {
                    'user': user_instance,
                    'district': district_instance
                }
                new_user_district = UserDistricts.objects.create(**users_districts_data)                
            

            headers = self.get_success_headers(user_serializer.data)
            response_data=user_serializer.data
            district_instance = user_instance.district_default
            # Access district information
            district_information = {
                'id': district_instance.id,
                'name': district_instance.name,                
            }
            user_districts_instances = UserDistricts.objects.filter(user=user_instance)            
            user_districts_info = []

            # Iterate through the instances and extract the required information
            for user_district_instance in user_districts_instances:
                district_info = {
                    'id': user_district_instance.district.id,
                    'name': user_district_instance.district.name,                    
                }
                user_districts_info.append(district_info)


            response_data['district_default']=district_information
            response_data['districts']=user_districts_info
            
            return Response({'status': 'success', 'data': response_data}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'status': 'fail', 'errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
class SeederUserView(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = AddUserSerializer
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset
        self.check_object_permissions(self.request, obj)
        return obj
    # Your other viewset methods...
    @swagger_auto_schema(auto_schema=None)  # This will exclude the method from Swagger
    @action(detail=False, methods=['post'])
    def seed_data(self, request):
        # Example user data
        users_data = [
            # {
            #     "password": "thisisapassword",
            #     "last_login": "2023-11-28 18:53:19.787 -0600",
            #     "is_active": True,
            #     "username": "JVALENZUELA",
            #     "name":"JESUS",
            #     "fathers_name": "VALENZUELA",
            #     "mothers_name":"DOMINGUEZ",
            #     "email":"jvalenzuela@siprob.com",
            #     "medical_cedula":"128733782",            
            #     "employee_number": 1,
            #     "discriminator": "medic"                
            # },    
            {
                "password": "thisisapassword",
                "last_login": "2023-11-28 18:53:19.787 -0600",
                "is_active": True,
                "username": "robo",
                "fathers_name": "cop",
                "mothers_name": "jojo",
                "email":"robo@siprob.com",                                
                "employee_number": "A1",
                "default_district":1,
                "discriminator": "police"                        
            },
            {
                "password": "securepassword",
                "last_login": "2023-11-29 09:15:45.123 -0600",
                "is_active": True,
                "username": "guardian",
                "fathers_name": "shield",
                "mothers_name": "armor",
                "email":"guardian@siprob.com",                
                "default_district":1,
                "employee_number": "B2",
                "discriminator": "security"                            
            },
            {
                "password": "strongpass",
                "last_login": "2023-11-30 12:40:22.567 -0600",
                "is_active": True,
                "username": "dispatcher",
                "fathers_name": "communication",
                "mothers_name": "control",
                "email":"dispatcher@siprob.com",                
                "default_district":1,
                "employee_number": "C3",
                "discriminator": "communication"                
            },
            {
                "password": "safepass123",
                "last_login": "2023-12-01 15:55:10.890 -0600",
                "is_active": True,
                "username": "investigator",
                "fathers_name": "sleuth",
                "mothers_name": "inspector",
                "email":"investigator@siprob.com",                
                "default_district":1,
                "employee_number": "D4",
                "discriminator": "investigation"                            
            },            
            {       
                "password": "userpass789",
                "last_login": "2023-12-02 09:30:00.000 -0600",
                "is_active": True,
                "username": "observer",
                "fathers_name": "watcher",
                "mothers_name": "lookout",
                "email":"observer@siprob.com",
                "default_district":1,
                "employee_number": "C5",
                "discriminator": "observation"            
            },
            {
                "password": "access1234",
                "last_login": "2023-12-03 14:20:00.000 -0600",
                "is_active": True,
                "username": "accessor",
                "fathers_name": "entry",
                "mothers_name": "pass",
                "email":"accesor@siprob.com",
                "default_district":1,                
                "employee_number": "C6",
                "discriminator": "access"           
            }
        ]

        # Hash passwords
        for user_data in users_data:
            # hasher = XorPasswordHasher()
            user_data["password"] = make_password(user_data["password"])            
            #user_data["password"] = make_password(user_data["password"], hasher='xor')            
            #user_data["password"] = XorPasswordHasher(user_data["password"], hasher='xor')            

        # Save users to the database or create a fixture file
        User.objects.bulk_create([User(**user_data) for user_data in users_data])

        return Response({"message": "User data seeded successfully."})
    
class SingleUserView(viewsets.ModelViewSet):
    serializer_class = RetrieveUserSerializer
    queryset = User.objects.filter(is_active=True)  

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk'], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(        
        responses={200: RetrieveUserSerializer(many=False)},
        operation_summary="Retrieves the user with the primary key provided in url",
        operation_description="This endpoint retrieves the information of the user .",
        tags=["Users"],
    )
    def retrieve(self, request, *args, **kwargs):
        user_instance = self.get_object()
        if user_instance:
            user_serializer = self.get_serializer(user_instance)
            response_data = user_serializer.data
            district_instance = user_instance.district_default
            if district_instance:
                response_data['district_default'] = {
                    'id': district_instance.id,
                    'name': district_instance.name,
                }
            user_districts_instances = UserDistricts.objects.filter(user=user_instance)
            user_districts_info = []
            for user_district_instance in user_districts_instances:
                user_districts_info.append({
                    'id': user_district_instance.district.id,
                    'name': user_district_instance.district.name,
                })
            response_data['districts'] = user_districts_info
            return Response({'status':'success','data':response_data})
        return Response({'status':'fail','message':'User not found'},status=status.HTTP_404_NOT_FOUND)
        

    @swagger_auto_schema(                
        responses={
            200: openapi.Response(
                description="User deleted successfully",
                examples={
                    "application/json": {
                    "status": "success",
                    "message": "User deleted",
                    }
                },
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                    "status": "fail",
                    "message": "User not found",
                    }
                },
            ),
        },
        operation_summary="Deletes the user with the primary key provided in url",
        operation_description="This endpoint does a soft delete of the user on database.",
        tags=["Users"],
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.is_active=False
            instance.save()
            return Response(
                {
                    'status':'success',
                    'message':'User_deleted'

                },
                status=status.HTTP_200_OK
                )
        return Response({'status':'fail','message':'User not found'},status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema( 
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
             properties={
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'medical_cedula': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'fathers_name': openapi.Schema(type=openapi.TYPE_STRING),
                'mothers_name': openapi.Schema(type=openapi.TYPE_STRING),
                'discriminator': openapi.Schema(type=openapi.TYPE_STRING),
                'employee_number': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),                
                'district_default': openapi.Schema(type=openapi.TYPE_INTEGER),
                'districts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
                'detainee_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detainee_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),                
                'detention_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detention_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'detention_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'medic_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'cell_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'actions_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'records_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'car_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'object_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'reports_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_detainee_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_car_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_agent_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'report_cell_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'users_module': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_show': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_create': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_edit': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                'user_delete': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False)

                # Add other properties as needed
            },
            required=['username','district_default','districts' ],

        ),               
        responses={201: RetrieveUserSerializer(many=False)},
        operation_summary="Updates the user with the primary key provided in url",
        operation_description="This endpoint updates the information on the user with the id provided in URL.",
        tags=["Users"]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance:
            # Clear existing many-to-many relations
            #instance.districts.clear()

            received_data = {
                
                'username': request.data.get('username', instance.username),
                'password': make_password(request.data.get('password')),
                'discriminator': request.data.get('discriminator', instance.discriminator),
                'medical_cedula': request.data.get('discriminator', instance.discriminator),
                'name': request.data.get('name', instance.name),
                'fathers_name': request.data.get('fathers_name', instance.fathers_name),
                'mothers_name': request.data.get('mothers_name', instance.mothers_name),
                'email': request.data.get('email', instance.email),
                'employee_number': request.data.get('empployee_number', instance.employee_number),
                'district_default': request.data.get('district_default', instance.employee_number),
                'detainee_module':request.data.get('detainee_module',instance.detainee_module),
                'detainee_show':request.data.get('detainee_show',instance.detainee_show),
                'detainee_create':request.data.get('detainee_create',instance.detainee_create),
                'detainee_edit':request.data.get('detainee_edit',instance.detainee_edit),
                'detainee_delete':request.data.get('detainee_delete',instance.detainee_delete),                
                'detention_create':request.data.get('detention_create',instance.detention_create),
                'detention_edit':request.data.get('detention_edit',instance.detention_edit),
                'detention_delete':request.data.get('detention_delete',instance.detention_delete),
                'medic_show':request.data.get('medic_show',instance.medic_show),
                'medic_create':request.data.get('medic_create',instance.medic_create),
                'medic_edit':request.data.get('medic_edit',instance.medic_edit),
                'medic_delete':request.data.get('medic_delete',instance.medic_delete),
                'cell_show':request.data.get('cell_show',instance.cell_show),
                'cell_create':request.data.get('cell_create',instance.cell_create),
                'cell_edit':request.data.get('cell_edit',instance.cell_show),
                'cell_delete':request.data.get('cell_delete',instance.cell_delete),
                'actions_show':request.data.get('actions_show',instance.actions_show),
                'actions_create':request.data.get('actions_create',instance.actions_create),
                'actions_edit':request.data.get('actions_edit',instance.actions_edit),
                'actions_delete':request.data.get('actions_delete',instance.actions_delete),                
                'records_module':request.data.get('records_module',instance.records_module),
                'car_show':request.data.get('car_show',instance.car_show),
                'car_create':request.data.get('car_create',instance.car_create),
                'car_edit':request.data.get('car_edit',instance.car_edit),
                'car_delete':request.data.get('car_delete',instance.car_delete),
                'object_show':request.data.get('object_show',instance.object_show),
                'object_create':request.data.get('object_create',instance.object_create),
                'object_edit':request.data.get('object_edit',instance.object_edit),
                'object_delete':request.data.get('object_delete',instance.object_delete),                
                'reports_module':request.data.get('reports_module',instance.reports_module),
                'report_detainee_show':request.data.get('report_detainee_show',instance.report_detainee_show),
                'report_detainee_create':request.data.get('report_detainee_create',instance.report_detainee_create),
                'report_detainee_edit':request.data.get('report_detainee_edit',instance.report_detainee_edit),
                'report_detainee_delete':request.data.get('report_detainee_delete',instance.report_detainee_delete),
                'report_car_show':request.data.get('report_car_show',instance.report_car_show),
                'report_car_create':request.data.get('report_car_edit',instance.report_car_delete),
                'report_car_edit':request.data.get('report_car_edit',instance.report_car_edit),
                'report_car_delete':request.data.get('report_car_delete',instance.report_car_delete),
                'report_agent_show':request.data.get('report_car_show',instance.report_car_show),
                'report_agent_create':request.data.get('report_agent_create',instance.report_agent_create),
                'report_agent_edit':request.data.get('report_agent_edit',instance.report_agent_edit),
                'report_agent_delete':request.data.get('report_agent_delete',instance.report_agent_delete),
                'report_cell_show':request.data.get('report_cell_show',instance.report_cell_show),
                'report_cell_create':request.data.get('report_cell_create',instance.report_cell_create),
                'report_cell_edit':request.data.get('report_cell_edit',instance.report_cell_edit),
                'report_cell_delete':request.data.get('report_cell_delete',instance.report_cell_delete),                
                'users_module':request.data.get('users_module',instance.users_module),
                'user_show':request.data.get('user_show',instance.user_show),
                'user_create':request.data.get('user_create',instance.user_create),
                'user_edit':request.data.get('user_edit',instance.user_edit),
                'user_delete':request.data.get('user_delete',instance.user_delete)
            }            

            # Add new many-to-many relations from the 'districts' field in the request            
            user_districts = UserDistricts.objects.filter(user=instance)
            if user_districts.exists():
                user_districts.delete()
            district_ids = request.data.get('districts', [])
            for district_id in district_ids:
                district_instance = get_object_or_404(District, pk=district_id)
                users_districts_data = {
                    'user': instance,
                    'district': district_instance
                }
                new_user_district = UserDistricts.objects.create(**users_districts_data)                                   

            #instance.districts.add(*district_ids)

            serializer = self.get_serializer(instance, data=received_data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response_data=serializer.data
            district_instance = instance.district_default
            # Access district information
            district_information = {
                'id': district_instance.id,
                'name': district_instance.name,                
            }
            user_districts_instances = UserDistricts.objects.filter(user=instance)            
            user_districts_info = []

            # Iterate through the instances and extract the required information
            for user_district_instance in user_districts_instances:
                district_info = {
                    'id': user_district_instance.district.id,
                    'name': user_district_instance.district.name,                    
                }
                user_districts_info.append(district_info)


            response_data['district_default']=district_information
            response_data['districts']=user_districts_info
            return Response({'status':'success','data':response_data})

        return Response({'status':'fail','message':'User not found'},status=status.HTTP_404_NOT_FOUND)
    


class ShowUserView(viewsets.ModelViewSet):
    serializer_class = RetrieveUserSerializer
    authentication = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]               

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'password': openapi.Schema(type=openapi.TYPE_STRING),                         
                },
            required=['password']
            ),  
            
        
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'status': openapi.Schema(type=openapi.TYPE_STRING),                         
                'message': openapi.Schema(type=openapi.TYPE_STRING),                         
                },
            ),
            },
        operation_summary="User password change",
        operation_description="Allows to change the password of logged user.",
        tags=["Users"],
    )
    
    def change_password(self, request, *args, **kwargs):
        # Get the authenticated user
        user = self.request.user
        # Get the new password from the request
        new_password = request.data.get('password')
        # Update the user's password
        user.set_password(new_password)
        user.save()
        # You may want to provide a success message in the response
        response_data = {
            'status': 'success',
            'message': 'Password changed successfully.',
        }
        return Response(response_data, status=status.HTTP_200_OK)                

class CreateTokenView(viewsets.ModelViewSet):    
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'username': openapi.Schema(type=openapi.TYPE_STRING),         
                'password': openapi.Schema(type=openapi.TYPE_STRING),               
                },
        ),  
        
        responses={
            201: RetrieveUserSerializer(many=False)},
        operation_summary="User Log In",
        operation_description="Logs the user and retrieves user information along with the token.",
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        #return super().post(request, *args, **kwargs)
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if username is None or password is None:
            return Response({'status': 'fail', 'message': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.filter(username=username).first()

        if user:  
            if check_password(password, user.password):    # Password is correct, generate a new token
                payload={
                    'user_id':user.id,
                    'exp':datetime.utcnow() + timedelta(days=1)
                }
                #  os.getenv("JWT_SECRET_KEY")
                token, created = Token.objects.get_or_create(user=user)
                #encoded_jwt = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm='HS256')

                # Retrieve user information using your serializer
                user_serializer = RetrieveUserSerializer(user)
                user_districts_info = UserDistricts.objects.filter(user=user.id)           

                # Create an array to store the information
                districts_info = []
                # Iterate through the instances and extract the required information
                for user_district_instance in user_districts_info:
                    district_info = {
                        'id': user_district_instance.district.id,
                        'name': user_district_instance.district.name,
                        # Add other fields as needed
                    }
                    districts_info.append(district_info)          

                response_data = user_serializer.data
                response_data['districts'] = districts_info
                response_data['token'] = token.key
                default_district_id = user_serializer.data.get('district_default')
                if default_district_id:
                    default_district_info = District.objects.filter(id=default_district_id).first()
                    if default_district_info:
                        response_data['district_default'] = {
                            'id': default_district_info.id,
                            'name': default_district_info.name
                        }

                # Agrupar permisos para el frontend
                response_data['permissions'] = {
                    'detainee_module': user.detainee_module,
                    'detainee_show': user.detainee_show,
                    'detainee_create': user.detainee_create,
                    'detainee_edit': user.detainee_edit,
                    'detainee_delete': user.detainee_delete,
                    'detention_create': user.detention_create,
                    'detention_edit': user.detention_edit,
                    'detention_delete': user.detention_delete,
                    'medic_show': user.medic_show,
                    'medic_create': user.medic_create,
                    'medic_edit': user.medic_edit,
                    'medic_delete': user.medic_delete,
                    'cell_show': user.cell_show,
                    'cell_create': user.cell_create,
                    'cell_edit': user.cell_edit,
                    'cell_delete': user.cell_delete,
                    'actions_show': user.actions_show,
                    'actions_create': user.actions_create,
                    'actions_edit': user.actions_edit,
                    'actions_delete': user.actions_delete,
                    'records_module': user.records_module,
                    'car_show': user.car_show,
                    'car_create': user.car_create,
                    'car_edit': user.car_edit,
                    'car_delete': user.car_delete,
                    'object_show': user.object_show,
                    'object_create': user.object_create,
                    'object_edit': user.object_edit,
                    'object_delete': user.object_delete,
                    'reports_module': user.reports_module,
                    'report_detainee_show': user.report_detainee_show,
                    'report_detainee_create': user.report_detainee_create,
                    'report_car_show': user.report_car_show,
                    'report_car_create': user.report_car_create,
                    'report_agent_show': user.report_agent_show,
                    'report_agent_create': user.report_agent_create,
                    'report_cell_show': user.report_cell_show,
                    'report_cell_create': user.report_cell_create,
                    'users_module': user.users_module,
                    'user_show': user.user_show,
                    'user_create': user.user_create,
                    'user_edit': user.user_edit,
                    'user_delete': user.user_delete,
                }
                return Response({'status': 'success', 'data': response_data})

            elif user.temporary_password is not None:
                if check_password(password, user.temporary_password):
                    if user.password_expiration > timezone.now():
                        payload={
                            'user_id':user.id,
                            'exp':datetime.utcnow() + timedelta(days=1)
                        }
                        #  os.getenv("JWT_SECRET_KEY")
                        token, created = Token.objects.get_or_create(user=user)
                        #encoded_jwt = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm='HS256')
        
                        # Retrieve user information using your serializer
                        user_serializer = RetrieveUserSerializer(user)
                        user_districts_info = UserDistricts.objects.filter(user=user.id)           
        
                        # Create an array to store the information
                        districts_info = []
                        # Iterate through the instances and extract the required information
                        for user_district_instance in user_districts_info:
                            district_info = {
                                'id': user_district_instance.district.id,
                                'name': user_district_instance.district.name,
                                # Add other fields as needed
                            }
                            districts_info.append(district_info)          
        
                        response_data = user_serializer.data
                        response_data['districts'] = districts_info
                        response_data['token'] = token.key
                        default_district_id = user_serializer.data.get('district_default')
                        if default_district_id:
                            default_district_info = District.objects.filter(id=default_district_id).first()
                            if default_district_info:
                                response_data['district_default'] = {
                                    'id': default_district_info.id,
                                    'name': default_district_info.name
                                }

                        # Agrupar permisos para el frontend
                        response_data['permissions'] = {
                            'detainee_module': user.detainee_module,
                            'detainee_show': user.detainee_show,
                            'detainee_create': user.detainee_create,
                            'detainee_edit': user.detainee_edit,
                            'detainee_delete': user.detainee_delete,
                            'detention_create': user.detention_create,
                            'detention_edit': user.detention_edit,
                            'detention_delete': user.detention_delete,
                            'medic_show': user.medic_show,
                            'medic_create': user.medic_create,
                            'medic_edit': user.medic_edit,
                            'medic_delete': user.medic_delete,
                            'cell_show': user.cell_show,
                            'cell_create': user.cell_create,
                            'cell_edit': user.cell_edit,
                            'cell_delete': user.cell_delete,
                            'actions_show': user.actions_show,
                            'actions_create': user.actions_create,
                            'actions_edit': user.actions_edit,
                            'actions_delete': user.actions_delete,
                            'records_module': user.records_module,
                            'car_show': user.car_show,
                            'car_create': user.car_create,
                            'car_edit': user.car_edit,
                            'car_delete': user.car_delete,
                            'object_show': user.object_show,
                            'object_create': user.object_create,
                            'object_edit': user.object_edit,
                            'object_delete': user.object_delete,
                            'reports_module': user.reports_module,
                            'report_detainee_show': user.report_detainee_show,
                            'report_detainee_create': user.report_detainee_create,
                            'report_car_show': user.report_car_show,
                            'report_car_create': user.report_car_create,
                            'report_agent_show': user.report_agent_show,
                            'report_agent_create': user.report_agent_create,
                            'report_cell_show': user.report_cell_show,
                            'report_cell_create': user.report_cell_create,
                            'users_module': user.users_module,
                            'user_show': user.user_show,
                            'user_create': user.user_create,
                            'user_edit': user.user_edit,
                            'user_delete': user.user_delete,
                        }
                        return Response({'status': 'success', 'data': response_data})
                    else:
                        return Response({'status': 'fail', 'message': 'Temporary password expired.'}, status=status.HTTP_401_UNAUTHORIZED)

                else:
                    return Response({'status': 'fail', 'message': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'status': 'fail', 'message': 'Invalid username.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'status': 'fail', 'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        

class SearchUsersViewSet(viewsets.ModelViewSet):
    response = {
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        "results": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "user_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_employee_number": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_username": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_default_district_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "user_default_district": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_status": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                },
            ),
        ),
        "per_page": openapi.Schema(type=openapi.TYPE_INTEGER),
        "page": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_items": openapi.Schema(type=openapi.TYPE_INTEGER),
        }),
    }

    search_body = {
        "sorted_column": openapi.Schema(type=openapi.TYPE_STRING),
        "filter_by": openapi.Schema(type=openapi.TYPE_STRING),
        "order": openapi.Schema(type=openapi.TYPE_STRING),
        "search": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=search_body,
        ),
        manual_parameters=[
            openapi.Parameter(
                "page",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Pagination page",
            ),
            openapi.Parameter(
                "per_page",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Items per page",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Search done successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=response,
                ),
            ),
        },
        operation_summary="Search in users",
        operation_description="This endpoint searches in the users.",
        tags=["Users"],
    )
    def search(self, request, *args, **kwargs):
        sorted_column = request.data.get('sorted_column')
        order = request.data.get('order')
        filter_by = request.data.get('filter_by')

        search = request.data.get('search')
        
        items_per_page = request.GET.get('per_page', 10)
        page = request.GET.get('page', 1)

        if search != "":
            results = User.objects.prefetch_related()
            results = results.filter(Q(name__icontains=search) | Q(fathers_name__icontains=search) | Q(mothers_name__icontains=search) | Q(employee_number__icontains=search))
        else:
            results = User.objects.prefetch_related()
        if sorted_column != "" and sorted_column is not None:
            # Mapear nombres del frontend a campos del modelo
            column_mapping = {
                'id': 'id',
                'employee_number': 'employee_number',
                'name': 'name',
                'user_name': 'fathers_name',
                'fathers_name': 'fathers_name',
                'mothers_name': 'mothers_name',
                'status': 'is_active',
            }
            sorted_column = column_mapping.get(sorted_column)

            if sorted_column and sorted_column != "district":
                if order == 'desc':
                    results = results.order_by(f'-{sorted_column}')
                else:
                    results = results.order_by(sorted_column)
        if filter_by != "":
            if filter_by == "active":
                results = results.filter(is_active=True)
        users = [
        {
            "user_id": result.id,
            "user_employee_number": result.employee_number,
            "user_username": result.username,
            "user_name": result.fathers_name,
            "user_fathers_name": result.fathers_name,
            "user_mothers_name": result.mothers_name,
            "user_default_district_id": result.district_default_id,
            "user_status": result.is_active,
        }
        for result in results
        ]
        for user in users:
            try:
                default_disctrict = District.objects.get(id=user.get('user_default_district_id'))
                user['user_default_district'] = default_disctrict.name
            except District.DoesNotExist:
                print("district not found")

        # for user in users:
        #     user['district'] = ""
        #     user_districts = UserDistricts.objects.filter(user_id=user.get('user_id')).values_list('district_id', flat=True)
        #     print(user_districts)
        #     for user_district in user_districts:
        #         try:
        #             district = District.objects.get(id=user_district)
        #             user['district'] += district.name + ", "
        #         except District.DoesNotExist:
        #             print("district not found")
        #     user['district'] = user['district'][:-2]
        #     all_districts = District.objects.filter(is_active=True).values_list('id', flat=True)
        #     if len(all_districts) == len(user_districts):
        #         user['district'] = "Todos"
                
        if sorted_column == 'district':
            if order == 'desc' and sorted_column == "district":
                users.sort(key=lambda x: x.get('user_default_district'), reverse=False)
            else:
                if sorted_column == "district":
                    users.sort(key=lambda x: x.get('user_default_district'), reverse=True)
                
        paginator = Paginator(users, items_per_page)

        items = paginator.page(page)

        data_response = {
            "results": items.object_list,
            "per_page": paginator.per_page,
            "page": int(page),
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        }

        return JsonResponse({"status": "success", "data": data_response})

class PasswordRecoverViewSet(viewsets.ModelViewSet):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'email': openapi.Schema(type=openapi.TYPE_STRING),                         
                },
            required=['email']
            ),  
            
        
        responses={
            200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'status': openapi.Schema(type=openapi.TYPE_STRING),                         
                'message': openapi.Schema(type=openapi.TYPE_STRING),                         
                },
            ),
            },
        operation_summary="User password recovery",
        operation_description="Sends an email to the user registered with the email provided in order to recover the password.",
        tags=["Users"],
    )   
        
    def send_email(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Check if the user with the provided email exists
        user = User.objects.filter(email=email, is_active=True).first()

        if user:
            # Generate a random password
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            # Hash the password
            hashed_password = make_password(random_password)

            # Save the hashed password and mark it as not used
            user.temporary_password = hashed_password
            user.password_expiration = timezone.now() + timedelta(hours=4)
            user.save()

            # Send the password to the user's email using Gmail SMTP
            subject = 'SIPROB - Restablecer contraseña'
            message = (
                f'Hemos recibido una solicitud para restablecer la contraseña de tu cuenta. '
                f'Se ha generado un acceso temporal disponible por las siguientes 4 horas. '
                f'Al ingresar, favor de actualizar tu acceso en la sección de perfil de usuario dando clic sobre tu nombre en el menú lateral.\n\n'
                f'Contraseña temporal: {random_password}\n'
            )
            from_email = 'SIPROB Sistema'  # Replace with your Gmail address
            recipient_list = [email]

            send_mail(
                subject, 
                message, 
                from_email, 
                recipient_list, 
                fail_silently=False,
                auth_user=os.getenv("EMAIL_ACCOUNT"),  # Your Gmail username
                auth_password=os.getenv("EMAIL_PASSWORD"),  # Your Gmail password
                #auth_user=str(os.getenv("EMAIL_SENDER")),  # Your Gmail username
                # auth_password=str(os.getenv("EMAIL_PASSWORD")),  # Your Gmail password
            )

            return Response({'status': 'success', 'message': 'Password sent successfully'})
        else:
            return Response({'status': 'fail', 'message': 'User with this email does not exist'})



# class CreateUserView(generics.CreateAPIView):
#     serializer_class = UserSerializer

#     @swagger_auto_schema(
#         request_body=UserSerializer,
#         responses={201: UserSerializer(many=False)},
#         operation_summary="Create a new user",
#         operation_description="This endpoint creates a new user.",
#         tags=["Users"],
#     )
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

# Create your views here.
