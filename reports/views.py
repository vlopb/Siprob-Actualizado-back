from django.shortcuts import render
from dateutil import parser
import re
import pytz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import *
import datetime
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from records.forms import RecordsAdvancedSearchForm
from django.http import JsonResponse, HttpResponse
from django.db import transaction
import json
import os
from drf_yasg import openapi
from records.serializers import *
from rest_framework import status, viewsets
from records.models import Records, MedicalInformation, Actions, Offended, Events, Cells, Belongings, OtherRecords
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import requests
from detainees.models import Detainee
from districts.models import District
from records.serializers import MedicalInformationSerializer, BelongingsSerializer, OtherRecordsSerializer
from detainees.serializers import DetaineesSerializer
from districts.serializers import DistrictsSerializer
from datetime import datetime, timedelta
from users.models import User
from users.serializers import RetrieveUserSerializer
from rest_framework.permissions import IsAuthenticated
from users.utils import decode_token
import locale
from django.forms.models import model_to_dict
import pandas as pd
from django.http import StreamingHttpResponse
from urllib.parse import quote
from io import BytesIO  # Import BytesIO for buffer

def format_datetime(dt, timezone_str='America/Denver', format_str="%d de %B de %Y %H:%M"):
    local_timezone = pytz.timezone(timezone_str)
    localized_datetime = dt.astimezone(local_timezone)
    return localized_datetime.strftime(format_str)

