from rest_framework import serializers
from ..models import District
from .projects import ProjectSerializer  # Make sure import is correct

class DistrictSerializer(serializers.ModelSerializer):
    # project = ProjectSerializer(source='fid', read_only=True)

    class Meta:
        model = District
        fields = [ 'project', 'name', 'name_m', 'geom']
