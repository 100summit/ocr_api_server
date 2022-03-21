from rest_framework import serializers
from .models import OcrDatas


class OcrDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcrDatas
        fields = ['test1', 'test2', 'test3', 'test4']

