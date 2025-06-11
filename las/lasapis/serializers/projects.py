
from rest_framework import serializers
from ..models import Project, District

# class ProjectSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Project
#         fields = '__all__'  # Or specify fields: ['uid', 'name', ...]


#     def to_representation(self, instance):
#         data = super().to_representation(instance)


#         # from django.http import JsonResponse
#         # from django.contrib.gis.db.models.functions import Transform
#         # from ..models import District
#         # districts = Project.objects.annotate(geom_wgs=Transform('geom', 4326))
        
#         # datas = []
#         # for d in districts:
#         #     datas.append(d.geom_wgs)
    

#         return {
#             'project_id': data['uid'],
#             'Project_Name': data['name'],
#             'Project_Name_Marathi': data['name_m'],
#             'description': data['remark'],
#             'geometry': data['geom'],
#         }

from rest_framework_gis.serializers import GeoModelSerializer
from ..models import Project, District

class ProjectSerializer(GeoModelSerializer):
    class Meta:
        model = Project
        geo_field = 'geom'  # specify the geometry field name
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.geom:
            transformed_instance = instance.geom.transform(4326, clone=True)
            data['geom'] = transformed_instance.geojson
        
        return {
            'project_id': data['uid'],
            'Project_Name': data['name'],
            'Project_Name_Marathi': data['name_m'],
            'description': data['remark'],
            'geometry': data['geom'], 
        }


class DistrictSerializer(GeoModelSerializer):

    class Meta:
        model = District
        fields = ['name_m', 'geom']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.geom:
            transformed_instance = instance.geom.transform(4326, clone=True)
            data['geom'] = transformed_instance.geojson
        return {
            'district_name': data['name_m'],
            'geom': data['geom'],
        }


from rest_framework import serializers
from ..models import Taluka

