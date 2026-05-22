from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from yaml import serialize
from detainees.serializers import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from detainees.models import Detainee, Addresses 
from districts.models import District
from districts.serializers import DistrictsSerializer
from users.models import User
from records.models import Belongings, CallsRegistry, Cells, Events, Records, Photos, MedicalInformation, Actions
from detainees.serializers import DetaineesSerializer,AddressesSerializer, PhotosSerializer
from records.serializers import RecordsSerializer, MedicalInformationSerializer, ActionsSerializer
from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class DetaineesViewSet(viewsets.ModelViewSet):
    queryset = Detainee.objects.filter(is_active=True)
    serializer_class = DetaineesSerializer
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset
        self.check_object_permissions(self.request, obj)
        return obj
    
    @swagger_auto_schema(
        operation_summary="Lists all detainees",
        operation_description="This endpoint lists all the detainees on the database.",
        tags=["Detainees"],
    )
    def get(self, request, *args, **kwargs):
        detainees = Detainee.objects.filter(is_active=True)
        serializer = DetaineesSerializer(detainees, many=True)
        return Response({'status': 'success', 'data': serializer.data})
        #return Role.objects.filter(is_active=True)
    
    general_data_schema_body = {
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "entry_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "photo_path": openapi.Schema(type=openapi.TYPE_STRING),
        "birth_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "age": openapi.Schema(type=openapi.TYPE_INTEGER),
        "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
        "sexual_preferences": openapi.Schema(type=openapi.TYPE_STRING),
        "occupation": openapi.Schema(type=openapi.TYPE_STRING),
        "gender": openapi.Schema(type=openapi.TYPE_STRING),
        "nicknames": openapi.Schema(type=openapi.TYPE_STRING),
        "fake_names": openapi.Schema(type=openapi.TYPE_STRING),
        "ethnicity": openapi.Schema(type=openapi.TYPE_STRING),
        "schooling": openapi.Schema(type=openapi.TYPE_STRING),
        "nationality": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
        "district": openapi.Schema(type=openapi.TYPE_NUMBER),
        "home_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="home"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        "work_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="work"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    }

    general_data_schema_response = {
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "entry_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "photo_path": openapi.Schema(type=openapi.TYPE_STRING),
        "birth_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "age": openapi.Schema(type=openapi.TYPE_INTEGER),
        "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
        "sexual_preferences": openapi.Schema(type=openapi.TYPE_STRING),
        "occupation": openapi.Schema(type=openapi.TYPE_STRING),
        "gender": openapi.Schema(type=openapi.TYPE_STRING),
        "nickname": openapi.Schema(type=openapi.TYPE_STRING),
        "fake_names": openapi.Schema(type=openapi.TYPE_STRING),
        "ethnicity": openapi.Schema(type=openapi.TYPE_STRING),
        "schooling": openapi.Schema(type=openapi.TYPE_STRING),
        "nationality": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
        "district": openapi.Schema(type=openapi.TYPE_NUMBER),
        "home_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="home"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        "work_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="work"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    }

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "general_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties=general_data_schema_body),
                "entry_dates": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        "notes": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
                },
        ),
        responses={
            201: openapi.Response(
                description="Detainee created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                     properties={
                        "general_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties=general_data_schema_response),
                        "entry_dates": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={                            
                                "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                "notes": openapi.Schema(type=openapi.TYPE_STRING)                           
                            },
                            ),
                        ),
                        "actions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={                            
                                "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "action_folio": openapi.Schema(type=openapi.TYPE_STRING),
                                "folio_afi": openapi.Schema(type=openapi.TYPE_STRING),
                                "created_by": openapi.Schema(type=openapi.TYPE_STRING),
                                "written_to": openapi.Schema(type=openapi.TYPE_STRING),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                            },
                            ),
                        ),
                    },
                ),
            ),
        },
    operation_summary="Creates a new Detainee",
    operation_description="This endpoint creates a new detainee.",
    tags=["Detainees"],
    )
    def post(self, request, *args, **kwargs):

        general_data = request.data.get('general_data')
        detainee = Detainee()
        detainee.name = general_data.get('name')
        detainee.fathers_name = general_data.get('fathers_name')
        detainee.mothers_name = general_data.get('mothers_name')
        detainee.birth_date = general_data.get('birth_date')
        detainee.age = general_data.get('age')
        detainee.marital_status = general_data.get('marital_status')
        detainee.sexual_preferences = general_data.get('sexual_preferences')
        detainee.occupation = general_data.get('occupation')
        detainee.gender = general_data.get('gender')
        detainee.nicknames = general_data.get('nicknames')
        detainee.fake_names = general_data.get('fake_names')
        detainee.ethnicity = general_data.get('ethnicity')
        detainee.schooling = general_data.get('schooling')
        detainee.nationality = general_data.get('nationality')
        detainee.notes = general_data.get('notes')
        detainee.save()
        
        if general_data.get('work_address') is not None:
            work_address = general_data.get('work_address')
            addresses = Addresses()
            addresses.detainee_id = detainee.id
            addresses.discriminator = 'work'
            addresses.country = work_address.get('country')
            addresses.state = work_address.get('state')
            addresses.municipality = work_address.get('municipality')
            addresses.locality = work_address.get('locality')
            addresses.street = work_address.get('street')
            addresses.exterior_number = work_address.get('exterior_number')
            addresses.interior_number = work_address.get('interior_number')
            addresses.colony = work_address.get('colony')
            addresses.postal_code = work_address.get('postal_code')
            addresses.save()

        if general_data.get('home_address') is not None:
            home_address = general_data.get('home_address')
            addresses = Addresses()
            addresses.detainee_id = detainee.id
            addresses.discriminator = 'home'
            addresses.country = home_address.get('country')
            addresses.state = home_address.get('state')
            addresses.municipality = home_address.get('municipality')
            addresses.locality = home_address.get('locality')
            addresses.street = home_address.get('street')
            addresses.exterior_number = home_address.get('exterior_number')
            addresses.interior_number = home_address.get('interior_number')
            addresses.colony = home_address.get('colony')
            addresses.postal_code = home_address.get('postal_code')
            addresses.save()
        
        photo = Photos()
        photo.image_path = general_data.get('photo_path')
        photo.detainee_id = detainee.id
        photo.save()
        saved_entry_dates =[]

        if request.data.get('entry_dates') is not None and len(request.data.get('entry_dates')) > 0:
            
            received_dates = request.data.get('entry_dates')
            for entry in received_dates:
                print(entry)
                date_received=entry.get('date_time')
                new_record_data = {
                    'detainee': detainee.id,
                    'entry_date': entry.get('date_time'),
                    'qualification_release_date': None,
                    'notes': entry.get('notes'),
                    'district':general_data.get('district')                
                } 

                print("NEW RECORD DATA: ", new_record_data)               

                current_date = timezone.now().date()
                date_string = current_date.strftime("%Y-%m-%d")
                #date_string_without_hyphen = date_string.replace("-", "")
                date_string_without_hyphen = date_received[:19]
                district_name=""
                try:
                    district_id = general_data.get('district')
                    district_information = District.objects.get(pk=district_id)
                    # Access the attributes of the district_information object as needed
                    district_name = district_information.name[:3]
                    # Add more attributes as needed
                except District.DoesNotExist:
                    # Handle the case where the District with the specified id doesn't exist
                    district_information = None                
                new_record_data['folio_afi']='DET-'+district_name+'-'+str(detainee.id)+'-'+date_string_without_hyphen                               
                new_record_serializer = RecordsSerializer(data=new_record_data)
        
                if new_record_serializer.is_valid():                    
                    new_record_serializer.save()
                    new_record_id = new_record_serializer.data.get('id')
                    # Include the id in new_record_data
                    new_record_data['id'] = new_record_id
                    saved_entry_dates.append(new_record_data)

                else:
                # Handle the case where the serializer is not valid, perhaps log the errors
                    print("Errors in RecordsSerializer:", new_record_serializer.errors)
                    Response({'status':'fail','error':new_record_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                print("SAVED ENTRY DATES: ",saved_entry_dates)
        request.data['general_data']['id'] = detainee.id
        response_data = request.data
        response_data['entry_dates']=saved_entry_dates

        return Response({'status':'success','data':response_data}, status=status.HTTP_201_CREATED)

class SingleDetaineeViewSet(viewsets.ModelViewSet):
    queryset = Detainee.objects.filter(is_active=True)
    serializer_class = DetaineesSerializer    

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=self.kwargs['pk'], is_active=True).first()
        self.check_object_permissions(self.request, obj)
        return obj

    general_data_schema_response = {
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "fathers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "mothers_name": openapi.Schema(type=openapi.TYPE_STRING),
        "entry_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "photo_path": openapi.Schema(type=openapi.TYPE_STRING),
        "birth_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        "age": openapi.Schema(type=openapi.TYPE_INTEGER),
        "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
        "sexual_preferences": openapi.Schema(type=openapi.TYPE_STRING),
        "occupation": openapi.Schema(type=openapi.TYPE_STRING),
        "gender": openapi.Schema(type=openapi.TYPE_STRING),
        "nicknames": openapi.Schema(type=openapi.TYPE_STRING),
        "fake_names": openapi.Schema(type=openapi.TYPE_STRING),
        "ethnicity": openapi.Schema(type=openapi.TYPE_STRING),
        "schooling": openapi.Schema(type=openapi.TYPE_STRING),
        "nationality": openapi.Schema(type=openapi.TYPE_STRING),
        "notes": openapi.Schema(type=openapi.TYPE_STRING),
        "district": openapi.Schema(type=openapi.TYPE_NUMBER),
        "home_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="home"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        "work_address": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "discriminator": openapi.Schema(type=openapi.TYPE_STRING, default="work"),
                "country": openapi.Schema(type=openapi.TYPE_STRING),
                "state": openapi.Schema(type=openapi.TYPE_STRING),
                "municipality": openapi.Schema(type=openapi.TYPE_STRING),
                "locality": openapi.Schema(type=openapi.TYPE_STRING),
                "street": openapi.Schema(type=openapi.TYPE_STRING),
                "exterior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "interior_number": openapi.Schema(type=openapi.TYPE_STRING),
                "colony": openapi.Schema(type=openapi.TYPE_STRING),
                "postal_code": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    }

    @swagger_auto_schema(        
        responses={
            201: openapi.Response(
                description="Detainee retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                     properties={
                        "general_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties=general_data_schema_response),
                        "entry_dates": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={                            
                                "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                "notes": openapi.Schema(type=openapi.TYPE_STRING)                           
                            },
                            ),
                        ),
                        "medical_history": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={                                                            
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "medical_folio": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_history_date": openapi.Schema(type=openapi.TYPE_STRING),
                                "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_t": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_fc": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_fr": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_ta": openapi.Schema(type=openapi.TYPE_STRING),
                                "saturation": openapi.Schema(type=openapi.TYPE_STRING),
                                "medic": openapi.Schema(type=openapi.TYPE_STRING),
                                "folio_afi": openapi.Schema(type=openapi.TYPE_STRING)                              
                            },
                            ),
                        ),
                    },
                ),
            ),
        },
        operation_summary="Retrieves the detainee with the primary key provided in url",
        operation_description="This endpoint retrieves the information for the detainee .",
        tags=["Detainees"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:     
            serializer = self.get_serializer(instance) 
            work_addresses_queryset = Addresses.objects.filter(detainee=instance, discriminator='work')            
            # Check if there's exactly one work address
            if work_addresses_queryset.count() > 0:
                work_address_serializer = AddressesSerializer(work_addresses_queryset.first())
            else:
                # Handle the case where there are no work addresses or more than one
                work_address_serializer = None  # You can set this to a default value or handle it based on your needs
            
            home_addresses_queryset = Addresses.objects.filter(detainee=instance, discriminator='home')            
            # Check if there's exactly one work address
            if home_addresses_queryset.count() > 0:
                home_address_serializer = AddressesSerializer(home_addresses_queryset.first())
            else:
                # Handle the case where there are no work addresses or more than one
                home_address_serializer = None  # You can set this to a default value or handle it based on your needs
            
            response_photo_path="",
            photo_queryset = Photos.objects.filter(detainee=instance).order_by('-created_at')        
            # Check if there's exactly one work address
            if photo_queryset.count() > 0:
                photo_serializer = PhotosSerializer(photo_queryset.first())
                response_photo_path = photo_serializer.data.get('image_path')
            else:
                # Handle the case where there are no work addresses or more than one
                photo_serializer = None
                response_photo_path = None  # You can set this to a default value or handle it based on your needs
            
            records_queryset = Records.objects.filter(detainee=instance, is_active=True).order_by('-entry_date')          
            records_data = list(records_queryset.values())          

            saved_entry_dates =[]
            if records_data is not None and len(records_data) > 0:                
                for entry in records_data:
                    saved_entry_object={
                        'id':entry.get('id'),
                        'district':entry.get('district_id'),
                        'detainee':entry.get('detainee_id'),
                        'entry_date':entry.get('entry_date'),
                        'notes': entry.get('notes'),
                        'folio_afi':entry.get('folio_afi'),
                        'qualification_release_date':entry.get('qualification_release_date')
                    }                                        

                    saved_entry_dates.append(saved_entry_object)                              
            
            medical_history_items=[]
            if len(saved_entry_dates)>0:
                medical_history_queryset=MedicalInformation.objects.filter(record=saved_entry_dates[0].get('id')).order_by('-created_at')

                if medical_history_queryset.count() > 0:
                    for medical_info in medical_history_queryset.values():
                        try:
                            record = Records.objects.get(id=medical_info.get('record_id'))
                        except Records.DoesNotExist:
                            print("record does not exist")
                        medical_history_object={
                            'id':medical_info.get('id'),
                            'folio_afi':record.folio_afi,
                            'medical_folio':medical_info.get('folio'),
                            'medical_history_date':medical_info.get('created_at'),                            
                            'medic':medical_info.get('medic_name'),
                            'medical_cedula':medical_info.get('medical_cedula'),
                            'medical_date_time':medical_info.get('medical_date_time'),
                            'diagnostic':medical_info.get('diagnostic'),
                            'medical_t':medical_info.get('medical_t'),
                            'medical_fc':medical_info.get('medical_fc'),
                            'medical_fr':medical_info.get('medical_fr'),
                            'medical_ta':medical_info.get('medical_ta'),
                            'saturation':medical_info.get('saturation'),
                        }
                        
                        medical_history_items.append(medical_history_object)

                    medical_history_serializer = medical_history_queryset.values()
                else:
                    # Handle the case where there is no medical history
                    medical_history_serializer = None
                
            else:
                medical_history_serializer = None  # You can set this to a default value or handle it based on your needs          

            detentions_history = Records.objects.filter(detainee_id=serializer.data.get('id'))
            records_ids = [
                    detention_history.id
                for detention_history in detentions_history
            ]
            

            events = Events.objects.filter(record_id__in=records_ids).prefetch_related('record')
            formated_events = [
                {
                    "id": event.id,
                    "qualifies": event.qualifies,
                    "detention_folio": event.detention_folio,
                    "created_at": event.created_at,
                    "record_folio": event.record.folio_afi,
                    "created_by": event.created_by,
                    "discriminator": event.discriminator,
                    "type": event.type,
                    "subtype": event.subtype,
                    "detention_datetime": event.detention_datetime,
                    "event_datetime": event.event_datetime,
                    "event_description": event.event_description,
                } for event in events
            ]

            cells_history = Records.objects.filter(detainee_id=serializer.data.get('id'))
            records_ids = [
                    detention_history.id
                for detention_history in cells_history
            ]

            cells = Cells.objects.filter(record_id__in=records_ids).prefetch_related('record__detainee')

            formated_cells = [
                {
                    "id": cell.id,
                    "assignment_folio": cell.assignment_folio,
                    "notes": cell.cell_notes,
                    "folio_afi": cell.record.folio_afi,
                    "cell": cell.cell,
                    "created_at": cell.created_at,
                    "updated_at": cell.updated_at,
                    "detainee":f"{cell.record.detainee.name} {cell.record.detainee.fathers_name} {cell.record.detainee.mothers_name}".replace("None", "") if cell.record else "",
                    "created_by": cell.created_by,
                    "belongings_registered": cell.registered_belongings,
                    "calls_registered": cell.registered_calls,
                    "total_belongings": cell.total_belongings,
                    "total_calls": cell.total_calls,
                } for cell in cells
            ]

            actions_for_detainee = Actions.objects.filter(record__detainee=instance).order_by('-created_at')

            formated_actions = [
                {
                    "id": action.id,
                    "action_folio": action.action_folio,
                    "folio_afi": action.record.folio_afi,                    
                    "discriminator": action.discriminator,
                    "created_by": action.user,
                    "created_at": action.created_at,
                    "updated_at": action.updated_at
                    
                } for action in actions_for_detainee
            ]


            response_data = {
                'general_data': {
                    **serializer.data,
                    'photo_path': response_photo_path,
                    'work_address': work_address_serializer.data if work_address_serializer else None,
                    'home_address': home_address_serializer.data if home_address_serializer else None,
                    
                },
                'entry_dates': saved_entry_dates,
                'medical_history':medical_history_items,
                'detentions':formated_events,
                'cells':formated_cells,
                'actions':formated_actions
            }

            return Response({'status': 'success', 'data': response_data})

        return Response({'status': 'fail', 'message': 'Detainee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    response = {
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "detainee_id": openapi.Schema(type=openapi.TYPE_STRING),
                "qualification_release_date": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Detainee ID",
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                "release_type": openapi.Schema(type=openapi.TYPE_STRING),
                "release_reason": openapi.Schema(type=openapi.TYPE_STRING),
                "release_important_cell_note": openapi.Schema(type=openapi.TYPE_STRING),
                "official_release_date": openapi.Schema(type=openapi.TYPE_STRING,format="date-time"),                
            },
        ),
        responses={
            200: openapi.Response(
                description="Detainee is free like",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status":openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, 
                            properties={
                                "detainee_id":openapi.Schema(type=openapi.TYPE_INTEGER),
                                "official_release_date":openapi.Schema(type=openapi.TYPE_STRING),

                            }
                        )
                    },
                ),
            ),
        },
        operation_summary="Releases the detainee with the id provided",
        operation_description="Releases the detainee with the id provided.",
        tags=["Detainees"],
    )
    def release(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            print(pk)
            detainee = Detainee.objects.get(id=pk)
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
            record = Records.objects.get(id=latest[0].get('record_id'))
            record.official_release_date = timezone.now()
            record.release_type = request.data.get('release_type')
            record.release_reason = request.data.get('release_reason')
            record.release_important_cell_note = request.data.get('release_important_cell_note')
            record.save()
            response_data = {
                "detanee_id": record.detainee_id,
                "official_release_date": record.official_release_date,
            }
        except Detainee.DoesNotExist:
            response_data = "detainee not found"
        except Records.DoesNotExist:
            response_data = "record not found "

        return Response({'status': 'success', 'data': response_data})

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "general_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties=general_data_schema_response),
                "entry_dates": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={                            
                            "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                            "notes": openapi.Schema(type=openapi.TYPE_STRING)                           
                        },
                    ),
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Detainee updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "general_data": openapi.Schema(type=openapi.TYPE_OBJECT, properties=general_data_schema_response),
                        "entry_dates": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={                            
                                "date_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                "notes": openapi.Schema(type=openapi.TYPE_STRING),
                                "medical_history": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={                                                            
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "medical_folio": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medical_history_date": openapi.Schema(type=openapi.TYPE_STRING),
                                        "diagnostic": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medical_t": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medical_fc": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medical_fr": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medical_ta": openapi.Schema(type=openapi.TYPE_STRING),
                                        "saturation": openapi.Schema(type=openapi.TYPE_STRING),
                                        "medic": openapi.Schema(type=openapi.TYPE_STRING),
                                        "folio_afi": openapi.Schema(type=openapi.TYPE_STRING)                              
                                    },
                                ),
                        ),                           
                            },
                            ),
                        ),
                    },
                ),
            ),
            # Add more response codes as needed
        },
        operation_summary="Updates the detainee with the primary key provided in the URL",
        operation_description="This endpoint updates the information for the detainee.",
        tags=["Detainees"],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = kwargs.get("pk")
        instance = self.get_object()
        if instance:
            if request.data.get('general_data') is not None:
                general_data = request.data.get('general_data')               

                try:
                    detainee = Detainee.objects.get(id=pk)
                    detainee.name = detainee.name if general_data.get('name') == None else general_data.get('name')
                    detainee.fathers_name = detainee.fathers_name if general_data.get('fathers_name') == None else general_data.get('fathers_name')
                    detainee.mothers_name = detainee.mothers_name if general_data.get('mothers_name') == None else general_data.get('mothers_name')
                    detainee.birth_date = detainee.birth_date if general_data.get('birth_date') == None else general_data.get('birth_date')
                    detainee.age = detainee.age if general_data.get('age') == None else general_data.get('age')
                    detainee.nicknames = detainee.nicknames if general_data.get('nicknames') == None else general_data.get('nicknames')
                    detainee.fake_names = detainee.fake_names if general_data.get('fake_names') == None else general_data.get('fake_names')
                    detainee.marital_status = detainee.marital_status if general_data.get('marital_status') == None else general_data.get('marital_status')
                    detainee.gender = detainee.gender if general_data.get('gender') == None else general_data.get('gender')
                    detainee.sexual_preferences = detainee.sexual_preferences if general_data.get('sexual_preferences') == None else general_data.get('sexual_preferences')
                    detainee.ethnicity = detainee.ethnicity if general_data.get('ethnicity') == None else general_data.get('ethnicity')
                    detainee.schooling = detainee.schooling if general_data.get('schooling') == None else general_data.get('schooling')
                    detainee.occupation = detainee.occupation if general_data.get('occupation') == None else general_data.get('occupation')
                    detainee.nationality = detainee.nationality if general_data.get('nationality') == None else general_data.get('nationality')
                    detainee.notes = detainee.notes if general_data.get('notes') == None else general_data.get('notes')
                    detainee.save()
                except Detainee.DoesNotExist:
                        return Response({'status': 'error', 'message': "detainee_not_found"})

            if general_data.get('work_address') is not None:
                try:
                    work_data = general_data.get('work_address')
                    detainee_work = Addresses.objects.get(detainee_id=pk, discriminator="work")
                    detainee_work.discriminator = "work"
                    detainee_work.country = detainee_work.country if work_data.get('country') == None else work_data.get('country')
                    detainee_work.postal_code = detainee_work.postal_code if work_data.get('postal_code') == None else work_data.get('postal_code')
                    detainee_work.exterior_number = detainee_work.exterior_number if work_data.get('exterior_number') == None else work_data.get('exterior_number')
                    detainee_work.interior_number = detainee_work.interior_number if work_data.get('interior_number') == None else work_data.get('interior_number')
                    detainee_work.street = detainee_work.street if work_data.get('street') == None else work_data.get('street')
                    detainee_work.colony = detainee_work.colony if work_data.get('colony') == None else work_data.get('colony')
                    detainee_work.locality = detainee_work.locality if work_data.get('locality') == None else work_data.get('locality')
                    detainee_work.municipality = detainee_work.municipality if work_data.get('municipality') == None else work_data.get('municipality')
                    detainee_work.state = detainee_work.state if work_data.get('state') == None else work_data.get('state')
                    detainee_work.detainee_id = pk
                    detainee_work.save()
                except Addresses.DoesNotExist:
                    detainee_work = Addresses()
                    detainee_work.discriminator = 'work'
                    detainee_work.country = work_data.get('country')
                    detainee_work.postal_code = work_data.get('postal_code')
                    detainee_work.exterior_number = work_data.get('exterior_number')
                    detainee_work.interior_number = work_data.get('interior_number')
                    detainee_work.street = work_data.get('street')
                    detainee_work.colony = work_data.get('colony')
                    detainee_work.locality = work_data.get('locality')
                    detainee_work.municipality = work_data.get('municipality')
                    detainee_work.state = work_data.get('state')
                    detainee_work.detainee_id = pk
                    detainee_work.save()
            
            if general_data.get('home_address') is not None:
                try:
                    home_data = general_data.get('home_address')
                    detainee_home = Addresses.objects.get(detainee_id=pk, discriminator="home")
                    detainee_home.discriminator = "home"
                    detainee_home.country = detainee_home.country if home_data.get('country') == None else home_data.get('country')
                    detainee_home.postal_code = detainee_home.postal_code if home_data.get('postal_code') == None else home_data.get('postal_code')
                    detainee_home.exterior_number = detainee_home.exterior_number if home_data.get('exterior_number') == None else home_data.get('exterior_number')
                    detainee_home.interior_number = detainee_home.interior_number if home_data.get('interior_number') == None else home_data.get('interior_number')
                    detainee_home.street = detainee_home.street if home_data.get('street') == None else home_data.get('street')
                    detainee_home.colony = detainee_home.colony if home_data.get('colony') == None else home_data.get('colony')
                    detainee_home.locality = detainee_home.locality if home_data.get('locality') == None else home_data.get('locality')
                    detainee_home.municipality = detainee_home.municipality if home_data.get('municipality') == None else home_data.get('municipality')
                    detainee_home.state = detainee_home.state if home_data.get('state') == None else home_data.get('state')
                    detainee_home.detainee_id = pk
                    detainee_home.save()
                except Addresses.DoesNotExist:
                    detainee_home = Addresses()
                    detainee_home.discriminator = 'home'
                    detainee_home.country = home_data.get('country')
                    detainee_home.postal_code = home_data.get('postal_code')
                    detainee_home.exterior_number = home_data.get('exterior_number')
                    detainee_home.interior_number = home_data.get('interior_number')
                    detainee_home.street = home_data.get('street')
                    detainee_home.colony = home_data.get('colony')
                    detainee_home.locality = home_data.get('locality')
                    detainee_home.municipality = home_data.get('municipality')
                    detainee_home.state = home_data.get('state')
                    detainee_home.detainee_id = pk
                    detainee_home.save()

            if general_data.get('photo_path') is not None:
                photo = Photos()
                photo.detainee_id = pk
                photo.image_path = general_data.get('photo_path')
                photo.save()
            if request.data.get('entry_dates') is not None and len(request.data.get('entry_dates')) > 0:
                entry_date = request.data.get('entry_dates')
                records = Records.objects.filter(detainee_id=pk)     
                new_record = Records()
                new_record.detainee_id = pk
                new_record.district_id = general_data.get('district')
                new_record.entry_date = entry_date[0]['date_time']
                date_string_without_hyphen = entry_date[0]['date_time'][:19]
                district_id = general_data.get('district')
                district_information = District.objects.get(pk=district_id)
                district_name = district_information.name[:3]
                new_record.folio_afi='DET-'+district_name+'-'+str(detainee.id)+'-'+date_string_without_hyphen
                new_record.save()

            detainee = Detainee.objects.get(id=pk)
            detainee_serializer = DetaineesSerializer(detainee)
            list_entry_dates = []
            records = Records.objects.filter(detainee_id=pk)     
            for record in records:
                list_entry_dates.append({"id":record.id,"folio_afi":record.folio_afi,"entry_date":record.entry_date, "qualification_release_date":record.qualification_release_date, "notes":record.notes})
            list_entry_dates.sort(key=lambda x: x.get('entry_date'), reverse=True)
            response_data = {
                "general_data": detainee_serializer.data,
                "entry_dates": list_entry_dates if len(list_entry_dates) > 0 else []
                }
            try:
                work_address = Addresses.objects.get(detainee_id=pk, discriminator="work")
                work_serializer = AddressesSerializer(work_address)
                response_data['general_data']['work_address'] = work_serializer.data
            except Addresses.DoesNotExist:
                print("work address does not exist")

            try:
                home_address = Addresses.objects.get(detainee_id=pk, discriminator="home")
                home_serializer = AddressesSerializer(home_address)
                response_data['general_data']['home_address'] = home_serializer.data
            except Addresses.DoesNotExist:
                print("home address does not exist")
            
            photo_queryset = Photos.objects.filter(detainee_id=pk).order_by('-created_at')        
            
            if photo_queryset.count() > 0:
                photo_serializer = PhotosSerializer(photo_queryset.first())
                response_data['general_data']['photo_path'] = photo_serializer.data.get('image_path')
            else:
                photo_serializer = None
                response_photo_path = None 
            
            cells_history = Records.objects.filter(detainee_id=pk)
            records_ids = [
                    detention_history.id
                for detention_history in cells_history
            ]

            cells = Cells.objects.filter(record_id__in=records_ids).prefetch_related('record__detainee')

            formated_cells = [
                {
                    "id": cell.id,
                    "assignment_folio": cell.assignment_folio,
                    "notes": cell.cell_notes,
                    "folio_afi": cell.record.folio_afi,
                    "cell": cell.cell,
                    "created_at": cell.created_at,
                    "updated_at": cell.updated_at,
                    "detainee":f"{cell.record.detainee.name} {cell.record.detainee.fathers_name} {cell.record.detainee.mothers_name}".replace("None", "") if cell.record else "",
                    "created_by": cell.created_by,
                    "belongings_registered": cell.registered_belongings,
                    "calls_registered": cell.registered_calls,
                    "total_belongings": cell.total_belongings,
                    "total_calls": cell.total_calls,
                } for cell in cells
            ]

            response_data['cells']=formated_cells

            actions_for_detainee = Actions.objects.filter(record__detainee=pk).order_by('-created_at')

            formated_actions = [
                {
                    "id": action.id,
                    "action_folio": action.action_folio,
                    "folio_afi": action.record.folio_afi,                    
                    "discriminator": action.discriminator,
                    "created_by": action.user,
                    "created_at": action.created_at,
                    "updated_at": action.updated_at
                    
                } for action in actions_for_detainee
            ]

            response_data['actions']=formated_actions


            return Response({'status': 'success', 'data': response_data})

        else:
            return Response({'status': 'fail', 'message': 'Detainee not found'}, status=status.HTTP_404_NOT_FOUND)



    # @swagger_auto_schema(
    #     request_body=RoleSerializer,
    #     responses={201: RoleSerializer(many=False)},
    #     operation_summary="Creates a new role",
    #     operation_description="This endpoint creates a new role.",
    #     tags=["Roles"],
    # )
    # def post(self, request, *args, **kwargs):
    #     super().create(request, *args, **kwargs)
    #     return Response(status=status.HTTP_201_CREATED)