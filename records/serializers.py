from rest_framework import serializers
from records.models import *
from districts.serializers import DistrictsSerializer
from detainees.serializers import DetaineesSerializer

# class ProcessSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Process
#         fields =['name','created_at','updated_at']

class RecordsSerializer(serializers.ModelSerializer):
    # district = DistrictsSerializer()
    # detainee = DetaineesSerializer()
    class Meta:
        model = Records
        fields = '__all__'

class ReportsRecordsSerializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    detainee = DetaineesSerializer()
    class Meta:
        model = Records
        fields = '__all__'

class OtherRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherRecords
        fields = '__all__'

class OtherRecordsDetaineesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherRecordsDetainees
        fields = '__all__'

class OffendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offended
        fields =['record','name','fathers_name','mothers_name','relationship','created_at','updated_at']

class RecordsPoliceAgentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordsPoliceAgents
        fields =['employee_number','record','created_at','updated_at']

class CellNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Belongings
        fields =['record','note','created_at','updated_at']

class BelongingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordsPoliceAgents
        fields =['record','description','delivered_to_another','delivery_reason','delivered_to','created_at','updated_at']

class MedicalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInformation
        fields =['record','medic_name','medical_cedula','medical_date_time','folio','weight','height','intoxication','mental','general_condition','user','pathologies','medical_t','medical_fc','medical_fr','medical_ta','saturation','diagnostic','blood_type','rh_factor','has_lesions','created_at','updated_at']

class LesionPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = LesionsPhotos
        fields =['image_path','created_at','updated_at']

class LesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesions
        fields =['record','medical_information','location','discriminator','descriptions','image_path','created_at','updated_at']

# class VehiclesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicles
#         fields =['record','detainee','reason','date','place','holder_name','brand','line','discriminator','model','color','plates','serial_number','stamp_number','asociation_expeditor','comments','created_at','updated_at']

# class ObjectsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Objects
#         fields =['record','detainee','reason','discriminator','subtype','quantity','general_condition','description','created_at','updated_at']

class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields =['record','datetime','description','status','created_at','updated_at']

class FaultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faults
        fields =['event','discriminator','subtype','discriminator','created_at','updated_at']

class ActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actions
        fields = '__all__'

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionNotes
        fields = ['id','action','user','text','created_at','updated_at']