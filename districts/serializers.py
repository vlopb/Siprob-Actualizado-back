from rest_framework import serializers
from districts.models import *

class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields =['name', 'created_at', 'updated_at']
        ref_name = 'District'