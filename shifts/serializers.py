from rest_framework import serializers
from shifts.models import *

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields =['id', 'start_hour','end_hour','created_at', 'updated_at']
        ref_name = 'Shift'