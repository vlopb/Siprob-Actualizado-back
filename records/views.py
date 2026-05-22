import re
import pytz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
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
from records.models import Records, MedicalInformation, Actions, Offended, Events, Cells, Belongings, OtherRecordsDetainees
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import requests
from detainees.models import Detainee
from districts.models import District
from records.serializers import MedicalInformationSerializer, BelongingsSerializer, OtherRecordsSerializer, OtherRecordsDetaineesSerializer
from detainees.serializers import DetaineesSerializer
from districts.serializers import DistrictsSerializer
from datetime import datetime, timedelta
from users.models import User
from users.serializers import RetrieveUserSerializer
from rest_framework.permissions import IsAuthenticated
from users.utils import decode_token
import locale
from django.forms.models import model_to_dict

def format_datetime(dt, timezone_str='America/Denver', format_str="%d de %B de %Y %H:%M"):
    local_timezone = pytz.timezone(timezone_str)
    localized_datetime = dt.astimezone(local_timezone)
    return localized_datetime.strftime(format_str)

default_prints_url="http://siprob-prints:3000/"

# Create your views here.
class RecordsViewSet(viewsets.ModelViewSet):
    general_data_schema_response = {
        "record_id": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_id": openapi.Schema(type=openapi.TYPE_STRING),
        "record_folio": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_entry_date": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        "detainee_sanction": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_process": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_release_date": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
    }

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Records listed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties=general_data_schema_response,
                        )
                    },
                ),
            ),
        },
        operation_summary="Lists all records",
        operation_description="This endpoint lists all the records.",
        tags=["Records"],
    )
    def get(self, request, *args, **kwargs):
        records = Records.objects.prefetch_related("detainee")

        records_list = [
            {
                "record_id": record.id,
                "detainee_id": record.detainee.id,
                "folio_afi": record.folio_afi,
                "detainee_name": record.detainee.name,
                "detainee_fathers_name": record.detainee.fathers_name,
                "detainee_mothers_name": record.detainee.mothers_name,
                "detainee_entry_date": record.entry_date,
                "detainee_sanction": record.sanction,
                "detainee_process": record.process,
                "detainee_qualification_release_date": record.qualification_release_date,
            }
            for record in records
        ]

        # Devuelve la respuesta JSON
        return JsonResponse({"status": "success", "data": records_list}, safe=False)

        # return Role.objects.filter(is_active=True)


