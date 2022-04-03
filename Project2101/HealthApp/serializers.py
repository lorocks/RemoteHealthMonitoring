from rest_framework import serializers
from .models import testingAPI

class testingAPISerializer(serializers.ModelSerializer):
    data = serializers.FloatField()
    string = serializers.CharField(max_length=200)

    class Meta:
        model = testingAPI
        fields = ('__all__')