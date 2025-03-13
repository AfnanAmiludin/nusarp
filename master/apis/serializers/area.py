from rest_framework import serializers
from master.models.area import Area

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = [
            'area_id', 
            'area_name', 
            'parent', 
            'status'
        ]