from django.forms import widgets
from rest_framework import serializers
from service.models import Kafic, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User


class KaficSerializer(serializers.ModelSerializer):
    #vlasnik = serializers.Field(source='vlasnik.username')

    class Meta:
        model = Kafic
        fields = ('id', 'naziv', 'adresa', 'broj_stolova', 'vlasnik')


class UserSerializer(serializers.ModelSerializer):
    kafici = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'kafici')