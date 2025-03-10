import logging

from django.contrib import auth
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType
from library.restframeworkflexfields import FlexFieldsModelSerializer

logger = logging.getLogger(__name__)

User = auth.get_user_model()


class ContentTypeSerializer(FlexFieldsModelSerializer,):
    object_name = serializers.SerializerMethodField(method_name='name_object')

    class Meta:
        model = ContentType
        fields = [
            'id',
            'app_label',
            'model',
            'name',
            'app_labeled_name',
            'object_name',
        ]

    def name_object(self, instance):
        return instance.object_name \
            if hasattr(instance, 'object_name') \
            else instance.model_class()._meta.object_name \
            if instance.model_class() is not None \
            else str(instance.model).title()
