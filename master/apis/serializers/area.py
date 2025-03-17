from rest_framework import serializers
from master.models.area import Area

class AreaSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Area
        fields = [
            'area_id', 
            'area_name', 
            'parent', 
            'status',
            'children',
        ]
        expandable_fields = {
            'parent': ('authentication.apis.serializers.area.AreaSerializer', {'many': False}),
        }
        read_only_fields = ['created', 'modified']
        extra_kwargs = {
            'area_id': {'read_only': True},
        }
    def get_children(self, obj):
        children = Area.objects.filter(parent=obj)
        return AreaSerializer(children, many=True).data