class TalukaSerializer(GeoModelSerializer):
    district_name = serializers.CharField(source='fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.name_m', read_only=True)

    class Meta:
        model = Taluka
        fields = ['uid', 'name_m', 'geom', 'district_name', 'project_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.geom:
            transformed_instance = instance.geom.transform(4326, clone=True)
            data['geom'] = transformed_instance.geojson
        return {
            'taluka_name': data['name_m'],
            'district_name': data['district_name'],
            'project_name': data['project_name'],
            'geom': data['geom']
        }


from rest_framework import serializers
from ..models import Village

class VillageSerializer(GeoModelSerializer):
    taluka_name = serializers.CharField(source='fid.name_m', read_only=True)
    district_name = serializers.CharField(source='fid.fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.fid.name_m', read_only=True)


    class Meta:
        model = Village
        fields = ['uid', 'name_m', 'geom', 'project_name','district_name', 'taluka_name' ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.geom:
            transformed_instance = instance.geom.transform(4326, clone=True)
            data['geom'] = transformed_instance.geojson
        return {
            'village_name': data['name_m'],
            'district_name': data['district_name'],
            'project_name': data['project_name'],
            'taluka_name': data['taluka_name'],
            'geom': data['geom']
        }



from ..models import Gut, Bund


class BundSerializer(GeoModelSerializer):
    # owner_name = serializers.CharField(source='fid.name_m', read_only=True)
    class Meta:
        model = Bund
        fields = ['name_m', 'acquiretype', 'ownertype','permtype','geom']

class GutSerializer(GeoModelSerializer):
    village_name = serializers.CharField(source='fid.name_m', read_only=True)
    taluka_name = serializers.CharField(source='fid.fid.name_m', read_only=True)
    district_name = serializers.CharField(source='fid.fid.fid.name_m', read_only=True)
    project_name = serializers.CharField(source='fid.fid.fid.fid.name_m', read_only=True)
    bunds = BundSerializer(source='bund_set', many=True, read_only=True)


    class Meta:
        model = Gut
        fields = ['uid', 'name_m', 'geom', 'project_name','district_name', 'taluka_name','village_name', 'bunds' ]
    ## for flattening the gut number and bund data
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.geom:
            transformed_instance = instance.geom.transform(4326, clone=True)
            data['geom'] = transformed_instance.geojson

        # Extract gut information
        gut_data = {
            'gut_id': instance.uid,
            'gut_no': data['name_m'],
            'village': data['village_name'],
            'district': data['district_name'],
            'project': data['project_name'],
            'taluka': data['taluka_name'],
            'gut_geometry': data['geom']
        }

        #Process each bund and combine with gut info
        result = []
        if data.get('bunds'):
            for bund in data['bunds']:
                combined = gut_data.copy()  # Copy gut info
                combined.update({
                    'land_owner_name': bund.get('name_m', ''),
                    'aquis_status': bund.get('acquiretype', ''),
                    'ownership': bund.get('ownertype', ''),
                    'permission_type': bund.get('permtype', ''),
                    'bund_geometry': bund.get('geom', '')
                })
                result.append(combined)

        return result


    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if instance.geom:
    #         transformed_instance = instance.geom.transform(4326, clone=True)
    #         data['geom'] = transformed_instance.geojson
    
    #     formatted_bunds = []
    #     if 'bunds' in data and data['bunds']:
    #         for bund in data['bunds']:
    #             formatted_bunds.append({
    #                 'bund_name': bund['name_m'],
    #                 'acquire_type': bund['acquiretype'],  # Include acquiretype
    #                 'geometry': bund['geom']
    #             })
    #     return {
    #         'gut':data['name_m'],
    #         'village_name': data['village_name'],
    #         'district_name': data['district_name'],
    #         'project_name': data['project_name'],
    #         'taluka_name': data['taluka_name'],
    #         'geom': data['geom'],
    #         'bunds': formatted_bunds
    #     }





from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import GEOSGeometry
import json
from ..models import Gut, Bund

class BundFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Bund
        geo_field = 'geom'
        fields = ['name_m', 'acquiretype', 'ownertype', 'permtype']
                #   , 'malmatta', 'other', 'utilitytype']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Transform geometry to WGS84
        if 'geometry' in data and data['geometry']:
            geom = GEOSGeometry(json.dumps(data['geometry']))
            data['geometry'] = json.loads(geom.transform(4326, clone=True).geojson)
        
        return {
            "geom": data.get('geometry', {}),
            "properties": {
                "acquire_type": data.get('acquiretype', ''),
                "ownership": data.get('ownertype', ''),
                "permission_type": data.get('permtype', ''),
                "land_owner_name": data.get('name_m', ''),

            }
        }

class GutFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gut
        fields = ['name_m', 'fid']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'gut_no': data['name_m'],
            'village': instance.fid.name_m if instance.fid else '',
            'taluka': instance.fid.fid.name_m if instance.fid and instance.fid.fid else '',
            'district': instance.fid.fid.fid.name_m if instance.fid and instance.fid.fid and instance.fid.fid.fid else '',
            'project': instance.fid.fid.fid.fid.name if instance.fid and instance.fid.fid and instance.fid.fid.fid and instance.fid.fid.fid.fid else ''
        }


from rest_framework_gis.serializers import GeoModelSerializer
from rest_framework import serializers
from django.contrib.gis.db.models.functions import Length, Area
from ..models import Project, Centreline
from django.db.models import Count

#
# class MainStatsSerializer(GeoModelSerializer):
#     length_or_area = serializers.SerializerMethodField()
#     district_name = serializers.SerializerMethodField()
#     taluka_name = serializers.SerializerMethodField()  # <-- declared
#     village_name = serializers.SerializerMethodField()  # <-- declared
#
#     class Meta:
#         model = Project
#         fields = ['uid', 'name', 'name_m', 'remark', 'length_or_area', 'district_name', 'taluka_name', 'village_name']
#
#     def get_length_or_area(self, obj):
#         centreline_qs = Centreline.objects.filter(fid=obj.uid)
#         if centreline_qs.exists():
#             total_length = centreline_qs.annotate(
#                 length=Length('geom')
#             ).aggregate(total=serializers.models.Sum('length'))['total']
#             vals = total_length.m if total_length else 0
#             return {'लांबी (मी)': round(vals, 2)}
#         else:
#             project_area = Project.objects.filter(uid=obj.uid).annotate(
#                 area=Area('geom')
#             ).values_list('area', flat=True).first()
#             vals = project_area.sq_m if project_area else 0
#             return {'क्षेत्र चौ.मी': round(vals, 2)}
#
#     def get_district_name(self, obj):
#         district = District.objects.filter(uid=obj.uid).first()
#         if district:
#             return {
#                 'name': district.name,
#                 'name_m': district.name_m,
#             }
#         return None
#
#     def get_taluka_name(self, obj):  # <-- ADD THIS
#         taluka = Taluka.objects.filter(uid=obj.uid).first()
#         if taluka:
#             return {
#                 'name': taluka.name,
#                 'name_m': taluka.name_m,
#             }
#         return None
#
#     def get_village_name(self, obj):  # <-- ADD THIS
#         village = Village.objects.filter(uid=obj.uid).first()
#         if village:
#             return {
#                 'name': village.name,
#                 'name_m': village.name_m,
#             }
#         return None


class MainStatsSerializer(GeoModelSerializer):
    length_or_area = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    taluka = serializers.SerializerMethodField()
    village = serializers.SerializerMethodField()
    gut_count = serializers.SerializerMethodField()
    bund_acquiretype_counts = serializers.SerializerMethodField()
    bund_ownertype_counts = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'uid', 'name_m', 'remark', 'length_or_area',
            'district', 'taluka', 'village',
            'gut_count', 'bund_acquiretype_counts', 'bund_ownertype_counts'
        ]

    def _get_fk(self, model, fid_val):
        return model.objects.filter(fid=fid_val).first()

    def get_length_or_area(self, obj):
        centreline_qs = Centreline.objects.filter(fid=obj.uid)
        if centreline_qs.exists():
            total_length = centreline_qs.annotate(
                length=Length('geom')
            ).aggregate(total=serializers.models.Sum('length'))['total']
            vals = total_length.m if total_length else 0
            return {'लांबी (मी)': round(vals, 2)}
        else:
            project_area = Project.objects.filter(uid=obj.uid).annotate(
                area=Area('geom')
            ).values_list('area', flat=True).first()
            vals = project_area.sq_m if project_area else 0
            return {'क्षेत्र चौ.मी': round(vals, 2)}

    def get_district(self, obj):
        d = self._get_fk(District, obj.uid)
        if d: return {'name_m': d.name_m, 'name': d.name}
        return None

    def get_taluka(self, obj):
        d = self._get_fk(District, obj.uid)
        t = self._get_fk(Taluka, d.uid) if d else None
        if t: return {'name_m': t.name_m, 'name': t.name}
        return None

    def get_village(self, obj):
        d = self._get_fk(District, obj.uid)
        t = self._get_fk(Taluka, d.uid) if d else None
        v = self._get_fk(Village, t.uid) if t else None
        if v: return {'name_m': v.name_m, 'name': v.name}
        return None

    def get_gut_count(self, obj):
        d = self._get_fk(District, obj.uid)
        t = self._get_fk(Taluka, d.uid) if d else None
        v = self._get_fk(Village, t.uid) if t else None
        return Gut.objects.filter(fid=v.uid).count() if v else 0

    def get_bund_acquiretype_counts(self, obj):
        d = self._get_fk(District, obj.uid)
        t = self._get_fk(Taluka, d.uid) if d else None
        v = self._get_fk(Village, t.uid) if t else None
        guts = Gut.objects.filter(fid=v.uid) if v else Gut.objects.none()
        return (Bund.objects
                .filter(fid__in=guts.values_list('uid', flat=True))
                .values('acquiretype')
                .annotate(count=Count('id')))

    def get_bund_ownertype_counts(self, obj):
        d = self._get_fk(District, obj.uid)
        t = self._get_fk(Taluka, d.uid) if d else None
        v = self._get_fk(Village, t.uid) if t else None
        guts = Gut.objects.filter(fid=v.uid) if v else Gut.objects.none()
        return (Bund.objects
                .filter(fid__in=guts.values_list('uid', flat=True))
                .values('ownertype')
                .annotate(count=Count('id')))