class OtherRecordsViewSet(viewsets.ModelViewSet):
    serializer_class = OtherRecordsSerializer
    queryset = OtherRecords.objects.filter(is_active=True)
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'initial_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'final_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'district': openapi.Schema(type=openapi.TYPE_STRING),             
                # Add other properties as needed
            },            
        ),
        responses={
            201: openapi.Response(
                "XLS document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
            400: "Bad Request",
        },
        operation_summary="Retrieves a report in MS Excel file for other records according to the filters provided",
        operation_description="This downloads a MS Excel file report, for other records with optional filtering the range of registration date and district",
        tags=["Reports"],
    )
    def download_other_records(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        received_district = request.data.get("district")               
        if received_district:                
            queryset = queryset.filter(district=received_district)
        
        if request.data.get("initial_date"):            
            initial_date_str = request.data["initial_date"]
            initial_date = parser.isoparse(initial_date_str)
            initial_date_utc = initial_date.astimezone(timezone.utc)        
        else:
            initial_date_utc = None        
        
        if request.data.get("final_date"):
            final_date_str = request.data["final_date"]
            final_date = parser.isoparse(final_date_str)
            final_date_utc = final_date.astimezone(timezone.utc)            
        else:
            final_date_utc = None

        if initial_date_utc and final_date_utc:  
            queryset=queryset.filter(date__gte=initial_date_utc, date__lte=final_date_utc)           
        
        if initial_date_utc and final_date_utc is None:            
            queryset=queryset.filter(date__gte=initial_date_utc) 
        
        if initial_date_utc is None and final_date_utc:            
            queryset=queryset.filter(date__gte=final_date_utc) 

        serializer = self.get_serializer(queryset, many=True)
        other_records_ids = [item['id'] for item in serializer.data]        
        #print("DATA: ", serializer.data)        
        detainees_queryset = OtherRecordsDetainees.objects.filter(other_record__in=other_records_ids).order_by('-detention_entry_date')
        detainees_serializer = OtherRecordsDetaineesSerializer(detainees_queryset, many=True)
        
        combined_data = []

        # Iterate over serializer.data and combine with detainees_serializer.data
        for record in serializer.data:
            record_id = record['id']

            # Filter detainees_serializer.data based on the current record_id
            related_detainees = [
                item for item in detainees_serializer.data if item['other_record'] == record_id
            ]

            date_string = record['date']
            date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = date_object.strftime('%m-%d-%Y %H:%M')                              

            combined_item = {
                "Distrito": record['district'],
                "Folio de otro registro":record['other_record_folio'],
                "Motivo": record['reason'],
                "Fecha y hora":formatted_date,
                "Lugar" : record['place'],
                "Nombre de quien asegura":record['holder_name'],
                "Tipo de vehiculo":record['vehicle_type'],
                "Linea" : record['line'],
                "Marca":record['brand'],                                
                "Diferenciador" :record['discriminator'],                
                "Tipo" :record['type'],
                "Subtipo" :record['subtype'],
                "Tipo de detención" :record['detention_type'],
                "Descripción" :record['description'],
                "Cantidad" : record['quantity'],
                "Condición general" : record['general_condition'],        
                "Modelo":record['model'],
                "Color":record['color'],
                "Placas" : record['plates'],        
                "Número de serie":record['serial_number'],
                "Número de engomado" : record['stamp_number'],                                         
                "Número de emisión" : record['emission_number'],                                         
                "Asociación que expide":record['association_expeditor'],                                            
                "Notas":record['comments'],                
                "Registrado por":record['created_by'],
                'Detenidos relacionados': len(related_detainees),
                'Último detenido': related_detainees[0]['name'] + ' ' + related_detainees[0]['fathers_name'] + ' ' + related_detainees[0]['mothers_name'] if related_detainees else ""

            }

            # Add the combined object to the result array
            combined_data.append(combined_item)
        if len(combined_data)==0:
            df = pd.DataFrame(columns=[
                "Distrito", "Folio de otro registro", "Motivo", "Fecha y hora", "Lugar",
                "Nombre de quien asegura", "Tipo de vehiculo", "Linea", "Marca",
                "Diferenciador", "Tipo", "Subtipo", "Tipo de detención", "Descripción", "Cantidad",
                "Condición general", "Modelo", "Color", "Placas", "Número de serie",
                "Número de engomado", "Número de emisión", "Asociación que expide",
                "Notas", "Registrado por", "Detenidos relacionados", "Último detenido"
            ])

        else:
            df = pd.DataFrame(combined_data)

        buffer = BytesIO()

        # Customize column names, styles, and widths as needed
        # column_mapping = {
        #     "district": "District",
        #     "other_record_folio": "Other Record Folio",
        #     # Add other mappings as needed
        # }

        #df = df.rename(columns=column_mapping)

        # Customize column styles and widths using ExcelWriter
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='OtrosRegistros')

            # Access the XlsxWriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['OtrosRegistros']

            # Customize styles and widths as needed
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center'})

            for col_num, value in enumerate(df.columns.values):                
                worksheet.write(0, col_num, value, header_format)
                # Customize column widths
                if (value=='Distrito'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Folio de otro registro'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Motivo'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Fecha y hora'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Lugar'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                if (value=='Nombre de quien asegura'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                if (value=='Tipo de vehiculo'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Linea'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Marca'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Diferenciador'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Tipo'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Subtipo'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Tipo de detención'):
                    worksheet.set_column(col_num, col_num, len(value) + 8)
                if (value=='Descripción'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Cantidad'):
                    worksheet.set_column(col_num, col_num, len(value) + 5)
                if (value=='Condición general'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Modelo'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Color'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Placas'):
                    worksheet.set_column(col_num, col_num, len(value) + 5)
                if (value=='Número de serie'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Número de engomado'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Número de emisión'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Asociación que expide'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Notas'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                if (value=='Registrado por'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                if (value=='Detenidos relacionados'):
                    worksheet.set_column(col_num, col_num, len(value) + 2)
                if (value=='Último detenido'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)

        # Set the buffer's cursor position to the beginning
        buffer.seek(0)

        # Create a file name for the Excel file
        filename = 'otros_registros.xlsx'

        # Create a StreamingHttpResponse to stream the file to the client
        response = StreamingHttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'

        #return Response({"status": "success", "data": combined_data}, status=status.HTTP_200_OK)
        return response


class DetaineesViewSet(viewsets.ModelViewSet):
    serializer_class = ReportsRecordsSerializer
    queryset = Records.objects.filter(is_active=True)    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'initial_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'final_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'district': openapi.Schema(type=openapi.TYPE_STRING),             
                # Add other properties as needed
            },            
        ),
        responses={
            201: openapi.Response(
                "XLS document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
            400: "Bad Request",
        },
        operation_summary="Retrieves a report in MS Excel file for detainees according to the filters provided",
        operation_description="This downloads a MS Excel file report, for other detainees with optional filtering the range of registration date and district",
        tags=["Reports"],
    )
    def download_detainees(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).select_related('district', 'detainee')
        district_name = request.data.get('district')        
        if district_name:
            queryset = queryset.filter(district__name=district_name)
        
        if request.data.get("initial_date"):            
            initial_date_str = request.data["initial_date"]
            initial_date = parser.isoparse(initial_date_str)
            initial_date_utc = initial_date.astimezone(timezone.utc)        
        else:
            initial_date_utc = None        
        
        if request.data.get("final_date"):
            final_date_str = request.data["final_date"]
            final_date = parser.isoparse(final_date_str)
            final_date_utc = final_date.astimezone(timezone.utc)            
        else:
            final_date_utc = None

        if initial_date_utc and final_date_utc:  
            queryset=queryset.filter(entry_date__gte=initial_date_utc, entry_date__lte=final_date_utc)           
        
        if initial_date_utc and final_date_utc is None:            
            queryset=queryset.filter(entry_date__gte=initial_date_utc) 
        
        if initial_date_utc is None and final_date_utc:            
            queryset=queryset.filter(entry_date__gte=final_date_utc) 
        

        serializer = self.get_serializer(queryset, many=True)        
        combined_data=[]
        # Iterate over serializer.data and combine with detainees_serializer.data
        for record in serializer.data:
            print("ENTRY DATE :", record['entry_date'])
            entry_date_string = record['entry_date']
            # Attempt to use format with milliseconds
            try:    
                entry_date_object = datetime.strptime(entry_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')   
            except ValueError:  
                # If ValueError occurs, fall back to format without milliseconds    
                entry_date_object = datetime.strptime(entry_date_string, '%Y-%m-%dT%H:%M:%SZ')  

            formatted_entry_date = entry_date_object.strftime('%d-%m-%Y %H:%M')

            formatted_official_release_date=""
            formatted_release_qualification_date=""

            if record['qualification_release_date']:
                qualification_release_date_date_string = record['qualification_release_date']
            # Attempt to use format with milliseconds
                try:    
                    qualification_release_date_date_object = datetime.strptime(qualification_release_date_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')   
                except ValueError:  
                    # If ValueError occurs, fall back to format without milliseconds    
                    qualification_release_date_date_object = datetime.strptime(qualification_release_date_date_string, '%Y-%m-%dT%H:%M:%SZ')  

                formatted_release_qualification_date = qualification_release_date_object.strftime('%d-%m-%Y %H:%M')                
            
            if record['official_release_date']:
                official_release_date_string = record['official_release_date']
                # Attempt to use format with milliseconds
                try:    
                    official_release_date_object = datetime.strptime(official_release_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')   
                except ValueError:  
                    # If ValueError occurs, fall back to format without milliseconds    
                    official_release_date_object = datetime.strptime(official_release_date_string, '%Y-%m-%dT%H:%M:%SZ')  

                formatted_official_release_date = official_release_date_object.strftime('%d-%m-%Y %H:%M')             

            combined_item = {
                "Distrito": record['district']['name'],
                "Nombre": record['detainee']['name'],
                "A.Paterno": record['detainee']['fathers_name'],
                "A.Materno": record['detainee']['mothers_name'],
                "Fecha de nacimiento": record['detainee']['birth_date'],
                "Edad": record['detainee']['age'],
                "Sexo": record['detainee']['gender'],
                "Orientación sexual": record['detainee']['sexual_preferences'],
                "Estado civil": record['detainee']['marital_status'],                
                "Etnia": record['detainee']['ethnicity'],                
                "Escolaridad": record['detainee']['schooling'],                
                "Ocupación": record['detainee']['occupation'],                
                "Nacionalidad": record['detainee']['nationality'],                
                "Nombre(s) falso(s)": record['detainee']['fake_names'],
                "Alias": record['detainee']['nicknames'],
                "Folio AFI": record['folio_afi'],
                "Fecha de ingreso": formatted_entry_date,                
                "Liberado": "Si" if record['has_been_released'] else "No",
                "Fecha de calificación de salida":formatted_release_qualification_date,
                "Fecha oficial de salida":formatted_official_release_date,
                "Sanción":record['sanction'],                
                "Tipo de salida":record['release_type'],
                "Motivo de salida":record['release_reason'],
                "Notas":record['notes']                
                # "Folio de otro registro":record['other_record_folio'],
                # "Motivo": record['reason'],
                # "Fecha y hora":record['date'],#hardcoded the username while the toked decode is ready
                # "Lugar" : record['place'],
                # "Nombre de quien asegura":record['holder_name'],
                # "Tipo de vehiculo":record['vehicle_type'],
                # "Linea" : record['line'],
                # "Marca":record['brand'],                                
                # "Diferenciador" :record['discriminator'],
                # "Tipo" :record['type'],
                # "Subtipo" :record['subtype'],
                # "Descripción" :record['description'],
                # "Cantidad" : record['quantity'],
                # "Condición general" : record['general_condition'],        
                # "Modelo":record['model'],
                # "Color":record['color'],
                # "Placas" : record['plates'],        
                # "Número de serie":record['serial_number'],
                # "Número de engomado" : record['stamp_number'],                                         
                # "Número de emisión" : record['emission_number'],                                         
                # "Asociación que expide":record['association_expeditor'],                                            
                # "Notas":record['comments'],                
                # "Registrado por":record['created_by'],
                # 'Detenidos relacionados': related_detainees
            }

            # Add the combined object to the result array
            combined_data.append(combined_item)

        if len(combined_data)==0:
            df = pd.DataFrame(columns=[
                "Distrito", "Nombre", "A.Paterno", "A.Materno", "Fecha de nacimiento", "Edad",
                "Sexo", "Orientación sexual", "Estado civil", "Etnia", "Escolaridad", "Ocupación",
                "Nacionalidad", "Nombre(s) falso(s)", "Alias", "Folio AFI", "Fecha de ingreso",
                "Liberado", "Fecha de calificación de salida", "Fecha oficial de salida", "Sanción",
                "Tipo de salida", "Motivo de salida", "Notas"
            ])
        else:
            df = pd.DataFrame(combined_data)

        buffer = BytesIO()

        # Customize column names, styles, and widths as needed
        # column_mapping = {
        #     "district": "District",
        #     "other_record_folio": "Other Record Folio",
        #     # Add other mappings as needed
        # }

        #df = df.rename(columns=column_mapping)

        # Customize column styles and widths using ExcelWriter
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Detenidos')

            # Access the XlsxWriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Detenidos']

            # Customize styles and widths as needed
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center'})

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                # Customize column widths
                if (value=='Distrito'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Nombre'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                if (value=='A.Paterno'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='A.Materno'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Fecha de nacimiento'):
                    worksheet.set_column(col_num, col_num, len(value) + 2)
                if (value=='Edad'):
                    worksheet.set_column(col_num, col_num, len(value) + 2)
                if (value=='Sexo'):
                    worksheet.set_column(col_num, col_num, len(value) + 8)
                if (value=='Orientación sexual'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Estado civil'):
                    worksheet.set_column(col_num, col_num, len(value) + 2)
                if (value=='Etnia'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Escolaridad'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Ocupación'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Nacionalidad'):
                    worksheet.set_column(col_num, col_num, len(value) + 12)
                if (value=='Nombre(s) falso(s)'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Alias'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Folio AFI'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Fecha de ingreso'):
                    worksheet.set_column(col_num, col_num, len(value) + 10)
                if (value=='Liberado'):
                    worksheet.set_column(col_num, col_num, len(value) + 2)
                if (value=='Fecha de calificación de salida'):
                    worksheet.set_column(col_num, col_num, len(value) + 5)
                if (value=='Fecha oficial de salida'):
                    worksheet.set_column(col_num, col_num, len(value) + 5)
                if (value=='Sanción'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Tipo de salida'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Motivo de salida'):
                    worksheet.set_column(col_num, col_num, len(value) + 15)
                if (value=='Notas'):
                    worksheet.set_column(col_num, col_num, len(value) + 20)
                # if (value=='Asociación que expide'):
                #     worksheet.set_column(col_num, col_num, len(value) + 12)
                # if (value=='Notas'):
                #     worksheet.set_column(col_num, col_num, len(value) + 20)
                # if (value=='Registrado por'):
                #     worksheet.set_column(col_num, col_num, len(value) + 20)
                # if (value=='Detenidos relacionados'):
                #     worksheet.set_column(col_num, col_num, len(value) + 2)
                # if (value=='Último detenido'):
                #     worksheet.set_column(col_num, col_num, len(value) + 20)

        # Set the buffer's cursor position to the beginning
        buffer.seek(0)

        # Create a file name for the Excel file
        filename = 'Detenidos.xlsx'

        # Create a StreamingHttpResponse to stream the file to the client
        response = StreamingHttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'

        return response
        #return Response({"status": "success", "data": combined_data}, status=status.HTTP_200_OK)



# Create your views here.
