from rest_framework import serializers
from authentication.models.asset import Model

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [
            'user_id',
            'user_name',
            'real_name',
            'email',
            'phone',
            'password',
            'avatar',
            'locale',
            'timezone',
            'last_ip_address',
            'last_activity_date',
            'actived_date',
            'is_staff',
            'is_active',
            'date_joined',
            'status'
        ]
