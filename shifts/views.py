from django.shortcuts import render
from django.shortcuts import render
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from shifts.models import Shift
from shifts.serializers import ShiftSerializer
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class ShiftsViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.filter(is_active=True)
    serializer_class = ShiftSerializer
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset
        self.check_object_permissions(self.request, obj)
        return obj
    
    @swagger_auto_schema(
        operation_summary="Lists all Shifts",
        operation_description="This endpoint lists all the shifts on the database.",
        tags=["Shifts"],
    )
    def get(self, request, *args, **kwargs):
        detainees = Shift.objects.filter(is_active=True)
        serializer = ShiftSerializer(detainees, many=True)
        return Response({'status': 'success', 'data': serializer.data})
        #return Role.objects.filter(is_active=True)   
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'startHour': openapi.Schema(type=openapi.TYPE_STRING,default="12:00"),
                'endHour': openapi.Schema(type=openapi.TYPE_STRING,default="20:00"),               
            },
        ),        
        responses={201: ShiftSerializer(many=False)},
        operation_summary="Creates a new shift",
        operation_description="This endpoint creates a new shift on database.",
        tags=["Shifts"],
    )
    def post(self, request, *args, **kwargs):        
        shift = Shift()
        shift.start_hour = request.data.get('startHour')
        shift.end_hour = request.data.get('endHour')        
        shift.save()                
        return Response(request.data, status=status.HTTP_201_CREATED)

class SingleShiftViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer 
    queryset = Shift.objects.filter(is_active=True)
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk'], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(        
        responses={200: ShiftSerializer(many=False)},
        operation_summary="Retrieves the shift with the primary key provided in url",
        operation_description="This endpoint retrieves the information of the shift .",
        tags=["Shifts"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:     
            serializer = self.get_serializer(instance)   
            return Response({'status':'success','data':serializer.data})
        return Response({'status':'fail','message':'Shift not found'},status=status.HTTP_404_NOT_FOUND)
        

    @swagger_auto_schema(                
        responses={201: ShiftSerializer(many=False)},
        operation_summary="Deletes the shift with the primary key provided in url",
        operation_description="This endpoint does a soft delete of the shift on database.",
        tags=["Shifts"],
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.is_active=False
            instance.save()
            return Response(
                {
                    'status':'success',
                    'message':'Shift_deleted'

                },
                status=status.HTTP_204_NO_CONTENT
                )
        return Response({'status':'fail','message':'Shift not found'},status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(                
        responses={201: ShiftSerializer(many=False)},
        operation_summary="Updates the shift with the primary key provided in url",
        operation_description="This endpoint updates the information on the shift with the id provided in URL.",
        tags=["Shifts"]
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({'status':'success','data':serializer.data})
        return Response({'status':'fail','message':'Shift not found'},status=status.HTTP_404_NOT_FOUND)    
