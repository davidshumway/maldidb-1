from rest_framework import serializers
from .models import *

class CollapsedSpectraSerializer(serializers.ModelSerializer):
  class Meta:
    model = CollapsedSpectra
    fields = '__all__'

class SpectraSerializer(serializers.ModelSerializer):
  class Meta:
    model = Spectra
    fields = '__all__'