class SingleRecordViewSet(viewsets.ModelViewSet):
    queryset = Records.objects.all()
    serializer_class = RecordsSerializer
    general_data_schema_response = {
        "record_id": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_id": openapi.Schema(type=openapi.TYPE_STRING),
        "folio_afi": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_entry_date": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        "detainee_sanction": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_process": openapi.Schema(type=openapi.TYPE_STRING),
        "detainee_release_date": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Folio of the record",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Records shown successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties=general_data_schema_response,
                        )
                    },
                ),
            ),
        },
        operation_summary="Retrieves the record with the folio provided in url",
        operation_description="This endpoint retrieves the information of the record.",
        tags=["Records"],
    )
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        records = Records.objects.filter(folio=pk).prefetch_related("detainee")

        records_list = [
            {
                "record_id": record.id,
                "detainee_id": record.detainee.id,
                "folio_afi": record.folio_afi,
                "detainee_name": record.detainee.name,
                "detainee_fathers_name": record.detainee.fathers_name,
                "detainee_mothers_name": record.detainee.mothers_name,
                "detainee_entry_date": record.entry_date,
                "detainee_sanction": record.sanction,
                "detainee_process": record.process,
                "detainee_qualification_release_date": record.qualification_release_date,
            }
            for record in records
        ]
        if len(records_list) == 0:
            return JsonResponse(
                {"status": "success", "message": "record_not_found"}, safe=False
            )
        medical_informations = MedicalInformation.objects.filter(
            record_id=records_list[0].get("record_id")
        )
        medical_list = [
            {
                "medic_info_id": med_info.id,
                "medic_name": med_info.medic_name,
                "medical_cedula":med_info.medical_cedula,
                'medical_date_time':med_info.medical_date_time,
                # "medic_name": med_info.medic.name,
                # "medic_father_name": med_info.medic.name,
                # "medic_mothers_name": med_info.medic.name,
                "medic_weight": med_info.weight,
                "medic_height": med_info.height,
                "medic_intoxication": med_info.intoxication,
                "medic_mental": med_info.mental,
                "medic_general_condition": med_info.general_condition,
                "medic_pathologies": med_info.pathologies,
                "medic_to": med_info.medical_t,
                "medic_fc": med_info.medical_fc,
                "medic_fr": med_info.medical_fr,
                "medic_ta": med_info.medical_ta,
                "medic_saturation": med_info.saturation,
                "medic_blood_type": med_info.blood_type,
                "medic_rh_factor": med_info.rh_factor,
                "medic_diagnostic": med_info.diagnostic,
                "medic_created_at": med_info.created_at,
                "medic_updated_at": med_info.updated_at,
            }
            for med_info in medical_informations
        ]
        records_list[0]["medical_information"] = medical_list

        events_list = Events.objects.filter(
            record_id=records_list[0].get("record_id")
        ).prefetch_related("record")

        events_list = [
            {
                "event_id": event.id,
                "detention_datetime": event.detention_datetime,
                "violence": event.violence,
                "ambient": event.ambient,
                "movil": event.movil,
                "modus_operandi": event.modus_operandi,
                "description": event.event_description,
                "datetime": event.event_datetime,
                "discriminator": event.discriminator,
                "type": event.type,
                "subtype": event.subtype,
                "reason": event.reason,
                "place": event.place,
                "unit": event.unit,
                "sector": event.sector,
                "clasification": event.clasification,
                "locality": event.locality,
                "country": event.country,
                "street": event.street,
                "exterior_number": event.exterior_number,
                "interior_number": event.interior_number,
                "colony": event.colony,
                "cross_street": event.cross_street,
                "is_active": event.is_active,
                "created_at": event.created_at,
                "updated_at": event.updated_at,
                "arrested_by_id": event.arrested_by,
                "record_id": event.record_id,
                "detention_type": event.detention_type
            }
            for event in events_list
        ]

        records_list[0]["detention_information"] = events_list

        records_list[0]["cell_information"] = "cell_list"

        return JsonResponse({"status": "success", "data": records_list[0]}, safe=False)

    record_data = {
        "medic_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            "medic": openapi.Schema(type=openapi.TYPE_STRING),
            "medical_cedula": openapi.Schema(type=openapi.TYPE_STRING),
            'medical_date_time':openapi.Schema(type=openapi.TYPE_STRING,format=openapi.FORMAT_DATETIME),
            "weight": openapi.Schema(type=openapi.TYPE_INTEGER),
            "height": openapi.Schema(type=openapi.TYPE_INTEGER),
            "intoxication": openapi.Schema(type=openapi.TYPE_STRING),
            "mental": openapi.Schema(type=openapi.TYPE_STRING),
            "general_condition": openapi.Schema(type=openapi.TYPE_STRING),
            "pathologies": openapi.Schema(type=openapi.TYPE_STRING),
            "TO": openapi.Schema(type=openapi.TYPE_STRING),
            "FC": openapi.Schema(type=openapi.TYPE_STRING),
            "FR": openapi.Schema(type=openapi.TYPE_STRING),
            "TA": openapi.Schema(type=openapi.TYPE_STRING),
            "saturation": openapi.Schema(type=openapi.TYPE_STRING),
            "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
            "blood_type": openapi.Schema(type=openapi.TYPE_STRING),
            "rh_factor": openapi.Schema(type=openapi.TYPE_STRING),
            "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
        }),
        "lesions": openapi.Schema(type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "location": openapi.Schema(type=openapi.TYPE_STRING),
                    "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
                    "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "notes": openapi.Schema(type=openapi.TYPE_STRING),
                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                },
            ),
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the medical record",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Medical record retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Retrieves a medical record with the id provided in url",
        operation_description="This endpoint retrieves medical record.",
        tags=["Records"],
    )
    def get_medic_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        medic_info = MedicalInformation.objects.filter(id=pk)

        if len(medic_info) == 0:
            return JsonResponse({"status": "error", "message": "medical_record_not_found"}, safe=False)

        formated_medic_information = [
            {
                "id": medic.id,
                "weight": medic.weight,
                "height": medic.height,
                "medical_folio": medic.folio,
                "intoxication": medic.intoxication,
                "mental": medic.mental,
                "general_condition": medic.general_condition,
                "medical_history_date": medic.created_at,
                "medic": medic.medic_name,
                "medical_cedula": medic.medical_cedula,
                "medical_date_time":medic.medical_date_time,
                "pathologies": medic.pathologies,
                "medical_t": medic.medical_t,
                "medical_fc": medic.medical_fc,
                "medical_fr": medic.medical_fr,
                "medical_ta": medic.medical_ta,
                "saturation": medic.saturation,
                "diagnostic": medic.diagnostic,
                "blood_type": medic.blood_type,
                "rh_factor": medic.rh_factor,
                "created_at": medic.created_at,
                "updated_at": medic.updated_at,
            }
            for medic in medic_info
        ]

        lesions = Lesions.objects.filter(medical_information_id=pk).values()

        formated_lesions = [
            {
                "id": lesion.get("id"),
                "location": lesion.get("location"),
                "discriminator": lesion.get("discriminator"),
                "image_path": lesion.get("image_path"),
                "description": lesion.get("description"),
                "notes": lesion.get("notes"),
                "created_at": lesion.get("created_at"),
                "updated_at": lesion.get("updated_at"),
            }
            for lesion in lesions
        ]
        med_info = MedicalInformation.objects.get(id=formated_medic_information[0].get('id'))
        record = Records.objects.get(id=med_info.record_id)
        formated_medic_information[0]['folio_afi'] = record.id
        response = {
            'medic_data': formated_medic_information[0],
            'lesions': formated_lesions,
        }

        return JsonResponse({"status": "success", "data": response}, safe=False)

    record_data = {
        "medic_name": openapi.Schema(type=openapi.TYPE_STRING),
        "medical_cedula": openapi.Schema(type=openapi.TYPE_STRING),
        'medical_date_time':openapi.Schema(type=openapi.TYPE_STRING,format=openapi.FORMAT_DATETIME),
        "weight": openapi.Schema(type=openapi.TYPE_INTEGER),
        "height": openapi.Schema(type=openapi.TYPE_INTEGER),
        "intoxication": openapi.Schema(type=openapi.TYPE_STRING),
        "mental": openapi.Schema(type=openapi.TYPE_STRING),
        "general_condition": openapi.Schema(type=openapi.TYPE_STRING),
        "pathologies": openapi.Schema(type=openapi.TYPE_STRING),
        "medical_t": openapi.Schema(type=openapi.TYPE_STRING),
        "medical_fc": openapi.Schema(type=openapi.TYPE_STRING),
        "medical_fr": openapi.Schema(type=openapi.TYPE_STRING),
        "medical_ta": openapi.Schema(type=openapi.TYPE_STRING),
        "saturation": openapi.Schema(type=openapi.TYPE_STRING),
        "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
        "blood_type": openapi.Schema(type=openapi.TYPE_STRING),
        "rh_factor": openapi.Schema(type=openapi.TYPE_STRING),
        "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
    }


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detainee",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Medical record added successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Adds a new medical record for a deatainee with the id provided in url",
        operation_description="This endpoint adds a new the record.",
        tags=["Records"],
    )
    def post_medic_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        medic_name = request.data.get("medic_name")
        medical_cedula = request.data.get("medical_cedula")
        medical_date_time = request.data.get("medical_date_time")
        weight = request.data.get("weight")
        height = request.data.get("height")
        created_by = request.data.get("created_by")
        intoxication = request.data.get("intoxication")
        mental = request.data.get("mental")
        general_condition = request.data.get("general_condition")
        pathologies = request.data.get("pathologies")
        medical_t = request.data.get("medical_t")
        medical_fc = request.data.get("medical_fc")
        medical_fr = request.data.get("medical_fr")
        medical_ta = request.data.get("medical_ta")
        saturation = request.data.get("saturation")
        diagnostic = request.data.get("diagnostic")
        blood_type = request.data.get("blood_type")
        rh_factor = request.data.get("rh_factor")

        today = timezone.now()
        medical_histories = Records.objects.filter(Q(detainee_id=pk) & Q(has_been_released=False)).values()

        latest = [
            {
                "record_id": medical_history['id'],
                "district":medical_history['district_id'],
                "folio_afi":medical_history['folio_afi']
            }
            for medical_history in medical_histories

        ]
        if len(latest) == 0:
            return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)
        else:
            print(latest[0])
            medic_info = MedicalInformation()
            medic_info.record_id = latest[0].get('record_id')
            medic_info.user_id = 1 # HARDCODED, MUST CHANGE LATER
            medic_info.medic_name = medic_name
            medic_info.medical_cedula=medical_cedula
            medic_info.medical_date_time=medical_date_time
            medic_info.weight = weight
            medic_info.height = height
            medic_info.intoxication = intoxication
            medic_info.mental = mental
            medic_info.general_condition = general_condition
            medic_info.pathologies = pathologies
            medic_info.medical_t = medical_t
            medic_info.medical_fc = medical_fc
            medic_info.medical_fr = medical_fr
            medic_info.medical_ta = medical_ta
            medic_info.saturation = saturation
            medic_info.diagnostic = diagnostic
            medic_info.blood_type = blood_type
            medic_info.rh_factor = rh_factor
            server_time = datetime.now()
            offset_hours = int(request.headers.get('offset-time', -6))
            client_time = server_time + timedelta(hours=offset_hours)
            formatted_client_time = client_time.strftime('%Y-%m-%dT%H:%M:%S')
            total_medical_histories = MedicalInformation.objects.filter(record=latest[0].get('record_id')).values()
            record_information=Records.objects.get(pk=medic_info.record_id)

            district_name=""
            try:
                # district_id = general_data.get('district')
                district_information = District.objects.get(pk=latest[0].get('district'))
                district_name = district_information.name[:3]
            except District.DoesNotExist:
                district_information = None
            folio = 'MED-'+district_name+'-'+pk+'-'+formatted_client_time
            medic_info.folio=folio
            medic_info.created_by=created_by
            medic_info.save()
            response_data = request.data
            response_data['medical_folio']=folio
            response_data['medical_history_date']=medic_info.created_at
            response_data['medical_cedula']=medic_info.medical_cedula
            response_data['medical_date_time']=medic_info.medical_date_time
            # response_data['medic']=medic_info.medic_name
            response_data['created_by']=medic_info.created_by
            response_data['created_at']=medic_info.created_at
            response_data['updated_at']=medic_info.updated_at
            response_data['id']=medic_info.id
            response_data['folio_afi']=latest[0].get('folio_afi')


        return JsonResponse({"status": "success", "data": response_data}, safe=False)

    record_data = {
        "discriminator": openapi.Schema(type=openapi.TYPE_INTEGER),
        "location": openapi.Schema(type=openapi.TYPE_INTEGER),
        "description": openapi.Schema(type=openapi.TYPE_INTEGER),
        "image_path": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the medical record",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Lesions record added successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Adds a new lesion record for a medical information with the id provided in url",
        operation_description="This endpoint adds a new the lesion.",
        tags=["Records"],
    )
    def post_lesions_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        discriminator = request.data.get("discriminator")
        location = request.data.get("location")
        description = request.data.get("description")
        notes = request.data.get("notes")
        image_path = request.data.get("image_path")

        medical_info = MedicalInformation.objects.filter(id=pk).values()

        print(len(medical_info))
        if len(medical_info) == 0:
            return JsonResponse({"status": "error", "message": "medical_record_not_found"}, safe=False)
        else:
            lesion = Lesions()
            lesion.discriminator = discriminator
            lesion.location = location
            lesion.description = description
            lesion.notes = notes
            lesion.image_path = image_path
            lesion.medical_information_id = pk
            lesion.save()

        return JsonResponse({"status": "success", "data": request.data}, safe=False)

    record_data = {
        "qualifies": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "qualification_release_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "minimum_salaries": openapi.Schema(type=openapi.TYPE_INTEGER),
        "qualified_hours": openapi.Schema(type=openapi.TYPE_INTEGER),
        "aggravating_factors": openapi.Schema(type=openapi.TYPE_INTEGER),
        "adjustment": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_payable": openapi.Schema(type=openapi.TYPE_INTEGER),
        "basis": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detention event record",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Detention event record qualified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Qualifies a detention record",
        operation_description="This endpoint qualifies a detention record.",
        tags=["Records"],
    )
    def qualify_detention(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            events = Events.objects.get(id=pk)
            active_records = Records.objects.filter(Q(id=events.record_id) & Q(has_been_released=False)).values()

            latest = [
                {
                    "record_id": active_record['id'],
                    "qualification_release_date": active_record['qualification_release_date'],
                }
                for active_record in active_records
            ]

            if len(latest) == 0:
                return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)
            latest_record = Records.objects.get(id=latest[0].get('record_id'))
            latest_record.qualification_release_date = request.data.get('qualification_release_date')
            latest_record.save()
            if request.data.get('qualifies') == True:
                events.qualifies = request.data.get('qualifies')
                events.minimum_salaries = request.data.get('minimum_salaries')
                events.qualified_hours = request.data.get('qualified_hours')
                events.aggravating_factors = request.data.get('aggravating_factors')
                events.adjustment = request.data.get('adjustment')
                events.total_payable = request.data.get('total_payable')
                events.basis = request.data.get('basis')
            else:
                events.qualifies = request.data.get('qualifies')
            events.save()
            request.data['id'] = events.id
            request.data['qualification_release_date'] = latest_record.qualification_release_date
        except Events.DoesNotExist:
            return JsonResponse({"status": "error", "message": "event not found"}, safe=False)
        except Records.DoesNotExist:
            return JsonResponse({"status": "error", "message": "event not found"}, safe=False)

        return JsonResponse({"status": "success", "data": request.data}, safe=False)

    record_data = {
        "detention_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        "event_datetime": openapi.Schema(type=openapi.TYPE_STRING),
        "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
        "type": openapi.Schema(type=openapi.TYPE_STRING),
        "subtype": openapi.Schema(type=openapi.TYPE_STRING),
        "violence": openapi.Schema(type=openapi.TYPE_STRING),
        "ambient": openapi.Schema(type=openapi.TYPE_STRING),
        "movil": openapi.Schema(type=openapi.TYPE_STRING),
        "modus_operandi": openapi.Schema(type=openapi.TYPE_STRING),
        "event_description": openapi.Schema(type=openapi.TYPE_STRING),
        "detention_datetime": openapi.Schema(type=openapi.TYPE_STRING),
        "detention_type": openapi.Schema(type=openapi.TYPE_STRING),
        "reason": openapi.Schema(type=openapi.TYPE_STRING),
        "arrested_by": openapi.Schema(type=openapi.TYPE_STRING),
        "place": openapi.Schema(type=openapi.TYPE_STRING),
        "unit": openapi.Schema(type=openapi.TYPE_STRING),
        "sector": openapi.Schema(type=openapi.TYPE_STRING),
        "clasification": openapi.Schema(type=openapi.TYPE_STRING),
        "locality": openapi.Schema(type=openapi.TYPE_STRING),
        "municipality": openapi.Schema(type=openapi.TYPE_STRING),
        "country": openapi.Schema(type=openapi.TYPE_STRING),
        "street": openapi.Schema(type=openapi.TYPE_STRING),
        "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
        "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
        "colony": openapi.Schema(type=openapi.TYPE_STRING),
        }),
        "offendeds": openapi.Schema(type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_STRING),
                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                    "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "relationship": openapi.Schema(type=openapi.TYPE_STRING),
                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                },
            ),
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detention event record",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Detention event record retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Retrieves a detention event record with the id provided in url",
        operation_description="This endpoint retrieves detention event record.",
        tags=["Records"],
    )
    def get_detention_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        events_info = Events.objects.filter(id=pk).prefetch_related('record')
        if len(events_info) == 0:
            return JsonResponse({"status": "error", "message": "detention_record_not_found"}, safe=False)

        formated_detention_information = [
            {
                'id': event.id,
                'event_datetime': event.event_datetime,
                'discriminator': event.discriminator,
                'type': event.type,
                'folio_afi': event.record.folio_afi,
                'detention_folio': event.detention_folio,
                'created_by': event.created_by,
                'subtype': event.subtype,
                'violence': event.violence,
                'ambient': event.ambient,
                'movil': event.movil,
                'modus_operandi': event.modus_operandi,
                'event_description': event.event_description,
                'detention_datetime': event.detention_datetime,
                'detention_type': event.detention_type,
                'reason': event.reason,
                'arrested_by': event.arrested_by,
                'place': event.place,
                'unit': event.unit,
                'sector': event.sector,
                'clasification': event.clasification,
                'locality': event.locality,
                'municipality': event.municipality,
                'country': event.country,
                'street': event.street,
                'exterior_number': event.exterior_number,
                'interior_number': event.interior_number,
                'colony': event.colony,
                'cross_street': event.cross_street,
                'qualifies': event.qualifies,
                'minimum_salaries': event.minimum_salaries,
                'qualified_hours': event.qualified_hours,
                'aggravating_factors': event.aggravating_factors,
                'adjustment': event.adjustment,
                'total_payable': event.total_payable,
                'basis': event.basis
            }
            for event in events_info
        ]

        events = Events.objects.get(id=pk)
        active_records = Records.objects.filter(Q(id=events.record_id)).values()

        latest = [
            {
                "record_id": active_record['id'],
                "qualification_release_date": active_record['qualification_release_date'],
            }
            for active_record in active_records
        ]

        detention_data = {
            'id': formated_detention_information[0].get('id'),
            'event_datetime': formated_detention_information[0].get('event_datetime'),
            'qualification_release_date': latest[0].get('qualification_release_date'),
            'discriminator': formated_detention_information[0].get('discriminator'),
            'type': formated_detention_information[0].get('type'),
            'folio_afi': formated_detention_information[0].get('folio_afi'),
            'detention_folio': formated_detention_information[0].get('detention_folio'),
            'created_by': formated_detention_information[0].get('created_by'),
            'subtype': formated_detention_information[0].get('subtype'),
            'violence': formated_detention_information[0].get('violence'),
            'ambient': formated_detention_information[0].get('ambient'),
            'movil': formated_detention_information[0].get('movil'),
            'modus_operandi': formated_detention_information[0].get('modus_operandi'),
            'event_description': formated_detention_information[0].get('event_description'),
        }

        detention_location = {
            'detention_datetime': formated_detention_information[0].get('detention_datetime'),
            'detention_type': formated_detention_information[0].get('detention_type'),
            'reason': formated_detention_information[0].get('reason'),
            'arrested_by': formated_detention_information[0].get('arrested_by'),
            'place': formated_detention_information[0].get('place'),
            'unit': formated_detention_information[0].get('unit'),
            'sector': formated_detention_information[0].get('sector'),
            'clasification': formated_detention_information[0].get('clasification'),
            'locality': formated_detention_information[0].get('locality'),
            'municipality': formated_detention_information[0].get('municipality'),
            'country': formated_detention_information[0].get('country'),
            'street': formated_detention_information[0].get('street'),
            'exterior_number': formated_detention_information[0].get('exterior_number'),
            'interior_number': formated_detention_information[0].get('interior_number'),
            'colony': formated_detention_information[0].get('colony'),
            'cross_street': formated_detention_information[0].get('cross_street'),
        }

        detention_qualification = {
            'qualifies': formated_detention_information[0].get('qualifies'),
            'minimum_salaries': formated_detention_information[0].get('minimum_salaries'),
            'qualified_hours': formated_detention_information[0].get('qualified_hours'),
            'aggravating_factors': formated_detention_information[0].get('aggravating_factors'),
            'adjustment': formated_detention_information[0].get('adjustment'),
            'total_payable': formated_detention_information[0].get('total_payable'),
            'basis': formated_detention_information[0].get('basis'),
        }

        offendeds = Offended.objects.filter(event_id=pk)

        formated_offendeds = [
            {
                "id": offended.id,
                "name": offended.name,
                "fathers_name": offended.fathers_name,
                "mothers_name": offended.mothers_name,
                "relationship": offended.relationship,
                "created_at": offended.created_at,
                "updated_at": offended.updated_at,
            }
            for offended in offendeds
        ]

        response = {
            'detention_data': detention_data,
            'detention_location': detention_location,
            'detention_qualification': detention_qualification,
            'offendeds': formated_offendeds,
        }

        # events = Events.objects.get(id=pk)
        # active_records = Records.objects.filter(Q(id=events.record_id) & Q(has_been_released=True)).values()

        # latest = [
        #     {
        #         "record_id": active_record['id'],
        #         "qualification_release_date": active_record['qualification_release_date'],
        #     }
        #     for active_record in active_records
        # ]

        return JsonResponse({"status": "success", "data": response}, safe=False)

    record_data = {
        "detention_data": openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                "event_datetime": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "subtype": openapi.Schema(type=openapi.TYPE_STRING),
                "violence": openapi.Schema(type=openapi.TYPE_STRING),
                "violence": openapi.Schema(type=openapi.TYPE_STRING),
                "ambient": openapi.Schema(type=openapi.TYPE_STRING),
                "movil": openapi.Schema(type=openapi.TYPE_STRING),
                "modus_operandi": openapi.Schema(type=openapi.TYPE_STRING),
                "event_description": openapi.Schema(type=openapi.TYPE_STRING),
                                         }),
        "detention_location": openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                "detention_datetime": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "detention_type": openapi.Schema(type=openapi.TYPE_STRING),
                "reason": openapi.Schema(type=openapi.TYPE_STRING),
                "arrested_by": openapi.Schema(type=openapi.TYPE_STRING),
                "place": openapi.Schema(type=openapi.TYPE_STRING),
                "unit": openapi.Schema(type=openapi.TYPE_STRING),
                "sector": openapi.Schema(type=openapi.TYPE_STRING),
                "clasification": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "cross_street": openapi.Schema(type=openapi.TYPE_STRING),
            }),
        "offendeds": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                    "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "relationship": openapi.Schema(type=openapi.TYPE_STRING)
                },
            ),
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detianee",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Detention info added",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Adds detention information for the detainne id provided in url",
        operation_description="This endpoint adds new detention information.",
        tags=["Records"],
    )
    def post_detention_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        active_records = Records.objects.filter(Q(detainee_id=pk) & Q(has_been_released=False)).values()

        latest = [
            {
                "record_id": active_record['id'],
                "qualification_release_date": active_record['qualification_release_date'],
            }
            for active_record in active_records
        ]

        if len(latest) == 0:
            return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)


        detention_data = request.data.get('detention_data')
        detention_location = request.data.get('detention_location')
        offendeds = request.data.get('offendeds')
        if request.data.get('offendeds') == None:
            offendeds = []

        event_datetime = detention_data.get('event_datetime')
        discriminator = detention_data.get('discriminator')
        type = detention_data.get('type')
        subtype = detention_data.get('subtype')
        violence = detention_data.get('violence')
        ambient = detention_data.get('ambient')
        movil = detention_data.get('movil')
        modus_operandi = detention_data.get('modus_operandi')
        events_description = detention_data.get('event_description')
        created_by = detention_data.get('created_by')

        detention_datetime = detention_location.get('detention_datetime')
        detention_type = detention_location.get('detention_type')
        reason = detention_location.get('reason')
        arrested_by = detention_location.get('arrested_by')
        place = detention_location.get('place')
        unit = detention_location.get('unit')
        sector = detention_location.get('sector')
        clasification = detention_location.get('clasification')
        locality = detention_location.get('locality')
        municipality = detention_location.get('municipality')
        street = detention_location.get('street')
        exterior_number = detention_location.get('exterior_number')
        interior_number = detention_location.get('interior_number')
        colony = detention_location.get('colony')
        cross_street = detention_location.get('cross_street')

        new_event = Events()
        new_event.record_id = latest[0].get('record_id')
        new_event.event_datetime = event_datetime
        new_event.discriminator = discriminator
        new_event.type = type
        new_event.subtype = subtype
        new_event.violence = violence
        new_event.ambient = ambient
        new_event.movil = movil
        new_event.modus_operandi = modus_operandi
        new_event.event_description = events_description
        new_event.detention_datetime = detention_datetime
        new_event.detention_type = detention_type
        new_event.reason = reason
        new_event.arrested_by = arrested_by
        new_event.place = place
        new_event.unit = unit
        new_event.sector = sector
        new_event.clasification = clasification
        new_event.locality = locality
        new_event.municipality = municipality
        new_event.street = street
        new_event.exterior_number = exterior_number
        new_event.interior_number = interior_number
        new_event.colony = colony

        medical_histories = Records.objects.filter(Q(detainee_id=pk) & Q(has_been_released=False)).values()

        latest = [
            {
                "record_id": medical_history['id'],
                "qualification_release_date": medical_history['qualification_release_date'],
                "district":medical_history['district_id'],
                "folio_afi":medical_history['folio_afi']
            }
            for medical_history in medical_histories
        ]
        if len(latest) == 0:
            return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)

        server_time = datetime.now()
        offset_hours = int(request.headers.get('offset-time', -6))
        client_time = server_time + timedelta(hours=offset_hours)
        formatted_client_time = client_time.strftime('%Y-%m-%dT%H:%M:%S')
        district_name=""
        try:
            # district_id = general_data.get('district')
            district_information = District.objects.get(id=latest[0].get('district'))
            district_name = district_information.name[:3]
        except District.DoesNotExist:
            district_information = None
        folio = 'DET-'+district_name+'-'+pk+'-'+formatted_client_time

        new_event.detention_folio = folio
        new_event.cross_street = cross_street
        new_event.created_by = created_by
        new_event.save()

        for offended in offendeds:
            new_offended = Offended()
            new_offended.event_id = new_event.id
            new_offended.name = offended.get('name')
            new_offended.fathers_name = offended.get('fathers_name')
            new_offended.mothers_name = offended.get('mothers_name')
            new_offended.relationship = offended.get('relationship')
            new_offended.save()
        response = request.data
        response['detention_data']['id'] = new_event.id
        response['detention_data']['folio_afi'] = latest[0].get('folio_afi')
        response['detention_data']['detention_folio'] = latest[0].get('folio_afi')
        response['detention_data']['created_by'] = new_event.created_by
        response['detention_data']['created_at'] = new_event.created_at
        response['detention_data']['updated_at'] = new_event.updated_at

        return JsonResponse({"status": "success", "data": response}, safe=False)

    record_data = {
        "cell": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
        "user": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detainee",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Cell assigned correctly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Assigns a cell to a detainee",
        operation_description="This endpoint assigns a cell to a detainee.",
        tags=["Records"],
    )
    def assign_cell(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        cell_name = request.data.get('cell')
        cell_notes = request.data.get('cell_notes')
        created_by = request.data.get('created_by')
        latest_records = Records.objects.filter(Q(detainee_id=pk) & Q(has_been_released=False)).values()

        latest = [
            {
                "record_id": latest_record['id'],
                "qualification_release_date": latest_record['qualification_release_date'],
                "folio_afi": latest_record['folio_afi'],
            }
            for latest_record in latest_records
        ]
        if len(latest) == 0:
                return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)
        server_time = datetime.now()
        offset_hours = int(request.headers.get('offset-time', -6))
        client_time = server_time + timedelta(hours=offset_hours)
        formatted_client_time = client_time.strftime('%Y-%m-%dT%H:%M:%S')
        district_name=""
        try:
            district_information = District.objects.get(pk=latest[0].get('district'))
            district_name = district_information.name[:3]
        except District.DoesNotExist:
            district_information = None
        folio = 'CEL-'+district_name+'-'+pk+'-'+formatted_client_time

        if len(latest) == 0:
            return JsonResponse({"status": "error", "message": "detainee_does_not_have_active_records"}, safe=False)
        cell = Cells()
        cell.record_id = latest[0].get('record_id')
        cell.cell = cell_name
        cell.assignment_folio = folio
        cell.created_by = created_by
        cell.cell_notes = cell_notes
        cell.save()
        response_data = {
            "id": cell.id,
            "cell": cell.cell,
            "notes": cell.cell_notes,
            "created_by": cell.created_by,
            "folio_afi": latest[0].get('folio_afi'),
            "assignment_folio": cell.assignment_folio,
            "created_at": cell.created_at,
            "updated_at": cell.updated_at,
        }
        return JsonResponse({"status": "success", "data": response_data}, safe=False)

    record_data = {
        "total_belongings": openapi.Schema(type=openapi.TYPE_INTEGER),
        "registration_datetime": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "accesories_backpack": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_belt": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_cap": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_cigarettes": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_handbag": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_other": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_ribbons": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_shoes": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_sunglasses": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "accesories_notes": openapi.Schema(type=openapi.TYPE_STRING),
        "bank_cards": openapi.Schema(type=openapi.TYPE_STRING),
        "delivery_notes": openapi.Schema(type=openapi.TYPE_STRING),
        "devices_aux": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_cables": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_cellphone": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_charger": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_computer_equipment": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_keys": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_laptop": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_tablet": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_usb": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "devices_notes": openapi.Schema(type=openapi.TYPE_STRING),
        "document_american_passport": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "document_ine": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "document_mexican_passport": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "document_other": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "document_residence": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "document_notes": openapi.Schema(type=openapi.TYPE_STRING),
        "jewelry_bracelet": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_chain": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_clock": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_earrings": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_other": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_ring": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        "jewelry_notes": openapi.Schema(type=openapi.TYPE_STRING),
        "money_american_dollars": openapi.Schema(type=openapi.TYPE_INTEGER, default=False),
        "money_mexican_pesos": openapi.Schema(type=openapi.TYPE_INTEGER, default=False),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the detainee",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Belongings registered successfuly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Registers the detainee belongings",
        operation_description="Registers the detainee belongings.",
        tags=["Records"],
    )
    def register_belongings(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        registered_belongings = Belongings.objects.filter(cell_id=pk).values()
        registered_belongings_array = [
            {
                "cell_id": belonging['cell_id'],
            }
            for belonging in registered_belongings
        ]
        if len(registered_belongings_array) != 0:
            return JsonResponse({"status": "error", "message": "detainee_has_belongings_registered"}, safe=False)
        try:
            cell = Cells.objects.get(id=pk)
            if request.data.get('total_belongings') == None:
                cell.total_belongings = 0
            else:
                cell.total_belongings = request.data.get('total_belongings')
            cell.save()
        except Cells.DoesNotExist:
            print("cell does not exist")
        belongings = Belongings()
        belongings.cell_id = pk
        belongings.registration_datetime = request.data.get('registration_datetime')
        belongings.accesories_backpack = request.data.get('accesories_backpack')
        belongings.accesories_belt = request.data.get('accesories_belt')
        belongings.accesories_cap = request.data.get('accesories_cap')
        belongings.accesories_cigarettes = request.data.get('accesories_cigarettes')
        belongings.accesories_handbag = request.data.get('accesories_handbag')
        belongings.accesories_other = request.data.get('accesories_other')
        belongings.accesories_ribbons = request.data.get('accesories_ribbons')
        belongings.accesories_shoes = request.data.get('accesories_shoes')
        belongings.accesories_sunglasses = request.data.get('accesories_sunglasses')
        belongings.accesories_notes = request.data.get('accesories_notes')
        belongings.bank_cards = request.data.get('bank_cards')
        belongings.delivery_notes = request.data.get('delivery_notes')
        belongings.devices_aux = request.data.get('devices_aux')
        belongings.devices_cables = request.data.get('devices_cables')
        belongings.devices_cellphone = request.data.get('devices_cellphone')
        belongings.devices_charger = request.data.get('devices_charger')
        belongings.devices_computer_equipment = request.data.get('devices_computer_equipment')
        belongings.devices_keys = request.data.get('devices_keys')
        belongings.devices_laptop = request.data.get('devices_laptop')
        belongings.devices_tablet = request.data.get('devices_tablet')
        belongings.devices_notes = request.data.get('devices_notes')
        belongings.devices_usb = request.data.get('devices_usb')
        belongings.document_american_passport = request.data.get('document_american_passport')
        belongings.document_ine = request.data.get('document_ine')
        belongings.document_mexican_passport = request.data.get('document_mexican_passport')
        belongings.document_other = request.data.get('document_other')
        belongings.document_residence = request.data.get('document_residence')
        belongings.document_notes = request.data.get('document_notes')
        belongings.jewelry_bracelet = request.data.get('jewelry_bracelet')
        belongings.jewelry_chain = request.data.get('jewelry_chain')
        belongings.jewelry_clock = request.data.get('jewelry_clock')
        belongings.jewelry_earrings = request.data.get('jewelry_earrings')
        belongings.jewelry_other = request.data.get('jewelry_other')
        belongings.jewelry_ring = request.data.get('jewelry_ring')
        belongings.jewelry_notes = request.data.get('jewelry_notes')
        belongings.money_american_dollars = request.data.get('money_american_dollars')
        belongings.money_mexican_pesos = request.data.get('money_mexican_pesos')
        belongings.save()

        return JsonResponse({"status": "success", "data": request.data}, safe=False)

    record_data = {
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "user": openapi.Schema(type=openapi.TYPE_STRING),
        "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
        "call_datetime": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "had_response": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "accepted": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "detainee_relationship": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the cell",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Call registered successfuly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Registers the calls of a detainee",
        operation_description="Registers the detainee calls.",
        tags=["Records"],
    )
    def register_calls(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            cell = Cells.objects.get(id=pk)
            if cell.total_calls == None:
                cell.total_calls = 1
            else:
                cell.total_calls = cell.total_calls + 1
            cell.save()

        except Cells.DoesNotExist:
            print("cell does not exists")
        call_registry = CallsRegistry()
        call_registry.cell_id = pk
        call_registry.name = request.data.get('name')
        call_registry.phone_number = request.data.get('phone_number')
        call_registry.call_datetime = request.data.get('call_datetime')
        call_registry.had_response = request.data.get('had_response')
        call_registry.accepted = request.data.get('accepted')
        call_registry.user = request.data.get('user')
        call_registry.detainee_relationship = request.data.get('detainee_relationship')
        call_registry.save()
        call_registry_id = call_registry.id
        response_data = request.data
        response_data['id'] = call_registry_id

        return JsonResponse({"status": "success", "data": response_data}, safe=False)

    record_data = {
        "delivered_to": openapi.Schema(type=openapi.TYPE_STRING),
        "delivered_to_another": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "relationship": openapi.Schema(type=openapi.TYPE_STRING),
        "datetime": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the cell record",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=record_data,
        ),
        responses={
            200: openapi.Response(
                description="Deliver registered successfuly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Registers the calls of a detainee",
        operation_description="Registers the detainee calls.",
        tags=["Records"],
    )
    def deliver_belongings(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        latest_records = Records.objects.filter(Q(detainee_id=pk) & Q(has_been_released=False)).values()
        latest = [
            {
                "record_id": latest_record['id'],
                "qualification_release_date": latest_record['qualification_release_date'],
            }
            for latest_record in latest_records
        ]
        try:
            belongings = Belongings.objects.get(cell_id=pk)
            if belongings.delivered == True:
                return JsonResponse({"status": "error", "message": "belongings_already_delivered"}, safe=False)

            belongings.delivered_to_another = request.data.get('delivered_to_another')
            belongings.delivered_to = request.data.get('delivered_to')
            belongings.delivery_relationship = request.data.get('relationship')
            belongings.delivery_datetime = request.data.get('datetime')
            belongings.delivery_notes = request.data.get('notes')
            belongings.delivered = True
            belongings.save()
        except Belongings.DoesNotExist:
            return JsonResponse({"status": "error", "message": "belongings_not_registered_yet"}, safe=False)

        return JsonResponse({"status": "success", "data": request.data}, safe=False)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the cell record",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Deliver registered successfuly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, properties=record_data
                        )
                    },
                ),
            ),
        },
        operation_summary="Registers the calls of a detainee",
        operation_description="Registers the detainee calls.",
        tags=["Records"],
    )
    def get_cell_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")


        cells = Cells.objects.filter(id=pk).prefetch_related('record')
        formated_cells = [
            {
                "id": cell.id,
                "cell": cell.cell,
                "created_by": cell.created_by,
                "folio_afi": cell.record.folio_afi,
                "cell_folio": cell.assignment_folio,
                "created_at": cell.created_at,
                "updated_at": cell.updated_at,
            } for cell in cells
        ]

        belongings = Belongings.objects.filter(cell_id=pk)
        formated_belongings = [
            {
                "cell_id": belonging.cell_id,
                "registration_datetime": belonging.registration_datetime,
                "document_mexican_passport": belonging.document_mexican_passport,
                "document_american_passport": belonging.document_american_passport,
                "document_residence": belonging.document_residence,
                "document_ine": belonging.document_ine,
                "document_other": belonging.document_other,
                "document_notes": belonging.document_notes,
                "jewelry_earrings": belonging.jewelry_earrings,
                "jewelry_ring": belonging.jewelry_ring,
                "jewelry_chain": belonging.jewelry_chain,
                "jewelry_bracelet": belonging.jewelry_bracelet,
                "jewelry_clock": belonging.jewelry_clock,
                "jewelry_other": belonging.jewelry_other,
                "jewelry_notes": belonging.jewelry_notes,
                "devices_keys": belonging.devices_keys,
                "devices_cables": belonging.devices_cables,
                "devices_laptop": belonging.devices_laptop,
                "devices_cellphone": belonging.devices_cellphone,
                "devices_aux": belonging.devices_aux,
                "devices_charger": belonging.devices_charger,
                "devices_tablet": belonging.devices_tablet,
                "devices_usb": belonging.devices_usb,
                "devices_computer_equipment": belonging.devices_computer_equipment,
                "devices_notes": belonging.devices_notes,
                "accesories_cap": belonging.accesories_cap,
                "accesories_ribbons": belonging.accesories_ribbons,
                "accesories_shoes": belonging.accesories_shoes,
                "accesories_backpack": belonging.accesories_backpack,
                "accesories_sunglasses": belonging.accesories_sunglasses,
                "accesories_cigarettes": belonging.accesories_cigarettes,
                "accesories_belt": belonging.accesories_belt,
                "accesories_handbag": belonging.accesories_handbag,
                "accesories_other": belonging.accesories_other,
                "accesories_notes": belonging.accesories_notes,
                "money_mexican_pesos": belonging.money_mexican_pesos,
                "money_american_dollars": belonging.money_american_dollars,
                "bank_cards": belonging.bank_cards,
                "is_active": belonging.is_active,
                "created_at": belonging.created_at,
                "updated_at": belonging.updated_at,
                "deliver_info": {
                    "delivered_to": belonging.delivered_to,
                    "delivered_to_another": belonging.delivered_to_another,
                    "delivery_notes": belonging.delivery_notes,
                    "delivery_datetime": belonging.delivery_datetime,
                    "delivery_relationship": belonging.delivery_relationship,
                } if belonging.delivered == True else {}
            } for belonging in belongings
        ]

        calls = CallsRegistry.objects.filter(cell_id=pk)
        formated_calls = [
            {
                "id": call.id,
                "cell_id": call.cell_id,
                "call_datetime": call.call_datetime,
                "had_response": call.had_response,
                "accepted":call.accepted,
                "user":call.user,
                "name": call.name,
                "phone_number": call.phone_number,
                "detainee_relationship": call.detainee_relationship,
                "is_active": call.is_active,
                "created_at": call.created_at,
                "updated_at": call.updated_at,
            } for call in calls
        ]
        response_data = {
            "cell_data": formated_cells[0] if len(formated_cells) > 0 else {},
            "belongings_data": formated_belongings[0] if len(formated_belongings) > 0 else {},
            "calls_data": formated_calls if len(formated_calls) > 0 else [],
        }

        return JsonResponse({"status": "success", "data": response_data}, safe=False)

