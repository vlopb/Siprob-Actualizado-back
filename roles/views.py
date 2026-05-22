from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework import status, viewsets
from rest_framework.response import Response
from roles.serializers import RoleSerializer
from roles.models import Role
from drf_yasg.utils import swagger_auto_schema

class RolesViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset
        self.check_object_permissions(self.request, obj)
        return obj
    
    @swagger_auto_schema(
        responses={201: RoleSerializer(many=True)},
        operation_summary="Lists all roles",
        operation_description="This endpoint lists all the active roles on the database.",
        tags=["Roles"],
    )
    def get(self, request, *args, **kwargs):
        roles = Role.objects.filter(is_active=True)
        serializer = RoleSerializer(roles, many=True)
        return Response({'status': 'success', 'data': serializer.data})

        #return Role.objects.filter(is_active=True)
    
    @swagger_auto_schema(
        request_body=RoleSerializer,
        responses={201: RoleSerializer(many=False)},
        operation_summary="Creates a new role",
        operation_description="This endpoint creates a new role.",
        tags=["Roles"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                #Detainee fields
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'color': openapi.Schema(type=openapi.TYPE_STRING),                
            },
            required=['name', 'colors']
        ),
        responses={201: RoleSerializer(many=False)},
        operation_summary="Creates a new role",
        operation_description="This endpoint creates a new role.",
        tags=["Roles"],
    )
    def post(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)
        


class SingleRoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer 
    queryset = Role.objects.filter(is_active=True)
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk'], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(        
        responses={200: RoleSerializer(many=False)},
        operation_summary="Retrieves the role with the primary key provided in url",
        operation_description="This endpoint retrieves the information of the role .",
        tags=["Roles"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:     
            serializer = self.get_serializer(instance)   
            return Response({'status':'success','data':serializer.data})
        return Response({'status':'fail','message':'Role not found'},status=status.HTTP_404_NOT_FOUND)
        

    @swagger_auto_schema(                
        responses={201: RoleSerializer(many=False)},
        operation_summary="Delete role with the primary key provided in url",
        operation_description="This endpoint does a soft delete of the role on database.",
        tags=["Roles"],
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.is_active=False
            instance.save()
            return Response(
                {
                    'status':'success',
                    'message':'Role_deleted'

                },
                status=status.HTTP_204_NO_CONTENT
                )
        return Response({'status':'fail','message':'Role not found'},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(                
        responses={201: RoleSerializer(many=False)},
        operation_summary="Updates the role with the primary key provided in url",
        operation_description="This endpoint updates the information on the role with the id provided in URL.",
        tags=["Roles"]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({'status':'success','data':serializer.data})
        return Response({'status':'fail','message':'Role not found'},status=status.HTTP_404_NOT_FOUND)    



