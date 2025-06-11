

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project
from .serializers import projects

class ProjectListView(APIView):
    def get(self, request):
        self.projectlists = Project.objects.all()
        self.serializer = projects.ProjectSerializer(self.projectlists, many=True)
        # print(serializer.data.uid)
        from django.contrib.gis.db.models.functions import Transform

        districts = Project.objects.annotate(geom_wgs=Transform('geom', 4326))
        
        # datas = []
        for d in districts:
            d.geom_wgs
        return Response(self.serializer.data )





from .models import District
from .serializers import projects
from rest_framework import status

class DistrictListView(APIView):
    def get(self, request):
        self.fid = request.query_params.get('fid')
        if self.fid:
            self.districts = District.objects.filter(fid__uid=self.fid)
        else:
            self.districts = District.objects.all()
        self.serializer = projects.DistrictSerializer(self.districts, many=True)

        
        return Response(self.serializer.data, status=status.HTTP_200_OK)


from .models import Taluka


class TalukaListView(APIView):
    def get(self, request):
        project_name = request.query_params.get('project')
        district_name = request.query_params.get('district')

        talukas = Taluka.objects.all()

        if project_name:
            talukas = talukas.filter(fid__fid__name=project_name)

        if district_name:
            talukas = talukas.filter(fid__name_m=district_name)

        serializer = projects.TalukaSerializer(talukas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from .models import Village

class VillageListView(APIView):
    def get(self, request):

        project_name = request.query_params.get('project')
        district_name = request.query_params.get('district')
        taluka_name = request.query_params.get('taluka')

        villages = Village.objects.all()

        if project_name:
            villages = villages.filter(fid__fid__fid__name=project_name)

        if district_name:
            villages = villages.filter(fid__fid__name_m=district_name)

        if taluka_name:
            villages = villages.filter(fid__name_m=taluka_name)

        serializer = projects.VillageSerializer(villages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from .models import Gut

class GutListView(APIView):
    def get(self, request):
        gut_name = request.query_params.get('village')
        project_name = request.query_params.get('project')
        district_name = request.query_params.get('district')
        taluka_name = request.query_params.get('taluka')
        guts = Gut.objects.all()

        if project_name:
            guts = guts.filter(fid__fid__fid__fid__name=project_name)

        if district_name:
            guts = guts.filter(fid__fid__fid__name_m=district_name)

        if taluka_name:
            guts = guts.filter(fid__fid__name_m=taluka_name)
        if gut_name:
            guts = guts.filter(fid__name_m=gut_name)

        serializer = projects.GutSerializer(guts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Gut
from .serializers import projects as pps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import GEOSGeometry
from .models import Gut, Bund
import json
from django.db.models import Q
# from django.contrib.gis.geos import GEOSGeometry


# Put this at the top of your views.py or in a separate config file
PROPERTY_CONFIG = {
    'acquire_type': {
        'field': 'acquiretype',
        'heading': 'भूसंपादन स्थिती',
        'source': 'bund',
        'type': 'str',
        'filterable': True

    },
    'ownership': {
        'field': 'ownertype',
        'heading': 'मालकी हक्क',
        'source': 'bund',
        'type': 'str',
        'filterable': True
    },
    'permission_type': {
        'field': 'permtype',
        'heading': 'परवानगी प्रकार',
        'source': 'bund',
        'type': 'str',
        'filterable': True 
    },
    'gut_no': {
        'field': 'name_m',
        'heading': 'गट क्रमांक',
        'source': 'gut',
        'type': 'str',
        'filterable': True 
    },
    'land_owner_name': {
        'field': 'name_m',
        'heading': 'जमीन मालकाचे नाव',
        'source': 'bund',
        'type': 'str',
        'filterable': True 
    },
    'village': {
        'field': 'name_m',
        'heading': 'गाव',
        'source': 'gut.fid',
        'type': 'str',
        'filterable': True 
    },
    'district': {
        'field': 'name_m',
        'heading': 'जिल्हा',
        'source': 'gut.fid.fid.fid',
        'type': 'str',
        'filterable': True 
    },
    'taluka': {
        'field': 'name_m',
        'heading': 'तालुका',
        'source': 'gut.fid.fid',
        'type': 'str' ,
        'filterable': True
    },
    'project': {
        'field': 'name',
        'heading': 'प्रकल्प',
        'source': 'gut.fid.fid.fid.fid',
        'type': 'str',
        'filterable': True
    },
    # Add new properties here as needed
    'sdolandtype': {
        'field': 'sdolandtype',
        'heading': 'एकूण क्षेत्रफळ',
        'source': 'bund',
        'type': 'str',
        'filterable': True
    },
    'name': {
        'field': 'name',
        'heading': 'नाव',
        'source': 'bund',
        'type': 'str',
        'filterable': True
    },
     'taxlandtype': {
        'field': 'taxlandtype',
        'heading': 'कर भू प्रकार',
        'source': 'bund',
        'type': 'str',
        'filterable': True 
    },
    'totaltax': {
        'field': 'totaltax',
        'heading': 'एकूण कर',
        'source': 'bund',
        'type': 'float',
        'filterable': True
    },
    'totalgutarea': {
        'field': 'totalgutarea',
        'heading': 'एकूण कर',
        'source': 'bund',
        'type': 'float',
        'filterable': True 
    }
    
}

class GutStatusView(APIView):
    def get(self, request):
        # 1. Validate mandatory parameters
        mandatory_params = {
            'project': request.query_params.get('project'),
            'district': request.query_params.get('district'),
            'taluka': request.query_params.get('taluka'),
            'village': request.query_params.get('village')
        }
        
        missing_params = [k for k, v in mandatory_params.items() if not v]
        if missing_params:
            return Response(
                {"error": f"Missing mandatory parameters: {', '.join(missing_params)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Extract all other filter parameters
        other_filters = {}
        for param, value in request.query_params.items():
            if param not in mandatory_params and param in PROPERTY_CONFIG:
                # Handle multiple values for the same parameter
                if ',' in value:
                    other_filters[param] = value.split(',')
                else:
                    other_filters[param] = [value]

        # 3. Build and execute query
        queryset = self._build_queryset(mandatory_params, other_filters)
        
        # 4. Process data and build response
        features, filter_values = self._process_queryset(queryset)
        
        return Response({
            "Filters": self._build_filters(filter_values),
            "Features": features
        })

    def _build_queryset(self, mandatory_params, other_filters):
        """Build queryset with mandatory and optional filters"""
        # Base queryset with mandatory hierarchical filters
        queryset = Gut.objects.filter(
            fid__name_m=mandatory_params['village'],
            fid__fid__name_m=mandatory_params['taluka'],
            fid__fid__fid__name_m=mandatory_params['district'],
            fid__fid__fid__fid__name=mandatory_params['project']
        ).select_related(
            'fid__fid__fid__fid',
            'fid__fid__fid',
            'fid__fid',
            'fid'
        ).prefetch_related('bund_set')

        # Apply additional property filters with multiple value support
        for prop, values in other_filters.items():
            config = PROPERTY_CONFIG[prop]
            
            # Build OR conditions for multiple values
            if config['source'] == 'bund':
                query = Q()
                for value in values:
                    query |= Q(**{f"bund__{config['field']}": value})
                queryset = queryset.filter(query)
            else:
                field_path = config['source'].replace('gut.', '').replace('.', '__')
                if field_path:
                    field_path += f'__{config["field"]}'
                else:
                    field_path = config['field']
                
                query = Q()
                for value in values:
                    query |= Q(**{field_path: value})
                queryset = queryset.filter(query)

        return queryset.distinct()
    
    def _process_queryset(self, queryset):
        """Process the queryset to extract features and filter values"""
        features = []
        filter_values = {key: set() for key in PROPERTY_CONFIG.keys()}

        for gut in queryset:
            for bund in gut.bund_set.all():
                properties = {}
                
                # Build properties dynamically
                for prop_key, config in PROPERTY_CONFIG.items():
                    value = self._get_property_value(gut, bund, config)
                    properties[prop_key] = value
                    if value != "":  # Skip empty values for filters
                        filter_values[prop_key].add(value)
                
                # Handle geometry
                geom = self._get_geometry(bund)
                
                features.append({
                    "geom": geom,
                    "properties": properties
                })
        
        return features, filter_values

    def _get_property_value(self, gut, bund, config):
        """Extract and properly format a property value"""
        try:
            # Get raw value
            if config['source'] == 'bund':
                raw_value = getattr(bund, config['field'], None)
            else:  # gut or gut.relationship
                obj = gut
                for part in config['source'].split('.')[1:]:  # skip 'gut' part
                    obj = getattr(obj, part, None)
                    if obj is None:
                        break
                raw_value = getattr(obj, config['field'], None) if obj else None
            
            # Convert based on type
            if raw_value is None:
                return ""
            
            if config['type'] == 'int':
                return int(float(raw_value))  # Handle string numbers
            elif config['type'] == 'float':
                return float(raw_value)
            return str(raw_value)
            
        except (ValueError, TypeError, AttributeError):
            return str(raw_value) if raw_value is not None else ""

    def _get_geometry(self, bund):
        """Extract and transform geometry"""
        if bund.geom:
            try:
                wgs84_geom = bund.geom.transform(4326, clone=True)
                return json.loads(wgs84_geom.geojson)
            except Exception:
                return {}
        return {}

    def _build_filters(self, filter_values):
        """Build the filters section with proper sorting"""
        filters = []
        for key, config in PROPERTY_CONFIG.items():
            if not config.get('filterable', True):
                continue
                
            values = filter_values[key]
            clean_values = [v for v in values if v != ""]
            
            # Type-specific sorting
            if config['type'] == 'int':
                sorted_values = sorted(clean_values, key=lambda x: int(x))
            elif config['type'] == 'float':
                sorted_values = sorted(clean_values, key=lambda x: float(x))
            else:  # str
                sorted_values = sorted(clean_values, key=lambda x: str(x).lower())
            
            filters.append({
                "key": key,
                "heading": config['heading'],
                "values": sorted_values,
                # "type": config['type']  # Uncomment if frontend needs type info
            })
        return filters


from .serializers import projects
class MainStats(APIView):
    def get(self, request):
        project_id = request.query_params.get('uid')
        district_name = request.query_params.get('district')
        # taluka_name = request.query_params.get('taluka')
        # village_name = request.query_params.get('village')

        queryset = Project.objects.all()

        if project_id:
            queryset = queryset.filter(uid=project_id)

        if district_name:
            districts = District.objects.filter(name__icontains=district_name)
            # queryset = queryset.filter(uid__in=[d.fid.uid for d in districts])
        #
        # if taluka_name:
        #     talukas = Taluka.objects.filter(name__icontains=taluka_name)
        #     queryset = queryset.filter(uid__in=[t.fid.fid.uid for t in talukas])
        #
        # if village_name:
        #     villages = Village.objects.filter(name__icontains=village_name)
        #     queryset = queryset.filter(uid__in=[v.fid.fid.fid.uid for v in villages])

        serializer = projects.MainStatsSerializer(districts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






# class GutStatusView(APIView):
#     def get(self, request):
#         # 1. Initialize and apply filters
#         query_filters = self._build_query_filters(request)
#         queryset = self._get_filtered_queryset(query_filters)
        
#         # 2. Process data
#         features, filter_values = self._process_queryset(queryset)
        
#         # 3. Build response
#         response_data = {
#             "Filters": self._build_filters(filter_values),
#             "Features": features
#         }
        
#         return Response(response_data)

#     def _build_query_filters(self, request):
#         """Extract and validate filters from request parameters"""
#         filters = {}
#         for param in request.query_params:
#             if param in PROPERTY_CONFIG and PROPERTY_CONFIG[param].get('filterable', True):
#                 filters[param] = request.query_params[param]
#         return filters

#     def _get_filtered_queryset(self, filters):
#         """Apply filters to the base queryset"""
#         queryset = Gut.objects.select_related(
#             'fid__fid__fid__fid',
#             'fid__fid__fid',
#             'fid__fid',
#             'fid'
#         ).prefetch_related('bund_set')

#         query = Q()
#         for key, value in filters.items():
#             config = PROPERTY_CONFIG[key]
#             if config['source'] == 'bund':
#                 # For bund fields, we need to filter through the related set
#                 queryset = queryset.filter(bund__**{config['field']: value})
#             else:
#                 # For gut fields (including relationships)
#                 field_path = config['source'].replace('gut.', '').replace('.', '__')
#                 if field_path:
#                     field_path += f'__{config["field"]}'
#                 else:
#                     field_path = config['field']
#                 queryset = queryset.filter(**{field_path: value})

#         return queryset.distinct()

#     def _process_queryset(self, queryset):
#         """Process the queryset to extract features and filter values"""
#         features = []
#         filter_values = {key: set() for key in PROPERTY_CONFIG.keys()}

#         for gut in queryset:
#             for bund in gut.bund_set.all():
#                 properties = {}
                
#                 # Build properties dynamically
#                 for prop_key, config in PROPERTY_CONFIG.items():
#                     value = self._get_property_value(gut, bund, config)
#                     properties[prop_key] = value
#                     if value != "":  # Skip empty values for filters
#                         filter_values[prop_key].add(value)
                
#                 # Handle geometry
#                 geom = self._get_geometry(bund)
                
#                 features.append({
#                     "geom": geom,
#                     "properties": properties
#                 })
        
#         return features, filter_values

#     def _get_property_value(self, gut, bund, config):
#         """Extract and properly format a property value"""
#         try:
#             # Get raw value
#             if config['source'] == 'bund':
#                 raw_value = getattr(bund, config['field'], None)
#             else:  # gut or gut.relationship
#                 obj = gut
#                 for part in config['source'].split('.')[1:]:  # skip 'gut' part
#                     obj = getattr(obj, part, None)
#                     if obj is None:
#                         break
#                 raw_value = getattr(obj, config['field'], None) if obj else None
            
#             # Convert based on type
#             if raw_value is None:
#                 return ""
            
#             if config['type'] == 'int':
#                 return int(float(raw_value))  # Handle string numbers
#             elif config['type'] == 'float':
#                 return float(raw_value)
#             return str(raw_value)
            
#         except (ValueError, TypeError, AttributeError):
#             return str(raw_value) if raw_value is not None else ""

#     def _get_geometry(self, bund):
#         """Extract and transform geometry"""
#         if bund.geom:
#             try:
#                 wgs84_geom = bund.geom.transform(4326, clone=True)
#                 return json.loads(wgs84_geom.geojson)
#             except Exception:
#                 return {}
#         return {}

#     def _build_filters(self, filter_values):
#         """Build the filters section with proper sorting"""
#         filters = []
#         for key, config in PROPERTY_CONFIG.items():
#             if not config.get('filterable', True):
#                 continue
                
#             values = filter_values[key]
#             clean_values = [v for v in values if v != ""]
            
#             # Type-specific sorting
#             if config['type'] == 'int':
#                 sorted_values = sorted(clean_values, key=lambda x: int(x))
#             elif config['type'] == 'float':
#                 sorted_values = sorted(clean_values, key=lambda x: float(x))
#             else:  # str
#                 sorted_values = sorted(clean_values, key=lambda x: str(x).lower())
            
#             filters.append({
#                 "key": key,
#                 "heading": config['heading'],
#                 "values": sorted_values,
#                 # "type": config['type']  # Uncomment if frontend needs type info
#             })
#         return filters


# class GutStatusView(APIView):
#     def get(self, request):
#         # Initialize filters from request parameters
#         filters = {key: request.query_params.get(key) 
#                   for key in PROPERTY_CONFIG.keys() 
#                   if request.query_params.get(key)}
        
#         # Start with all guts and prefetch related bunds
#         guts = Gut.objects.select_related(
#             'fid__fid__fid__fid',
#             'fid__fid__fid',
#             'fid__fid',
#             'fid'
#         ).prefetch_related('bund_set')

#         # Apply filters dynamically
#         for filter_key, filter_value in filters.items():
#             config = PROPERTY_CONFIG[filter_key]
#             if config['source'].startswith('gut'):
#                 # Build the field lookup path
#                 field_path = config['source'].replace('gut.', '')
#                 if field_path:  # if there's a relationship path
#                     field_path = field_path.replace('.', '__') + '__' + config['field']
#                 else:  # direct field on gut
#                     field_path = config['field']
#                 guts = guts.filter(**{field_path: filter_value})

#         # Initialize response data
#         response_data = {
#             "Filters": [],
#             "Features": []
#         }

#         # Initialize filter values collections
#         filter_values = {key: set() for key in PROPERTY_CONFIG.keys()}

#         # Process each gut and its bunds
#         for gut in guts:
#             for bund in gut.bund_set.all():
#                 properties = {}
#                 for prop_key, config in PROPERTY_CONFIG.items():
#                     # Get raw value
#                     if config['source'] == 'bund':
#                         raw_value = getattr(bund, config['field'], None)
#                     elif config['source'].startswith('gut'):
#                         obj = gut
#                         for part in config['source'].split('.')[1:]:
#                             obj = getattr(obj, part, None)
#                             if obj is None:
#                                 break
#                         raw_value = getattr(obj, config['field'], None) if obj else None
#                     else:
#                         raw_value = None

#                     # Convert based on type
#                     if raw_value is None:
#                         value = ""
#                     else:
#                         try:
#                             if config['type'] == 'int':
#                                 value = int(float(raw_value))  # Handle cases where DB returns string
#                             elif config['type'] == 'float':
#                                 value = float(raw_value)
#                             else:  # str or default
#                                 value = str(raw_value)
#                         except (ValueError, TypeError):
#                             value = str(raw_value)  # Fallback to string if conversion fails

#                     properties[prop_key] = value
#                     filter_values[prop_key].add(value)


#                 # Transform geometry
#                 bund_geom = bund.geom.transform(4326, clone=True).geojson if bund.geom else None

#                 # Create feature
#                 feature = {
#                     "geom": json.loads(bund_geom) if bund_geom else {},
#                     "properties": properties
#                 }
#                 response_data["Features"].append(feature)

#         # Build Filters section dynamically
#         response_data["Filters"] = []
#         for key, config in PROPERTY_CONFIG.items():
#             values = filter_values[key]
            
#             # Remove empty strings if they exist
#             clean_values = {v for v in values if v != ""}
            
#             # Sort based on type
#             if config['type'] == 'int':
#                 sorted_values = sorted(clean_values, key=lambda x: int(x))
#             elif config['type'] == 'float':
#                 sorted_values = sorted(clean_values, key=lambda x: float(x))
#             else:  # str
#                 sorted_values = sorted(clean_values, key=lambda x: str(x).lower())
            
#             response_data["Filters"].append({
#                 "key": key,
#                 "heading": config['heading'],
#                 "values": sorted_values,
#                 "type": config['type']  # Optional: include type in response if needed
#             })

#         return Response(response_data)
    

# class GutStatusView(APIView):
#     def get(self, request):
#         # Get all filter parameters
#         filters = {
#             'village': request.query_params.get('village'),
#             'project': request.query_params.get('project'),
#             'district': request.query_params.get('district'),
#             'taluka': request.query_params.get('taluka'),
#             'owner_name': request.query_params.get('owner_name'),
#             'acquire_type': request.query_params.get('acquire_type'),
#             'ownership': request.query_params.get('ownership'),
#             'permission_type': request.query_params.get('permission_type'),
#             # 'malmatta': request.query_params.get('malmatta'),
#             # 'utility_type': request.query_params.get('utility_type')
#         }

#         # Start with all guts and prefetch related bunds
#         guts = Gut.objects.select_related(
#             'fid__fid__fid__fid',
#             'fid__fid__fid',
#             'fid__fid',
#             'fid'
#         ).prefetch_related('bund_set')

#         # Apply filters
#         if filters['project']:
#             guts = guts.filter(fid__fid__fid__fid__name=filters['project'])
#         if filters['district']:
#             guts = guts.filter(fid__fid__fid__name_m=filters['district'])
#         if filters['taluka']:
#             guts = guts.filter(fid__fid__name_m=filters['taluka'])
#         if filters['village']:
#             guts = guts.filter(fid__name_m=filters['village'])
#         # if filters['owner_name']:
#         #     guts = guts.filter(name_m=filters['owner_name'])

#         # Initialize response data structure
#         response_data = {
#             "Filters": [],
#             "Features": []
#         }

#         # Collections for filter values
#         filter_values = {
#             'acquire_type': set(),
#             'ownership': set(),
#             'permission_type': set(),
#             'gut_no': set(),
#             'land_owner_name': set(),
#             # 'malmatta': set(),
#             # 'utility_type': set(),
#             'village': set(),
#             'district': set(),
#             'taluka': set(),
#             'project': set()
#         }

#         # Process each gut and its bunds
#         for gut in guts:
#             # Collect filter values from gut
#             filter_values['gut_no'].add(gut.name_m)
#             filter_values['village'].add(gut.fid.name_m if gut.fid else '')
#             filter_values['district'].add(gut.fid.fid.fid.name_m if gut.fid and gut.fid.fid and gut.fid.fid.fid else '')
#             filter_values['project'].add(gut.fid.fid.fid.fid.name if gut.fid and gut.fid.fid and gut.fid.fid.fid and gut.fid.fid.fid.fid else '')
#             filter_values['taluka'].add(gut.fid.fid.name_m if gut.fid and gut.fid.fid else '')

#             for bund in gut.bund_set.all():
#                 # Collect filter values from bund
#                 filter_values['acquire_type'].add(bund.acquiretype or '')
#                 filter_values['ownership'].add(bund.ownertype or '')
#                 filter_values['permission_type'].add(bund.permtype or '')
#                 filter_values['land_owner_name'].add(bund.name_m or '')
#                 # filter_values['malmatta'].add(bund.malmatta or '')
#                 # filter_values['utility_type'].add(bund.utilitytype or '')

#                 # Transform geometries to WGS84
#                 gut_geom = gut.geom.transform(4326, clone=True).geojson if gut.geom else None
#                 bund_geom = bund.geom.transform(4326, clone=True).geojson if bund.geom else None

#                 # Create feature
#                 feature = {
#                     "geom": json.loads(bund_geom) if bund_geom else {},
#                     "properties": {
#                         "acquire_type": bund.acquiretype or "",
#                         "ownership": bund.ownertype or "",
#                         "permission_type": bund.permtype or "",
#                         "gut_no": gut.name_m or "",
#                         "land_owner_name": bund.name_m or "",
#                         # "Malmatta": bund.malmatta or "",
#                         # "others": bund.other or "",
#                         # "utility_type": bund.utilitytype or "",
#                         "village": gut.fid.name_m if gut.fid else "",
#                         "district": gut.fid.fid.fid.name_m if gut.fid and gut.fid.fid and gut.fid.fid.fid else "",
#                         "project": gut.fid.fid.fid.fid.name if gut.fid and gut.fid.fid and gut.fid.fid.fid and gut.fid.fid.fid.fid else "",
#                         "taluka": gut.fid.fid.name_m if gut.fid and gut.fid.fid else "",
#                     }
#                 }
#                 response_data["Features"].append(feature)

#         # Build Filters section with Marathi headings
#         response_data["Filters"] = [
#             {
#                 "key": "acquire_type",
#                 "heading": "भूसंपादन स्थिती",
#                 "values": sorted(list(filter_values['acquire_type']))
#             },
#             {
#                 "key": "ownership",
#                 "heading": "मालकी हक्क",
#                 "values": sorted(list(filter_values['ownership']))
#             },
#             {
#                 "key": "permission_type",
#                 "heading": "परवानगी प्रकार",
#                 "values": sorted(list(filter_values['permission_type']))
#             },
#             {
#                 "key": "gut_no",
#                 "heading": "गट क्रमांक",
#                 "values": sorted(list(filter_values['gut_no']))
#             },
#             {
#                 "key": "land_owner_name",
#                 "heading": "जमीन मालकाचे नाव",
#                 "values": sorted(list(filter_values['land_owner_name']))
#             },
#             # {
#             #     "key": "malmatta",
#             #     "heading": "मालमत्ता",
#             #     "values": sorted(list(filter_values['malmatta']))
#             # },
#             # {
#             #     "key": "utility_type",
#             #     "heading": "उपयुक्तता प्रकार",
#             #     "values": sorted(list(filter_values['utility_type']))
#             # },
#             {
#                 "key": "village",
#                 "heading": "गाव",
#                 "values": sorted(list(filter_values['village']))
#             },
#             {
#                 "key": "district",
#                 "heading": "जिल्हा",
#                 "values": sorted(list(filter_values['district']))
#             },
#             {
#                 "key": "taluka",
#                 "heading": "तालुका",
#                 "values": sorted(list(filter_values['taluka']))
#             },
#             {
#                 "key": "project",
#                 "heading": "प्रकल्प",
#                 "values": sorted(list(filter_values['project']))
#             }
#         ]

#         return Response(response_data)

# class GutStatusView(APIView):
#     def get(self, request):
#         # Get filter parameters
#         gut_name = request.query_params.get('village')
#         project_name = request.query_params.get('project')
#         district_name = request.query_params.get('district')
#         taluka_name = request.query_params.get('taluka')
#         owner_name = request.query_params.get('owner_name')

#         # Start with all guts
#         guts = Gut.objects.select_related(
#             'fid__fid__fid__fid',
#             'fid__fid__fid',
#             'fid__fid',
#             'fid'
#         ).prefetch_related('bund_set')

#         # Apply filters
#         if project_name:
#             guts = guts.filter(fid__fid__fid__fid__name=project_name)
#         if district_name:
#             guts = guts.filter(fid__fid__fid__name_m=district_name)
#         if taluka_name:
#             guts = guts.filter(fid__fid__name_m=taluka_name)
#         if gut_name:
#             guts = guts.filter(fid__name_m=gut_name)
#         if owner_name:
#             guts = guts.filter(name_m=owner_name)

#         # Initialize response data
#         response_data = {
#             "Filters": [],
#             "Features": []
#         }

#         # Serialize for filters
#         filter_serializer = pps.GutFilterSerializer(guts, many=True)
#         filter_data = filter_serializer.data

#         # Build Filters section
#         gut_numbers = set()
#         villages = set()
#         districts = set()
#         projects = set()
#         talukas = set()

#         for item in filter_data:
#             gut_numbers.add(item['gut_no'])
#             villages.add(item['village'])
#             districts.add(item['district'])
#             projects.add(item['project'])
#             talukas.add(item['taluka'])

#         response_data["Filters"] = [
#             {"key": "gut_no", "heading": "Gut Number", "values": list(gut_numbers)},
#             {"key": "village", "heading": "Village", "values": list(villages)},
#             {"key": "district", "heading": "District", "values": list(districts)},
#             {"key": "project", "heading": "Project", "values": list(projects)},
#             {"key": "taluka", "heading": "Taluka", "values": list(talukas)}
#         ]

#         # Serialize for features
#         for gut in guts:
#             for bund in gut.bund_set.all():
#                 feature_serializer = pps.BundFeatureSerializer(bund)
#                 feature_data = feature_serializer.data
#                 feature_data['properties']['gut_no'] = gut.name_m
#                 response_data["Features"].append(feature_data)

#         return Response(response_data)

class GutStats(APIView):
    def get(self, request):
        gut_name = request.query_params.get('village')
        project_name = request.query_params.get('project')
        district_name = request.query_params.get('district')
        taluka_name = request.query_params.get('taluka')
        owner_name = request.query_params.get('owner_name')
        print(owner_name,"llllllllllllllllllllllllllllllllll")

        guts = Gut.objects.all()

        if project_name:
            guts = guts.filter(fid__fid__fid__fid__name=project_name)

        if district_name:
            guts = guts.filter(fid__fid__fid__name_m=district_name)

        if taluka_name:
            guts = guts.filter(fid__fid__name_m=taluka_name)
        if gut_name:
            guts = guts.filter(fid__name_m=gut_name)
        if owner_name:
            guts = guts.filter(name_m=owner_name)

        serializer = projects.GutSerializer(guts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





from .serializers.distict import get_status_counts

class ProjectStatsAPIView(APIView):

    def get(self, request):
        project_id = request.GET.get('uid')
        district_name = request.GET.get('district_name')
        print(district_name,"lllllllllllllllllllll")
        taluka_name = request.GET.get('taluka_name')
        print(taluka_name)
        village_name = request.GET.get('village_name')
        gut_name = request.GET.get('gut_name')
        if project_id:
            counts = get_status_counts(
                project_id=project_id,
                district_name=district_name,
                taluka_name=taluka_name,
                village_name=village_name,
                gut_name=gut_name
            )

            return JsonResponse(counts)
        else:
            return JsonResponse("Please select a project.")

# myapp/views.py

from django.http import JsonResponse
from .tasks import slow_add

def start_task(request):
    task = slow_add.delay(3, 4)
    return JsonResponse({'task_id': task.id})

from celery.result import AsyncResult

def check_task(request, task_id):
    result = AsyncResult(task_id)
    if result.ready():
        return JsonResponse({'status': 'done', 'result': result.result})
    return JsonResponse({'status': 'pending'})