class AdvancedSearchViewSet(viewsets.ModelViewSet):
    response = {
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        "results": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "record_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "name": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "fathers_name": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "entry_date": openapi.Schema(type=openapi.TYPE_STRING),
                    "qualification_release_date": openapi.Schema(type=openapi.TYPE_STRING),
                    "sanction": openapi.Schema(type=openapi.TYPE_STRING),
                    "process": openapi.Schema(type=openapi.TYPE_STRING),
                    "fault": openapi.Schema(type=openapi.TYPE_STRING),
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
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "sorted_column": openapi.Schema(type=openapi.TYPE_STRING),
        "order": openapi.Schema(type=openapi.TYPE_STRING),
        "search": openapi.Schema(type=openapi.TYPE_STRING),
        "advanced": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
                "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
                "nickname": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "entry_date": openapi.Schema(type=openapi.TYPE_STRING),
                "qualification_release_date": openapi.Schema(type=openapi.TYPE_STRING),
                "process": openapi.Schema(type=openapi.TYPE_STRING),
                "fault": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
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
        operation_summary="Advanced search in the folios",
        operation_description="This endpoint searches in the records.",
        tags=["Records"],
    )
    def search(self, request, *args, **kwargs):

        today = timezone.now()

        status = request.data.get('status')
        sorted_column = request.data.get('sorted_column')
        order = request.data.get('order')

        district = request.data.get('district_id')

        search = request.data.get('search')
        advancedSearch = request.data.get('advanced')

        items_per_page = request.GET.get('per_page', 10)
        page = request.GET.get('page', 1)

        # Inicializar results por defecto
        results = Records.objects.prefetch_related("detainee")

        if search != "" and search is not None:
            results = results.filter(Q(detainee__name__icontains=search) | Q(detainee__fathers_name__icontains=search)| Q(detainee__mothers_name__icontains=search)| Q(folio_afi__icontains=search))
            if district and int(district) > 0:
                results = results.filter(Q(district_id=district))
        else:
            form = RecordsAdvancedSearchForm(advancedSearch)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                fathers_name = form.cleaned_data.get('fathers_name')
                mothers_name = form.cleaned_data.get('mothers_name')
                nickname = form.cleaned_data.get('nickname')
                gender = form.cleaned_data.get('gender')
                record_entry_date = form.cleaned_data.get('entry_date')
                qualification_release_date = form.cleaned_data.get('qualification_release_date')
                record_process = form.cleaned_data.get('process')
                fault = form.cleaned_data.get('crime')
                records_fault_filterd = []
                if fault:
                    events = Events.objects.filter(Q(type__icontains=fault) | Q(subtype__icontains=fault)).values('record_id').distinct()
                    events = [
                    {
                        "id": event.get('record_id'),
                    }
                    for event in events
                    ]

                    for event in events:
                        records_fault_filterd.append(event.get('id'))

                # results_events = Events.objects.filter(Q(type__icontains=fault) | Q(subtype__icontains=fault)).values_list('record_id', flat=True)
                results = Records.objects.prefetch_related("detainee")

                if name:
                    results = results.filter(detainee__name__icontains=name)
                if fathers_name:
                    results = results.filter(detainee__fathers_name__icontains=fathers_name)
                if mothers_name:
                    results = results.filter(detainee__mothers_name__icontains=mothers_name)
                if nickname:
                    results = results.filter(detainee__nickname__icontains=nickname)
                if gender:
                    results = results.filter(detainee__gender__icontains=gender)
                if record_entry_date:
                    results = results.filter(Q(entry_date__date__icontains=record_entry_date))
                if qualification_release_date:
                    results = results.filter(Q(qualification_release_date__date__icontains=qualification_release_date))
                if record_process:
                    results = results.filter(Q(process__icontains=record_process))
                if fault:
                    results = results.filter(Q(id__in=records_fault_filterd))
                if district and int(district) > 0:
                    results = results.filter(Q(district_id=district))
        if status == 'active':
            # Activos: no liberados O con fecha de liberación futura O sin fecha
            results = results.filter(
                Q(has_been_released=False) |
                Q(qualification_release_date__gt=today) |
                Q(qualification_release_date__isnull=True)
            )
        if sorted_column != "":

            if sorted_column == 'record_id':
                sorted_column = 'id'
            if sorted_column == 'detainee_id':
                sorted_column = 'detainee__id'
            if sorted_column == 'record_folio':
                sorted_column = 'folio_afi'
            if sorted_column == 'detainee_name':
                sorted_column = 'detainee__name'
            if sorted_column == 'detainee_fathers_name':
                sorted_column = 'detainee__fathers_name'
            if sorted_column == 'detainee_mothers_name':
                sorted_column = 'detainee__mothers_name'
            if sorted_column == 'detainee_entry_date':
                sorted_column = 'entry_date'
            if sorted_column == 'detainee_sanction':
                sorted_column = 'sanction'
            if sorted_column == 'detainee_process':
                sorted_column = 'process'
            if sorted_column == 'detainee_release_date':
                sorted_column = 'qualification_release_date'

            if order == 'desc':
                results = results.order_by(f'-{sorted_column}')
            else:
                results = results.order_by(sorted_column)
        detainees = [
        {
            "record_id": result.id,
            "detainee_id": result.detainee.id,
            "folio_afi": result.folio_afi,
            "detainee_name": result.detainee.name,
            "detainee_fathers_name": result.detainee.fathers_name,
            "detainee_mothers_name": result.detainee.mothers_name,
            "detainee_entry_date": result.entry_date,
            "detainee_sanction": result.sanction,
            "detainee_process": result.process,
            "has_been_released": result.has_been_released,
            "detainee_qualification_release_date": result.qualification_release_date,
            "detainee_official_release_date": result.official_release_date,
        }
        for result in results
        ]

        for detainee in detainees:
            total_payables = Events.objects.filter(record_id=detainee.get('record_id')).values_list('total_payable')
            detainee['detainee_sanction'] = 0
            for total_payable in total_payables:
                if total_payable[0] is not None:
                    detainee['detainee_sanction'] += total_payable[0]
            events = Events.objects.filter(record_id=detainee.get('record_id')).values_list('type', 'subtype')
            detainee['detainee_processes'] = []
            for event in events:
                if event[0] is not None and event[1] is not None:
                    all_processes = " ".join(event)
                    detainee['detainee_processes'].append(all_processes)

        paginator = Paginator(detainees, items_per_page)

        items = paginator.page(page)

        data = {
            "results": items.object_list,
            "per_page": paginator.per_page,
            "page": int(page),
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        }

        return JsonResponse({"status": "success", "data": data})


