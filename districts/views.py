from django.shortcuts import render
from rest_framework import generics
from rest_framework import generics, authentication, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from districts.serializers import *
from districts.models import District
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class DistrictViewSet(viewsets.ModelViewSet):
    serializer_class = DistrictsSerializer
    queryset = District.objects.all()

    @swagger_auto_schema(
        responses={201: DistrictsSerializer(many=False)},
        operation_summary="Lists all districts",
        operation_description="List all the active districts stored on database.",
        tags=["Districts"],
    )    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk'], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(        
        responses={200: DistrictsSerializer(many=False)},
        operation_summary="Retrieves the district with the primary key provided in url",
        operation_description="This endpoint retrieves the information of the district .",
        tags=["Districts"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:     
            serializer = self.get_serializer(instance)   
            return Response(serializer.data)
        return Response({'status':'fail','message':'District not found'},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(        
        responses={200: DistrictsSerializer(many=False)},
        operation_summary="Lists all districts",
        operation_description="This endpoint lists all the districts .",
        tags=["Districts"],
    )
    def list(self, request, *args, **kwargs):
        districts = District.objects.filter()
        formated_districts = [
            {
                'id': district.id,
                'name': district.name,
                'created_at': district.created_at,
                'updated_at': district.updated_at,
            }
            for district in districts
        ]
        return Response({'status': "success", 'data': formated_districts})
        

    @swagger_auto_schema(                
        responses={201: DistrictsSerializer(many=False)},
        operation_summary="Delete district with the primary key provided in url",
        operation_description="This endpoint does a soft delete of the District on database.",
        tags=["Districts"],
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.is_active=False
            instance.save()
            return Response(
                {
                    'status':'success',
                    'message':'District_deleted'

                },
                status=status.HTTP_204_NO_CONTENT
                )
        return Response({'status':'fail','message':'district not found'},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(                
        responses={201: DistrictsSerializer(many=False)},
        operation_summary="Updates the district with the primary key provided in url",
        operation_description="This endpoint updates the information on the district with the id provided in URL.",
        tags=["Districts"]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)            
        return Response({'status':'fail','message':'District not found'},status=status.HTTP_404_NOT_FOUND)    
    