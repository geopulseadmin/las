
from rest_framework import serializers
from ..models import Project, District

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'  # Or specify fields: ['uid', 'name', ...]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'project_id': data['uid'],
            'Project_Name': data['name'],
            'Project_Name_Marathi': data['name_m'],
            'description': data['remark'],
            'geometry': data['geom'],
        }


class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ['name_m', 'geom']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'district_name': data['name_m'],
            'geom': data['geom'],
        }


from rest_framework import serializers
from ..models import Taluka

class TalukaSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.name_m', read_only=True)

    class Meta:
        model = Taluka
        fields = ['uid', 'name_m', 'geom', 'district_name', 'project_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'taluka_name': data['name_m'],
            'district_name': data['district_name'],
            'project_name': data['project_name'],
            'geom': data['geom']
        }


from rest_framework import serializers
from ..models import Village

class VillageSerializer(serializers.ModelSerializer):
    taluka_name = serializers.CharField(source='fid.name_m', read_only=True)
    district_name = serializers.CharField(source='fid.fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.fid.name_m', read_only=True)


    class Meta:
        model = Village
        fields = ['uid', 'name_m', 'geom', 'project_name','district_name', 'taluka_name' ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'village_name': data['name_m'],
            'district_name': data['district_name'],
            'project_name': data['project_name'],
            'taluka_name': data['taluka_name'],
            'geom': data['geom']
        }



from ..models import Gut, Bund


class BundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bund
        fields = ['name_m', 'acquiretype', 'ownertype','permtype','geom']

class GutSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source='fid.name_m', read_only=True)
    taluka_name = serializers.CharField(source='fid.fid.name_m', read_only=True)
    district_name = serializers.CharField(source='fid.fid.fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.fid.fid.name_m', read_only=True)
    bunds = BundSerializer(source='bund_set', many=True, read_only=True)


    class Meta:
        model = Gut
        fields = ['uid', 'name_m', 'geom', 'project_name','district_name', 'taluka_name','village_name', 'bunds' ]
    ## for flattening the gut number and bund data
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     # Extract gut information
    #     gut_data = {
    #         'gut_id': instance.uid,
    #         'gut_no': data['name_m'],
    #         'village': data['village_name'],
    #         'district': data['district_name'],
    #         'project': data['project_name'],
    #         'taluka': data['taluka_name'],
    #         'gut_geometry': data['geom']
    #     }

        # Process each bund and combine with gut info
        # result = []
        # if data.get('bunds'):
        #     for bund in data['bunds']:
        #         combined = gut_data.copy()  # Copy gut info
        #         combined.update({
        #             'land_owner_name': bund.get('name_m', ''),
        #             'aquis_status': bund.get('acquiretype', ''),
        #             'ownership': bund.get('ownertype', ''),
        #             'permission_type': bund.get('permtype', ''),
        #             'bund_geometry': bund.get('geom', '')
        #         })
        #         result.append(combined)

        # return result


    def to_representation(self, instance):
        data = super().to_representation(instance)
    
        formatted_bunds = []
        if 'bunds' in data and data['bunds']:
            for bund in data['bunds']:
                formatted_bunds.append({
                    'bund_name': bund['name_m'],
                    'acquire_type': bund['acquiretype'],  # Include acquiretype
                    'geometry': bund['geom']
                })
        return {
            'gut':data['name_m'],
            'village_name': data['village_name'],
            'district_name': data['district_name'],
            'project_name': data['project_name'],
            'taluka_name': data['taluka_name'],
            'geom': data['geom'],
            'bunds': formatted_bunds
        }