class SingleOtherRecordsViewSet(viewsets.ModelViewSet):
    serializer_class = OtherRecordsSerializer
    queryset = OtherRecords.objects.filter(is_active=True)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs["pk"], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        responses={200: OtherRecordsSerializer(many=False)},
        operation_summary="Retrieve the information of a single other record with the id provided in URL",
        operation_description="Retrieve the information of a single other record with the id provided in URL",
        tags=["Records"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:            
            detainees_queryset = OtherRecordsDetainees.objects.filter(other_record=instance)
            detainees_serializer = OtherRecordsDetaineesSerializer(detainees_queryset, many=True)            
            serializer = self.get_serializer(instance)
            record_data=serializer.data
            record_data['other_record_detainees']= detainees_serializer.data
            response_data = {
                'status': 'success',
                'data': record_data
            }
            return Response(response_data)

        return Response(
            {"status": "fail", "message": "Record not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                "district": openapi.Schema(type=openapi.TYPE_STRING),
                "reason": openapi.Schema(type=openapi.TYPE_STRING),                
                "date": openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),                
                "place": openapi.Schema(type=openapi.TYPE_STRING),
                "holder_name": openapi.Schema(type=openapi.TYPE_STRING),
                "vehicle_type": openapi.Schema(type=openapi.TYPE_STRING),
                "brand": openapi.Schema(type=openapi.TYPE_STRING),
                "created_by": openapi.Schema(type=openapi.TYPE_STRING),
                "line": openapi.Schema(type=openapi.TYPE_STRING),
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
                "detention_type": openapi.Schema(type=openapi.TYPE_STRING),
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "subtype": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "quantity": openapi.Schema(type=openapi.TYPE_STRING),
                "general_condition": openapi.Schema(type=openapi.TYPE_STRING),
                "model": openapi.Schema(type=openapi.TYPE_STRING),
                "color": openapi.Schema(type=openapi.TYPE_STRING),
                "plates": openapi.Schema(type=openapi.TYPE_STRING),
                "serial_number": openapi.Schema(type=openapi.TYPE_STRING),
                "stamp_number": openapi.Schema(type=openapi.TYPE_STRING),
                "emission_number": openapi.Schema(type=openapi.TYPE_STRING),
                "association_expeditor": openapi.Schema(type=openapi.TYPE_STRING),
                "comments": openapi.Schema(type=openapi.TYPE_STRING),
                "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                "records": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),

            },            
        ),
        responses={
            200: OtherRecordsSerializer(many=False),
          
        },
        operation_summary="Updates other record.",
        operation_description="Updates the other record with the id provided in the URL",
        tags=["Records"],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:          
            received_data={
                'district': request.data.get('district', instance.district),
                'reason': request.data.get('reason', instance.reason),
                'date': request.data.get('date', instance.date),
                'place': request.data.get('place', instance.place),
                'holder_name': request.data.get('holder_name', instance.holder_name),
                'vehicle_type': request.data.get('vehicle_type', instance.vehicle_type),
                'brand': request.data.get('brand', instance.brand),
                'created_by': request.data.get('created_by', instance.created_by),
                'line': request.data.get('line', instance.line),
                'discriminator': request.data.get('discriminator', instance.discriminator),
                "detention_type": request.data.get('detention_type', instance.detention_type),
                'type': request.data.get('type', instance.type),
                'subtype': request.data.get('subtype', instance.subtype),
                'description': request.data.get('description', instance.description),
                'quantity': request.data.get('quantity', instance.quantity),
                'general_condition': request.data.get('general_condition', instance.general_condition),
                'model': request.data.get('model', instance.model),
                'color': request.data.get('color', instance.color),
                'plates': request.data.get('plates', instance.plates),
                'serial_number': request.data.get('serial_number', instance.serial_number),
                'stamp_number': request.data.get('stamp_number', instance.stamp_number),
                'emission_number': request.data.get('emission_number', instance.emission_number),
                'association_expeditor': request.data.get('association_expeditor', instance.association_expeditor),
                'comments': request.data.get('comments', instance.comments),
                'image_path': request.data.get('image_path', instance.image_path),
                'records': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),                
            }
            
            serializer = self.get_serializer(instance, data=received_data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            OtherRecordsDetainees.objects.filter(other_record=instance).delete()
            record_ids_array = request.data.get("records", [])

            with transaction.atomic():
                # Assuming there is a ForeignKey relationship between OtherRecordsDetainees and Records
                # Assuming there is a OneToOneField relationship between Records and Detainees
                records_detainees_data = Records.objects.filter(id__in=record_ids_array).values(
                    'id', 'folio_afi','entry_date', 'detainee__id', 'detainee__name', 'detainee__fathers_name', 'detainee__mothers_name'
                )

                detainee_ids = set(item['detainee__id'] for item in records_detainees_data)
                detainees = Detainee.objects.filter(id__in=detainee_ids).values('id', 'name', 'fathers_name', 'mothers_name')
                detainee_mapping = {detainee['id']: detainee for detainee in detainees}

                detainee_records = []

                for item in records_detainees_data:
                    detainee_instance_data = detainee_mapping.get(item['detainee__id'], {})
                    other_records_detainee = OtherRecordsDetainees(
                        other_record=instance,
                        relation_folio=serializer.data.get("other_record_folio"),
                        related_to_detention=item['folio_afi'],
                        detention_entry_date=item['entry_date'],
                        detainee_id=item['detainee__id'],
                        name=detainee_instance_data.get('name'),
                        fathers_name=detainee_instance_data.get('fathers_name'),
                        mothers_name=detainee_instance_data.get('mothers_name'),
                    )
                    detainee_records.append(other_records_detainee)

                OtherRecordsDetainees.objects.bulk_create(detainee_records)

            
            serialized_detainee_records = [
                {
                    'other_record': record.other_record.id,
                    'relation_folio': record.relation_folio,
                    'related_to_detention':record.related_to_detention,
                    'detention_entry_date': record.detention_entry_date,
                    'detainee_id': record.detainee_id,
                    'name': record.name,
                    'fathers_name': record.fathers_name,
                    'mothers_name': record.mothers_name,
                }
                for record in detainee_records
            ]

            response_data = {
                "id": serializer.data.get('id'),
                "district": serializer.data.get('district'),
                "other_record_folio":serializer.data.get('other_record_folio'),
                "reason": serializer.data.get('reason'),
                "date":serializer.data.get('date'),#hardcoded the username while the toked decode is ready
                "place" : serializer.data.get('place'),
                "holder_name":serializer.data.get('holder_name'),
                "vehicle_type":serializer.data.get('vehicle_type'),
                "brand":serializer.data.get('brand'),
                "created_by":serializer.data.get('created_by'),
                "line" : serializer.data.get('line'),
                "discriminator" :serializer.data.get('discriminator'),
                "detention_type" :serializer.data.get('detention_type'),
                "type" :serializer.data.get('type'),
                "subtype" :serializer.data.get('subtype'),
                "description" :serializer.data.get('description'),
                "quantity" : serializer.data.get('quantity'),
                "general_condition" : serializer.data.get('general_condition'),        
                "model":serializer.data.get('model'),
                "color":serializer.data.get('color'),
                "plates" : serializer.data.get('plates'),        
                "serial_number":serializer.data.get('serial_number'),
                "stamp_number" : serializer.data.get('stamp_number'),                                         
                "emission_number" : serializer.data.get('emission_number'),                                         
                "association_expeditor":serializer.data.get('association_expeditor'),                                            
                "comments":serializer.data.get('comments'),
                "image_path":serializer.data.get('image_path'),                
                "created_at": serializer.data.get('created_at'),
                "updated_at": serializer.data.get('created_at'),
                'other_record_detainees': serialized_detainee_records
                
            }

            # response_data = serializer.data
            # response_data['other_record_detainees']: serialized_detainee_records
            
            #response_data['other_record']['other_record_detainees']: serialized_detainee_records       
            return Response({'status':'success','data':response_data})

            

        else:
            # return Response({'status':'success','data':record_actions})
            return Response(
                {"status": "fail", "message": "Record not found"},
                status=status.HTTP_404_NOT_FOUND)


class OtherRecordsViewSet(viewsets.ModelViewSet):
    serializer_class = OtherRecordsSerializer
    queryset = OtherRecords.objects.filter(is_active=True)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs["pk"], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        responses={200: ActionsSerializer(many=True)},
        operation_summary="List all all the other records registered",
        operation_description="List all the other records on database",
        tags=["Records"],
    )
    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        other_records_ids = [item['id'] for item in serializer.data]

        # Fetch related OtherRecordDetainees using the IDs
        detainees_queryset = OtherRecordsDetainees.objects.filter(other_record__in=other_records_ids)
        detainees_serializer = OtherRecordsDetaineesSerializer(detainees_queryset, many=True)
        # Create a new data structure to hold combined information
        combined_data = []

        # Iterate over serializer.data and combine with detainees_serializer.data
        for record in serializer.data:
            record_id = record['id']

            # Filter detainees_serializer.data based on the current record_id
            related_detainees = [
                item for item in detainees_serializer.data if item['other_record'] == record_id
            ]
            # Combine information into a new object
      

            combined_item = {
                "id": record['id'],
                "district": record['district'],
                "other_record_folio":record['other_record_folio'],
                "reason": record['reason'],
                "date":record['date'],#hardcoded the username while the toked decode is ready
                "place" : record['place'],
                "holder_name":record['holder_name'],
                "vehicle_type":record['vehicle_type'],
                "brand":record['brand'],
                "created_by":record['created_by'],
                "line" : record['line'],
                "discriminator" :record['discriminator'],
                "detention_type" :record['detention_type'],
                "type" :record['type'],
                "subtype" :record['subtype'],
                "description" :record['description'],
                "quantity" : record['quantity'],
                "general_condition" : record['general_condition'],        
                "model":record['model'],
                "color":record['color'],
                "plates" : record['plates'],        
                "serial_number":record['serial_number'],
                "stamp_number" : record['stamp_number'],                                         
                "emission_number" : record['emission_number'],                                         
                "association_expeditor":record['association_expeditor'],                                            
                "comments":record['comments'],
                "image_path":record['image_path'],                
                "created_at": record['created_at'],
                "updated_at": record['updated_at'],
                'other_record_detainees': related_detainees
            }

            # Add the combined object to the result array
            combined_data.append(combined_item)

        # Include the combined information in the response
        response_data = {
            "status": "success",
            "data": combined_data
        }        

        return Response({"status": "success", "data": combined_data}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                "district": openapi.Schema(type=openapi.TYPE_STRING),
                "reason": openapi.Schema(type=openapi.TYPE_STRING),                
                "date": openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),                
                "place": openapi.Schema(type=openapi.TYPE_STRING),
                "holder_name": openapi.Schema(type=openapi.TYPE_STRING),
                "vehicle_type": openapi.Schema(type=openapi.TYPE_STRING),
                "brand": openapi.Schema(type=openapi.TYPE_STRING),
                "created_by": openapi.Schema(type=openapi.TYPE_STRING),
                "line": openapi.Schema(type=openapi.TYPE_STRING),
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "subtype": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "detention_type": openapi.Schema(type=openapi.TYPE_STRING),
                "quantity": openapi.Schema(type=openapi.TYPE_STRING),
                "general_condition": openapi.Schema(type=openapi.TYPE_STRING),
                "model": openapi.Schema(type=openapi.TYPE_STRING),
                "color": openapi.Schema(type=openapi.TYPE_STRING),
                "plates": openapi.Schema(type=openapi.TYPE_STRING),
                "serial_number": openapi.Schema(type=openapi.TYPE_STRING),
                "stamp_number": openapi.Schema(type=openapi.TYPE_STRING),
                "emission_number": openapi.Schema(type=openapi.TYPE_STRING),
                "association_expeditor": openapi.Schema(type=openapi.TYPE_STRING),
                "comments": openapi.Schema(type=openapi.TYPE_STRING),
                "image_path": openapi.Schema(type=openapi.TYPE_STRING),
                'records': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
            },            
        ),
        responses={
            200: OtherRecordsSerializer(many=False),
          
        },
        operation_summary="Adds a new other record.",
        operation_description="Adds a new other record that can be related to the detainee provided in body",
        tags=["Records"],
    )
    def add(self, request, *args, **kwargs):
        
        
        # serializer = self.get_serializer(instance)
        # parent_record_id = record_id = serializer.data.get("id")                                   
        #full_url= siprob_prints_url + request.data.get("discriminator")
        # Make the POST request
        #logged_user = request.user
        #logged_user = User.objects.get(pk=1)
        # user_fullname = logged_user.name
        # if logged_user.fathers_name is not None:
        #     user_fullname = user_fullname +" "+logged_user.fathers_name
        # if logged_user.mothers_name is not None:
        #     user_fullname = user_fullname +" "+logged_user.mothers_name
        # data_to_send['user']=user_fullname         
        server_time = datetime.now()
        offset_hours = int(request.headers.get('offset-time', -6))
        client_time = server_time + timedelta(hours=offset_hours)
        formatted_client_time = client_time.strftime('%Y-%m-%dT%H:%M:%S') 
        other_record_folio = 'OTR-'+request.data.get("district")[:3]+'-'+formatted_client_time
        other_record_data = {
            "district": request.data.get("district"),
            "other_record_folio":other_record_folio,
            "reason": request.data.get("reason"),             
            "date":request.data.get('date'),#hardcoded the username while the toked decode is ready
            "place" : request.data.get("place"),                
            "holder_name":request.data.get("holder_name"),            
            "detention_type":request.data.get("detention_type"),            
            "vehicle_type":request.data.get("vehicle_type"),
            "brand":request.data.get("brand"),            
            "created_by":request.data.get("created_by"),
            "line" : request.data.get("line"),
            "discriminator" :request.data.get("discriminator"),
            "type" :request.data.get("type"),
            "subtype" :request.data.get("subtype"),
            "description" :request.data.get("description"),
            "quantity" : request.data.get("quantity"),
            "general_condition" : request.data.get("general_condition"),                        
            "model":request.data.get("model"),
            "color":request.data.get("color"),                
            "plates" : request.data.get("plates"),                        
            "serial_number":request.data.get("serial_number"),
            "stamp_number" : request.data.get("stamp_number"),                                                         
            "emission_number" : request.data.get("emission_number"),                                                         
            "association_expeditor":request.data.get("association_expeditor"),                                                            
            "comments":request.data.get("comments"),
            "image_path":request.data.get("image_path"),
        }
        new_other_record = OtherRecords.objects.create(**other_record_data)
        # Serialize the created Action object

        record_ids_array = request.data.get("records", [])

        with transaction.atomic():
            # Assuming there is a ForeignKey relationship between OtherRecordsDetainees and Records
            # Assuming there is a OneToOneField relationship between Records and Detainees
            records_detainees_data = Records.objects.filter(id__in=record_ids_array).values(
                'id', 'folio_afi','entry_date', 'detainee__id', 'detainee__name', 'detainee__fathers_name', 'detainee__mothers_name'
            )

            detainee_ids = set(item['detainee__id'] for item in records_detainees_data)
            detainees = Detainee.objects.filter(id__in=detainee_ids).values('id', 'name', 'fathers_name', 'mothers_name')
            detainee_mapping = {detainee['id']: detainee for detainee in detainees}

            detainee_records = []

            for item in records_detainees_data:
                detainee_instance_data = detainee_mapping.get(item['detainee__id'], {})
                print("Item: ",item)
                other_records_detainee = OtherRecordsDetainees(
                    other_record=new_other_record,
                    relation_folio=other_record_folio,
                    related_to_detention=item['folio_afi'],
                    detention_entry_date=item['entry_date'],
                    detainee_id=item['detainee__id'],
                    name=detainee_instance_data.get('name'),
                    fathers_name=detainee_instance_data.get('fathers_name'),
                    mothers_name=detainee_instance_data.get('mothers_name'),
                )
                detainee_records.append(other_records_detainee)

            OtherRecordsDetainees.objects.bulk_create(detainee_records)


        
        other_record_serializer = OtherRecordsSerializer(new_other_record)
        new_other_record_data = other_record_serializer.data
        serialized_detainee_records = [
            {
                'other_record': record.other_record.id,
                'relation_folio': record.relation_folio,
                'related_to_detention':record.related_to_detention,
                'detention_entry_date': record.detention_entry_date,
                'detainee_id': record.detainee_id,
                'name': record.name,
                'fathers_name': record.fathers_name,
                'mothers_name': record.mothers_name,
            }
            for record in detainee_records
        ]

        response_data = {
                "id": new_other_record_data['id'],
                "district": new_other_record_data['district'],
                "other_record_folio":new_other_record_data['other_record_folio'],
                "reason": new_other_record_data['reason'],
                "date":new_other_record_data['date'],#hardcoded the username while the toked decode is ready
                "place" : new_other_record_data['place'],
                "holder_name":new_other_record_data['holder_name'],
                "vehicle_type":new_other_record_data['vehicle_type'],
                "brand":new_other_record_data['brand'],
                "created_by":new_other_record_data['created_by'],
                "line" : new_other_record_data['line'],
                "discriminator" :new_other_record_data['discriminator'],
                "detention_type" :new_other_record_data['detention_type'],
                "type" :new_other_record_data['type'],
                "subtype" :new_other_record_data['subtype'],
                "description" :new_other_record_data['description'],
                "quantity" : new_other_record_data['quantity'],
                "general_condition" : new_other_record_data['general_condition'],        
                "model":new_other_record_data['model'],
                "color":new_other_record_data['color'],
                "plates" : new_other_record_data['plates'],        
                "serial_number":new_other_record_data['serial_number'],
                "stamp_number" : new_other_record_data['stamp_number'],                                         
                "emission_number" : new_other_record_data['emission_number'],                                         
                "association_expeditor":new_other_record_data['association_expeditor'],                                            
                "comments":new_other_record_data['comments'],
                "image_path":new_other_record_data['image_path'],                
                "created_at": new_other_record_data['created_at'],
                "updated_at": new_other_record_data['created_at'],
                'other_record_detainees': serialized_detainee_records
                
        }        

        # response_data = new_other_record_data           
        # response_data['other_record_detainees']: serialized_detainee_records
        
        return Response(
            {"status": "success", "data": response_data},
            status=status.HTTP_200_OK)                 

class SearchOtherRecordsViewSet(viewsets.ModelViewSet):
    response = {
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        "results": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "other_record_id": openapi.Schema(type=openapi.TYPE_STRING),
                    "other_record_folio": openapi.Schema(type=openapi.TYPE_STRING),
                    "date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    "discriminator": openapi.Schema(type=openapi.TYPE_STRING),
                    "related_detainee": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    "reason": openapi.Schema(type=openapi.TYPE_STRING),
                    "created_by": openapi.Schema(type=openapi.TYPE_STRING),
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
        "status": openapi.Schema(type=openapi.TYPE_STRING),
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
        operation_summary="Search in other records",
        operation_description="This endpoint searches in the other records.",
        tags=["Records"],
    )
    def search(self, request, *args, **kwargs):
        sorted_column = request.data.get('sorted_column')
        order = request.data.get('order')
        filter_by = request.data.get('filter_by')

        search = request.data.get('search')
        district = request.data.get('district_id')

        items_per_page = request.GET.get('per_page', 10)
        page = request.GET.get('page', 1)

        if search != "":
            results = OtherRecords.objects.prefetch_related()
            results_detainees = OtherRecordsDetainees.objects.filter(Q(name__icontains=search) | Q(fathers_name__icontains=search) | Q(mothers_name__icontains=search)).values_list('other_record_id', flat=True)
            results = results.filter(Q(other_record_folio__icontains=search) | Q(id__in=results_detainees))
        else:
            results = OtherRecords.objects.prefetch_related()
        if district != None:
            print(district)
            results = results.filter(district=district)
        if sorted_column != "":
            if sorted_column == 'other_record_folio':
                sorted_column = 'other_record_folio'
            if sorted_column == 'date':
                sorted_column = 'date'
            if sorted_column == 'discriminator':
                sorted_column = 'discriminator'
            if sorted_column == 'reason':
                sorted_column = 'reason'
            if sorted_column == 'created_by':
                sorted_column = 'created_by'

            if order == 'desc' and sorted_column != 'related_detainees':
                results = results.order_by(f'-{sorted_column}')
            else:
                if order == 'asc' and sorted_column != 'related_detainees':
                    results = results.order_by(sorted_column)
        if filter_by != "":
            if filter_by == "objects":
                results = results.filter(discriminator='objects')
            if filter_by == "vehicles":
                results = results.filter(discriminator='vehicles')
        other_records = [
        {
            "other_record_id": result.id,
            "other_record_folio": result.other_record_folio,
            "date": result.date,
            "discriminator": result.discriminator,
            "reason": result.reason,
            "created_by": result.created_by
        }
        for result in results
        ]
        for other_record in other_records:
            other_records_detainees = OtherRecordsDetainees.objects.filter(other_record_id=other_record.get('other_record_id')).values_list('name', 'fathers_name', 'mothers_name')
            other_record['related_detainees'] = []
            for other_records_detainee in other_records_detainees:
                full_name = " ".join(other_records_detainee)
                other_record['related_detainees'].append(full_name)
        if sorted_column == 'related_detainees':
            if order == 'desc':
                other_records.sort(key=lambda x: x.get('related_detainees'), reverse=False)
            else:
                other_records.sort(key=lambda x: x.get('related_detainees'), reverse=True)

        paginator = Paginator(other_records, items_per_page)
        items = paginator.page(page)

        data = {
            "results": items.object_list,
            "per_page": paginator.per_page,
            "page": int(page),
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        }

        return JsonResponse({"status": "success", "data": data})

class ActionsViewSet(viewsets.ModelViewSet):
    serializer_class = RecordsSerializer
    queryset = Records.objects.filter(is_active=True)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs["pk"], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        responses={200: ActionsSerializer(many=True)},
        operation_summary="List all the actions related to a record",
        operation_description="List all the actions related the record with the id provided in URL",
        tags=["Records"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            parent_record_id = record_id = serializer.data.get("id")
            related_actions = Actions.objects.filter(record=parent_record_id)
            actions_serializer = ActionsSerializer(related_actions, many=True)
            actions_data = actions_serializer.data
            return JsonResponse({"status": "success", "data": actions_data}, safe=False)
            # return Response({'status':'success','data':record_actions})
        return Response(
            {"status": "fail", "message": "Record not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                #"user" : openapi.Schema(type=openapi.TYPE_STRING),
                "discriminator" : openapi.Schema(type=openapi.TYPE_STRING, enum=["hospitalgeneral", "salidaprovisional", "solicitudaudiencia","constanciaconsular","entregafamiliares","desistimiento","salidadefinitiva","trabajosocial","citatorioaudienciacerecito","solicitudaudienciacerecito","pertenencias","entregaadolescente","entregadehechos","entregadeimputado","llamadas","pertenencias","salidasindelito","salidacondelito","custodiahospital","formatolibre"]),
                "office_number":openapi.Schema(type=openapi.TYPE_STRING),
                "user":openapi.Schema(type=openapi.TYPE_STRING),
                "detainee":openapi.Schema(type=openapi.TYPE_STRING),
                "age" : openapi.Schema(type=openapi.TYPE_STRING),
                "nationality" :openapi.Schema(type=openapi.TYPE_STRING),
                "address" :openapi.Schema(type=openapi.TYPE_STRING),
                "relative" :openapi.Schema(type=openapi.TYPE_STRING),
                "relative_age" :openapi.Schema(type=openapi.TYPE_STRING),
                "identification" : openapi.Schema(type=openapi.TYPE_STRING),
                "id_number" : openapi.Schema(type=openapi.TYPE_STRING),
                "affinity":openapi.Schema(type=openapi.TYPE_STRING),
                "medical_certificate":openapi.Schema(type=openapi.TYPE_STRING),
                "description":openapi.Schema(type=openapi.TYPE_STRING),
                "district_name":openapi.Schema(type=openapi.TYPE_STRING),
                "date":openapi.Schema(type=openapi.TYPE_STRING,  format="date"),
                "hour":openapi.Schema(type=openapi.TYPE_STRING),
                "article":openapi.Schema(type=openapi.TYPE_STRING),
                "fraction":openapi.Schema(type=openapi.TYPE_STRING),
                "number":openapi.Schema(type=openapi.TYPE_STRING),
                "infraction_number":openapi.Schema(type=openapi.TYPE_STRING),
                "unit":openapi.Schema(type=openapi.TYPE_STRING),
                "agent1":openapi.Schema(type=openapi.TYPE_STRING),
                "agent2":openapi.Schema(type=openapi.TYPE_STRING),
                "action_date":openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                "medic_name":openapi.Schema(type=openapi.TYPE_STRING),
                "medical_cedula":openapi.Schema(type=openapi.TYPE_STRING),
                "medical_date_time":openapi.Schema(type=openapi.TYPE_STRING,format=openapi.FORMAT_DATETIME),
                "devices_laptop": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "devices_charger": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "accesories_cap": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "money_mexican_pesos": openapi.Schema(type=openapi.TYPE_STRING),
                "money_american_dollars": openapi.Schema(type=openapi.TYPE_STRING),
                "remission": openapi.Schema(type=openapi.TYPE_STRING),
                "subject": openapi.Schema(type=openapi.TYPE_STRING),
                "written_to": openapi.Schema(type=openapi.TYPE_STRING),
                "crime" :openapi.Schema(type=openapi.TYPE_STRING),
                "victim" :openapi.Schema(type=openapi.TYPE_STRING),
                "other" :openapi.Schema(type=openapi.TYPE_STRING),
                "agent_name" :openapi.Schema(type=openapi.TYPE_STRING),
                "agent_job" :openapi.Schema(type=openapi.TYPE_STRING),
                "agent_number" :openapi.Schema(type=openapi.TYPE_STRING),
                "agent_unit" :openapi.Schema(type=openapi.TYPE_STRING),
                "has_ministerio_publico" : openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "has_iph" : openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "has_chain_custody" : openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "has_medical_certificate" : openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "has_car_inventory" : openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),

            },
            required=['discriminator']
        ),
        responses={
            # 200: ActionsSerializer(many=False),
            201: openapi.Response(
                "PDF document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
        },
        operation_summary="Adds and print a new action to a record.",
        operation_description="Creates a PDF document for the record with the id provided and stores the information on database",
        tags=["Records"],
    )
    def add(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            parent_record_id = record_id = serializer.data.get("id")
            valid_discriminators = ["hospitalgeneral", "salidaprovisional", "solicitudaudiencia","constanciaconsular","entregafamiliares","desistimiento","salidadefinitiva","trabajosocial","citatorioaudienciacerecito","solicitudaudienciacerecito","pertenencias","entregaadolescente","entregadehechos","entregadeimputado","llamadas","pertenencias","salidasindelito","salidacondelito","custodiahospital","formatolibre"]
            if request.data.get('discriminator') is None or request.data.get('discriminator') not in valid_discriminators:
                return Response({"status": "fail", "message": "The type of the action is empty or invalid"}, status=status.HTTP_404_NOT_FOUND)

            #full_url= siprob_prints_url + request.data.get("discriminator")
            # Make the POST request
            #logged_user = request.user
            #logged_user = User.objects.get(pk=1)
            # user_fullname = logged_user.name
            # if logged_user.fathers_name is not None:
            #     user_fullname = user_fullname +" "+logged_user.fathers_name
            # if logged_user.mothers_name is not None:
            #     user_fullname = user_fullname +" "+logged_user.mothers_name
            # data_to_send['user']=user_fullname
            server_time = datetime.now()
            offset_hours = int(request.headers.get('offset-time', -6))
            client_time = server_time + timedelta(hours=offset_hours)
            formatted_client_time = client_time.strftime('%Y-%m-%dT%H:%M:%S')
            action_folio = 'ACT-'+request.data.get("district_name")[:3]+'-'+str(parent_record_id)+'-'+formatted_client_time


            action_data = {
                "record": instance,  # Assuming the relationship between Action and Record is called 'record'
                "action_date": request.data.get("date"),
                "user":request.data.get('user'),#hardcoded the username while the toked decode is ready
                "discriminator" : request.data.get("discriminator"),
                "office_number":request.data.get("office_number"),
                "action_folio":action_folio,
                "detainee":request.data.get("detainee"),
                "age" : request.data.get("age"),
                "nationality" :request.data.get("nationality"),
                "address" :request.data.get("address"),
                "relative" :request.data.get("relative"),
                "relative_age" :request.data.get("relative_age"),
                "identification" : request.data.get("identification"),
                "id_number" : request.data.get("id_number"),
                "affinity":request.data.get("affinity"),
                "medical_certificate":request.data.get("medical_certificate"),
                "description":request.data.get("description"),
                "district_name":request.data.get("district_name"),
                "date":request.data.get("date"),
                "hour":request.data.get("hour"),
                "article":request.data.get("article"),
                "fraction":request.data.get("fraction"),
                "number":request.data.get("number"),
                "infraction_number":request.data.get("infraction_number"),
                "unit":request.data.get("unit"),
                "agent1":request.data.get("agent1"),
                "agent2":request.data.get("agent2"),
                "medic_name":request.data.get("medic_name"),
                "medical_cedula":request.data.get("medical_cedula"),
                "medical_date_time":request.data.get("medical_date_time"),
                "devices_laptop": request.data.get("devices_laptop"),
                "devices_charger": request.data.get("devices_charger"),
                "accesories_cap": request.data.get("accesories_cap"),
                "money_mexican_pesos": request.data.get("money_mexican_pesos"),
                "money_american_dollars": request.data.get("money_mexican_pesos"),
                "remission": request.data.get("remission"),
                "subject": request.data.get("subject"),
                "written_to": request.data.get("written_to"),
                "crime" :request.data.get("crime"),
                "victim" :request.data.get("victim"),
                "other" :request.data.get("other"),
                "agent_name" : request.data.get("agent_name"),
                "agent_job" :request.data.get("agent_job"),
                "agent_number" :request.data.get("agent_number"),
                "agent_unit" :request.data.get("agent_unit"),
                "has_ministerio_publico" : request.data.get("has_ministerio_publico"),
                "has_iph" : request.data.get("has_iph"),
                "has_chain_custody" : request.data.get("has_chain_custody"),
                "has_medical_certificate" : request.data.get("has_medical_certificate"),
                "has_car_inventory" : request.data.get("has_car_inventory")
            }

            new_action = Actions.objects.create(**action_data)
            # Serialize the created Action object
            action_serializer = ActionsSerializer(new_action)
            serialized_action_data = action_serializer.data
            return Response(
                {"status": "success", "data": action_serializer.data},
                status=status.HTTP_200_OK)


        else:
            # return Response({'status':'success','data':record_actions})
            return Response(
                {"status": "fail", "message": "Record not found"},
                status=status.HTTP_404_NOT_FOUND)

class ActionsPrintViewSet(viewsets.ModelViewSet):
    serializer_class = RecordsSerializer
    queryset = Records.objects.filter(is_active=True)
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs["pk"], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the action",
            ),
        ],
        responses={
            # 200: ActionsSerializer(many=False),
            201: openapi.Response(
                "PDF document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
        },
        operation_summary="Retrieves PDF file of an action",
        operation_description="This endpoint retrieves a PDF file with the information of the action with the id provided",
        tags=["Records"],
        security=[{"Bearer Token": []}],  # Add this line for Authorization header
    )



    def print_action(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        #token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        # decoded_token = decode_token(token)
        # print(token)
        # user_info={}

        # if decoded_token:
        #     user_info = {'user_id': decoded_token['user_id'], 'username': decoded_token['username']}
        #     return Response(user_info)
        # else:
        #     return Response({'detail': 'Invalid or expired token'}, status=401)

        #print(user_info)

        action_info = Actions.objects.get(id=pk)
        if action_info is None :
            return JsonResponse({"status": "error", "message": "action_record_not_found"}, safe=False)

        action_info_dict = model_to_dict(action_info)
        locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        original_timezone = pytz.timezone('America/Denver')
        siprob_prints_url = default_prints_url
        if os.getenv("ENVIRONMENT")=='LOCAL':
            siprob_prints_url = "http://localhost:8023/"

        full_url= siprob_prints_url + action_info_dict.get('discriminator')
        action_info_dict['action_date'] = action_info_dict['action_date'].isoformat()
        action_info_dict['folio'] = action_info_dict['action_folio']

        action_date_object = datetime.strptime(action_info_dict['date'], '%Y-%m-%d')
        # Format the datetime object as desired
        formatted_date = action_date_object.strftime('%d de %B de %Y')
        action_info_dict['date'] = formatted_date
        action_info_dict['hour'] = action_info_dict['hour'][:-3]
        action_info_dict['has_ministerio_publico'] = "Si" if action_info_dict['has_ministerio_publico'] else "No",
        action_info_dict['has_iph'] = "Si" if action_info_dict['has_iph'] else "No",
        action_info_dict['has_chain_custody'] = "Si" if action_info_dict['has_chain_custody'] else "No",
        action_info_dict['has_medical_certificate'] = "Si" if action_info_dict['has_medical_certificate'] else "No",
        action_info_dict['has_car_inventory'] = "Si" if action_info_dict['has_car_inventory'] else "No",
        action_info_dict['devices_laptop'] = "Si" if action_info_dict['devices_laptop'] else "No",
        action_info_dict['devices_charger'] = "Si" if action_info_dict['devices_charger'] else "No",
        action_info_dict['accesories_cap'] = "Si" if action_info_dict['accesories_cap'] else "No",


        #action_info_dict['medical_date_time'] = action_info_dict['medical_date_time'].isoformat()


        response = requests.post(full_url, json=action_info_dict, timeout=30)
        if response.status_code == 200:
                response_data = response.json()
                pdf_path = siprob_prints_url+response_data.get("path")
                pdf_response = requests.get(pdf_path, timeout=30)
                if pdf_response.status_code == 200:
                    # Successfully fetched the PDF content
                    # Create a FileResponse with the fetched PDF content
                    try:
                        pdf_response = requests.get(pdf_path, timeout=10)
                        pdf_response.raise_for_status()
                    except requests.RequestException as e:
                        return Response({"status": "error", "message": f"Error fetching PDF content: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Create a FileResponse with the fetched PDF content
                    filename = action_info_dict.get('discriminator') + '_' + action_info_dict.get('detainee')+'_'+action_info_dict.get('folio')+'.pdf'
                    pdf_content = pdf_response.content
                    pdf_file_response = HttpResponse(pdf_content, content_type='application/pdf')
                    pdf_file_response['Content-Disposition'] = f'inline; filename="{filename}"'

                    # Return the FileResponse
                    return pdf_file_response
                else:
                    # Handle the error in fetching the PDF content
                    return Response({"status": "error", "message": "Error fetching PDF content"},
                                    status=pdf_response.status_code)
        else:
            # Handle the error in the external API response
            print(response.text)  # Print the error response
            return Response({"status": "error", "message": response.text},
                                status=response.status_code)

        # response = {
        #     'medic_data': formated_medic_information[0],

        # }

        return JsonResponse({"status": "success", "data": 'response'}, safe=False)

    def retrieve(self, request, *args, **kwargs):
        # Call the parent perform_create to save the instance
        #instance = serializer.save()
        instance = self.get_object()
        if instance:

            serializer = self.get_serializer(instance)
            parent_record_id = record_id = serializer.data.get("id")
            data_to_send = request.data
            #siprob_prints_url = os.getenv("PRINTS_URL")
            siprob_prints_url = default_prints_url
            if os.getenv("ENVIRONMENT")=='LOCAL':
                siprob_prints_url = "http://localhost:8023/"
            valid_discriminators = ['hospitalgeneral', 'salidaprovisional', 'solicitudaudiencia','constanciaconsular','citatorioaudiencia','entregafamiliares','desistimiento','salidadefinitiva','trabajosocial','citatorioaudienciacerecito','solicitudaudienciacerecito','formatolibre']
            if request.data.get('discriminator') is None or request.data.get('discriminator') not in valid_discriminators:
                return Response({"status": "fail", "message": "The type of the action is empty or invalid"}, status=status.HTTP_404_NOT_FOUND)

            full_url= siprob_prints_url + request.data.get("discriminator")
            # Make the POST request
            logged_user = request.user
            user_fullname = logged_user.name
            if logged_user.fathers_name is not None:
                user_fullname = user_fullname +" "+logged_user.fathers_name
            if logged_user.mothers_name is not None:
                user_fullname = user_fullname +" "+logged_user.mothers_name
            data_to_send['user']=user_fullname

            record_detainee = serializer.data.get("detainee")
            related_detainee = Detainee.objects.filter(id=record_detainee).first()  # Use first() to get a single object
            detainee_serializer = DetaineesSerializer(related_detainee) if related_detainee else None

            if detainee_serializer:
                detainee_data = detainee_serializer.data
                detainee_fullname = detainee_data.get("name", "")

                fathers_name = detainee_data.get("fathers_name")
                mothers_name = detainee_data.get("mothers_name")

                if fathers_name is not None:
                    detainee_fullname += " " + fathers_name
                if mothers_name is not None:
                    detainee_fullname += " " + mothers_name
                data_to_send['detainee'] = detainee_fullname
            else:
                data_to_send['detainee'] = None

            record_district = serializer.data.get("district")
            related_district = District.objects.filter(id=record_district).first()  # Use first() to get a single object
            district_serializer = DistrictsSerializer(related_district) if related_district else None

            if district_serializer:
                district_data = district_serializer.data
                district_name = district_data.get("name")

                if district_name is not None:
                    data_to_send['district'] = district_name
            else:
                data_to_send['district'] = None

            response = requests.post(full_url, json=data_to_send, timeout=30)
            if response.status_code == 200:
                # Successfully sent the data
                response_data = response.json()

                # Retrieve the PDF path from the response
                pdf_path = siprob_prints_url+response_data.get("path")
                # Fetch the PDF content
                pdf_response = requests.get(pdf_path, timeout=30)
                if pdf_response.status_code == 200:
                    # Successfully fetched the PDF content
                    # Create a FileResponse with the fetched PDF content
                    try:
                        pdf_response = requests.get(pdf_path, timeout=10)
                        pdf_response.raise_for_status()
                    except requests.RequestException as e:
                        return Response({"status": "error", "message": f"Error fetching PDF content: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Create a FileResponse with the fetched PDF content
                    filename = request.data.get('discriminator') + '_' + request.data.get('detainee')+'.pdf'
                    pdf_content = pdf_response.content
                    pdf_file_response = HttpResponse(pdf_content, content_type='application/pdf')
                    pdf_file_response['Content-Disposition'] = f'inline; filename="{filename}"'

                    # Return the FileResponse
                    return pdf_file_response
                else:
                    # Handle the error in fetching the PDF content
                    return Response({"status": "error", "message": "Error fetching PDF content"},
                                    status=pdf_response.status_code)
            else:
                # Handle the error in the external API response
                print(response.text)  # Print the error response
                return Response({"status": "error", "message": response.text},
                                status=response.status_code)
            # return Response({'status':'success','data':record_actions})
        return Response(
            {"status": "fail", "message": "Record not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


class PrintRecordViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Records.objects.all()
    serializer_class = RecordsSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the medical record",
            ),
        ],
        responses={
            # 200: ActionsSerializer(many=False),
            201: openapi.Response(
                "PDF document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
        },
        operation_summary="Retrieves a medical certificate PDF file",
        operation_description="This endpoint retrieves a medical certificate with the information of the medical history with the id provided",
        tags=["Records"],
        security=[{"Bearer Token": []}],  # Add this line for Authorization header
    )
    def print_medic_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        #token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        # decoded_token = decode_token(token)
        # print(token)
        # user_info={}

        # if decoded_token:
        #     user_info = {'user_id': decoded_token['user_id'], 'username': decoded_token['username']}
        #     return Response(user_info)
        # else:
        #     return Response({'detail': 'Invalid or expired token'}, status=401)

        #print(user_info)

        medic_info = MedicalInformation.objects.filter(id=pk).prefetch_related("user").prefetch_related("record")
        if len(medic_info) == 0:
            return JsonResponse({"status": "error", "message": "medical_record_not_found"}, safe=False)

        locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        original_timezone = pytz.timezone('America/Denver')
        formated_medic_information = [
            {
                "id": medic.id,
                "folio":medic.folio,
                "age":medic.record.detainee.age,
                "gender":medic.record.detainee.gender,
                "diagnostic": medic.diagnostic,
                "medical_t": medic.medical_t,
                "medical_fc": medic.medical_fc,
                "medical_fr": medic.medical_fr,
                "medical_ta": medic.medical_ta,
                "medical_sat": medic.saturation,
                "record":medic.record.id,
                "district":medic.record.district.name,
                "detainee":f"{medic.record.detainee.name} {medic.record.detainee.fathers_name} {medic.record.detainee.mothers_name}".replace("None", "") if medic.record else "",
                "user": medic.medic_name,
                "medical_cedula":medic.medical_cedula,
                #"medical_date_time": medic.medical_date_time.strftime("%Y-%m-%d %H:%M:%S") if medic.medical_date_time else None,
                "date": medic.medical_date_time.astimezone(original_timezone).strftime("%d de %B del %Y").lstrip("0").upper() if medic.medical_date_time else None,
                "hour": medic.medical_date_time.astimezone(original_timezone).strftime("%H:%M") if medic.medical_date_time else None,

            }
            for medic in medic_info
        ]

        #data_to_send=formated_medic_information[0]

        #siprob_prints_url = os.getenv("PRINTS_URL")
        siprob_prints_url = default_prints_url
        if os.getenv("ENVIRONMENT")=='LOCAL':
            siprob_prints_url = "http://localhost:8023/"
        full_url= siprob_prints_url + "certificadomedico"

        response = requests.post(full_url, json=formated_medic_information[0], timeout=30)
        if response.status_code == 200:
                # Successfully sent the data
                response_data = response.json()
                # Retrieve the PDF path from the response
                pdf_path = siprob_prints_url+response_data.get("path")
                # Fetch the PDF content
                pdf_response = requests.get(pdf_path, timeout=30)
                if pdf_response.status_code == 200:
                    # Successfully fetched the PDF content
                    # Create a FileResponse with the fetched PDF content
                    try:
                        pdf_response = requests.get(pdf_path, timeout=10)
                        pdf_response.raise_for_status()
                    except requests.RequestException as e:
                        return Response({"status": "error", "message": f"Error fetching PDF content: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Create a FileResponse with the fetched PDF content
                    filename = 'certificado_medico' + '_' + formated_medic_information[0].get('detainee')+'.pdf'
                    pdf_content = pdf_response.content
                    pdf_file_response = HttpResponse(pdf_content, content_type='application/pdf')
                    pdf_file_response['Content-Disposition'] = f'inline; filename="{filename}"'

                    # Return the FileResponse
                    return pdf_file_response
                else:
                    # Handle the error in fetching the PDF content
                    return Response({"status": "error", "message": "Error fetching PDF content"},
                                    status=pdf_response.status_code)
        else:
            # Handle the error in the external API response
            print(response.text)  # Print the error response
            return Response({"status": "error", "message": response.text},
                                status=response.status_code)

        # response = {
        #     'medic_data': formated_medic_information[0],

        # }

        return JsonResponse({"status": "success", "data": 'response'}, safe=False)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the call record",
            ),
        ],
        responses={
            # 200: ActionsSerializer(many=False),
            201: openapi.Response(
                "PDF document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
        },
        operation_summary="Retrieves a call registry PDF file",
        operation_description="This endpoint retrieves a PDF file with the information of the call with the id provided",
        tags=["Records"],
        security=[{"Bearer Token": []}],  # Add this line for Authorization header
    )
    def print_call_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        #token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        # decoded_token = decode_token(token)
        # print(token)
        # user_info={}

        # if decoded_token:
        #     user_info = {'user_id': decoded_token['user_id'], 'username': decoded_token['username']}
        #     return Response(user_info)
        # else:
        #     return Response({'detail': 'Invalid or expired token'}, status=401)

        #print(user_info)

        call_info = CallsRegistry.objects.filter(id=pk).prefetch_related("cell__record")

        if len(call_info) == 0:
            return JsonResponse({"status": "error", "message": "call_record_not_found"}, safe=False)

        locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        original_timezone = pytz.timezone('America/Denver')
        formated_call_information = [
            {
                "id": call.id,
                "folio":call.cell.record.folio_afi,
                "detainee":f"{call.cell.record.detainee.name} {call.cell.record.detainee.fathers_name} {call.cell.record.detainee.mothers_name}".replace("None", "") if call.cell.record else "",
                "user":call.user,
                "datetime":format_datetime(call.call_datetime),
                "answered":"Si" if call.had_response else "No",
                "accepted":"Si" if call.accepted else "No",
                "phone":call.phone_number,
                "called_to": call.name,
                "relativeness":call.detainee_relationship

            }
            for call in call_info
        ]

        #data_to_send=formated_medic_information[0]
        #siprob_prints_url = os.getenv("PRINTS_URL")
        siprob_prints_url = default_prints_url
        if os.getenv("ENVIRONMENT")=='LOCAL':
            siprob_prints_url = "http://localhost:8023/"
        full_url= siprob_prints_url + "llamadas"

        response = requests.post(full_url, json=formated_call_information[0], timeout=30)
        if response.status_code == 200:
                # Successfully sent the data
                response_data = response.json()
                # Retrieve the PDF path from the response
                pdf_path = siprob_prints_url+response_data.get("path")
                # Fetch the PDF content
                pdf_response = requests.get(pdf_path, timeout=30)
                if pdf_response.status_code == 200:
                    # Successfully fetched the PDF content
                    # Create a FileResponse with the fetched PDF content
                    try:
                        pdf_response = requests.get(pdf_path, timeout=10)
                        pdf_response.raise_for_status()
                    except requests.RequestException as e:
                        return Response({"status": "error", "message": f"Error fetching PDF content: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Create a FileResponse with the fetched PDF content
                    filename = 'registro_de_llamada' + '_' + formated_call_information[0].get('detainee')+'.pdf'
                    pdf_content = pdf_response.content
                    pdf_file_response = HttpResponse(pdf_content, content_type='application/pdf')
                    pdf_file_response['Content-Disposition'] = f'inline; filename="{filename}"'

                    # Return the FileResponse
                    return pdf_file_response
                else:
                    # Handle the error in fetching the PDF content
                    return Response({"status": "error", "message": "Error fetching PDF content"},
                                    status=pdf_response.status_code)
        else:
            # Handle the error in the external API response
            print(response.text)  # Print the error response
            return Response({"status": "error", "message": response.text},
                                status=response.status_code)

        return JsonResponse({"status": "success", "data": 'response'}, safe=False)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="ID of the cell related to the belongings information",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user":openapi.Schema(type=openapi.TYPE_STRING),


            },
            required=['user']
        ),
        responses={
            # 200: ActionsSerializer(many=False),
            201: openapi.Response(
                "PDF document",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
                # examples={
                #     "application/pdf": FileResponse(open("path/to/sample.pdf", "rb")),
                # },
            ),
        },
        operation_summary="Retrieves a PDF file with the information of the belongings registered on record",
        operation_description="Retrieves a PDF file with the information of the belongings registered on record",
        tags=["Records"],
        security=[{"Bearer Token": []}],  # Add this line for Authorization header
    )

    def print_belongings_info(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        #token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        # decoded_token = decode_token(token)
        # print(token)
        # user_info={}

        # if decoded_token:
        #     user_info = {'user_id': decoded_token['user_id'], 'username': decoded_token['username']}
        #     return Response(user_info)
        # else:
        #     return Response({'detail': 'Invalid or expired token'}, status=401)

        #print(user_info)

        #record_instance = Records.objects.get(id=pk).prefetch_related('detainee')
        record_instance = Records.objects.select_related('detainee', 'district').get(id=pk)


        # if record_instance is None :
        #     return Response({"status": "error", "message": "record_not_found"}, safe=False)

        # Get the Record instance
        #record_instance = get_object_or_404(Record, id=record_id)

        #cell_instance = Cells.objects.get(record=record_instance.id)
        # cell_instance = Cells.objects.get(id=pk)

        # if not cell_instance.exists() :
        #     return Response({"status": "error", "message": "cell_not_found"}, safe=False)

        try:
            cell_instance = Cells.objects.get(id=pk)
        except Cells.DoesNotExist:
            return Response({"status": "error", "message": "cell_not_found"},status=status.HTTP_404_NOT_FOUND)

        belonging_instance = Belongings.objects.get(cell=cell_instance.id)
        if belonging_instance is None :
            return Response({"status": "error", "message": "belongings_record_not_found"}, status=status.HTTP_404_NOT_FOUND)

        record_instance = Records.objects.select_related('detainee', 'district').get(id=cell_instance.record_id)
        detainee_instance = record_instance.detainee
        full_name = (
            f"{detainee_instance.name} "
            f"{detainee_instance.fathers_name or ''} "
            f"{detainee_instance.mothers_name or ''}"
        )
        district_instance = record_instance.district
        district_name = district_instance.name if district_instance else None
        record_info_dict = model_to_dict(record_instance)
        cell_info_dict = model_to_dict(cell_instance)
        belonging_info_dict = model_to_dict(belonging_instance)
        locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

        utc_now = datetime.utcnow()

        # Convert UTC time to local time
        local_timezone = pytz.timezone('America/Denver')  # Replace with your local timezone
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        # Format the local time with Spanish month names
        formated_time = local_now.strftime('%d de %B de %Y %H:%M')
        # Format the date with Spanish month names
        formated_date = local_now.strftime('%d de %B de %Y')
        # Format the hour
        formated_hour = local_now.strftime('%H:%M')

        formated_data={
                "folio": record_info_dict['folio_afi'],
                "registration_datetime": formated_time,
                "hour":formated_hour,
                "date":formated_date,
                "detainee": full_name,
                "district_name": district_name,
                "user": request.data.get('user'),
                "devices_laptop": belonging_info_dict['devices_laptop'],
                "devices_charger": belonging_info_dict['devices_charger'],
                "devices_aux": belonging_info_dict['devices_aux'],
                "accesories_cap": belonging_info_dict['accesories_cap'],
                "money_mexican_pesos": belonging_info_dict['money_mexican_pesos']
        }

        #CODE TO RETRIEVE PDF
        siprob_prints_url = default_prints_url
        if os.getenv("ENVIRONMENT")=='LOCAL':
            siprob_prints_url = "http://localhost:8023/"
        full_url= siprob_prints_url + 'pertenencias'
        #record_info_dict['medical_date_time'] = record_info_dict['medical_date_time'].isoformat()

        response = requests.post(full_url, json=formated_data, timeout=30)
        if response.status_code == 200:
                response_data = response.json()
                pdf_path = siprob_prints_url+response_data.get("path")
                pdf_response = requests.get(pdf_path, timeout=30)
                if pdf_response.status_code == 200:
                    # Successfully fetched the PDF content
                    # Create a FileResponse with the fetched PDF content
                    try:
                        pdf_response = requests.get(pdf_path, timeout=10)
                        pdf_response.raise_for_status()
                    except requests.RequestException as e:
                        return Response({"status": "error", "message": f"Error fetching PDF content: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # Create a FileResponse with the fetched PDF content
                    filename = 'pertenencias' + '_' + full_name+'_'+record_info_dict.get('folio_afi')+'.pdf'
                    pdf_content = pdf_response.content
                    pdf_file_response = HttpResponse(pdf_content, content_type='application/pdf')
                    pdf_file_response['Content-Disposition'] = f'inline; filename="{filename}"'

                    # Return the FileResponse
                    return pdf_file_response
                else:
                    # Handle the error in fetching the PDF content
                    return Response({"status": "error", "message": "Error fetching PDF content"},
                                    status=pdf_response.status_code)
        else:
            # Handle the error in the external API response
            print(response.text)  # Print the error response
            return Response({"status": "error", "message": response.text},
                                status=response.status_code)




    # record_data = {
    #     "medic": openapi.Schema(type=openapi.TYPE_STRING),
    #     "weight": openapi.Schema(type=openapi.TYPE_INTEGER),
    #     "height": openapi.Schema(type=openapi.TYPE_INTEGER),
    #     "intoxication": openapi.Schema(type=openapi.TYPE_STRING),
    #     "mental": openapi.Schema(type=openapi.TYPE_STRING),
    #     "general_condition": openapi.Schema(type=openapi.TYPE_STRING),
    #     "pathologies": openapi.Schema(type=openapi.TYPE_STRING),
    #     "TO": openapi.Schema(type=openapi.TYPE_STRING),
    #     "FC": openapi.Schema(type=openapi.TYPE_STRING),
    #     "FR": openapi.Schema(type=openapi.TYPE_STRING),
    #     "TA": openapi.Schema(type=openapi.TYPE_STRING),
    #     "saturation": openapi.Schema(type=openapi.TYPE_STRING),
    #     "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
    #     "blood_type": openapi.Schema(type=openapi.TYPE_STRING),
    #     "rh_factor": openapi.Schema(type=openapi.TYPE_STRING),
    #     "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
    # }

    # @swagger_auto_schema(
    #     responses={201: RoleSerializer(many=False)},
    #     operation_summary="Delete role with the primary key provided in url",
    #     operation_description="This endpoint does a soft delete of the role on database.",
    #     tags=["Roles"],
    # )

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance:
    #         instance.is_active=False
    #         instance.save()
    #         return Response(
    #             {
    #                 'status':'success',
    #                 'message':'Role_deleted'

    #             },
    #             status=status.HTTP_204_NO_CONTENT
    #             )
    #     return Response({'status':'fail','message':'Role not found'},status=status.HTTP_404_NOT_FOUND)

    # @swagger_auto_schema(
    #     responses={201: RoleSerializer(many=False)},
    #     operation_summary="Updates the role with the primary key provided in url",
    #     operation_description="This endpoint updates the information on the role with the id provided in URL.",
    #     tags=["Roles"]
    # )
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     if instance:
    #         serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_update(serializer)
    #         return Response({'status':'success','data':serializer.data})
    #     return Response({'status':'fail','message':'Role not found'},status=status.HTTP_404_NOT_FOUND)
