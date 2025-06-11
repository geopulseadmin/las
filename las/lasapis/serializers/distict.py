from django.db.models import Count, Sum
from django.db.models import Sum
from ..models import Project, District, Taluka, Village, Gut, Bund


def format_indian_currency(value):
    """
    Convert a numeric value to Indian currency format with units (Cr, Lakh, etc.)
    Example: 180860770.1060 → "₹18.09 Cr" or "₹18,08,60,770"
    """
    value = round(float(value), 2)

    # For values >= 1 Crore (1,00,00,000)
    if abs(value) >= 10000000:
        cr = round(value / 10000000, 2)
        return f"₹{cr:,} Cr"

    # For values >= 1 Lakh (1,00,000)
    elif abs(value) >= 100000:
        lakh = round(value / 100000, 2)
        return f"₹{lakh:,} Lakh"
    # For values >= 1 Thousand (1,000)
    elif abs(value) >= 1000:
        thousand = round(value / 1000, 2)
        return f"₹{thousand:,} K"

    # For smaller values
    else:
        return f"₹{value:,.2f}"





from rest_framework_gis.serializers import GeoModelSerializer
from rest_framework import serializers
from django.contrib.gis.db.models.functions import Length, Area
from ..models import Project, Centreline
from django.db.models import Count

from django.contrib.gis.db.models.functions import Length, Area, Intersection
from django.db.models import Sum, Count, F
from django.contrib.gis.measure import D  # for distance conversion


# def get_length_or_area(obj, filters):
#     """
#     Calculate length or area based on applied filters
#     """
#     # Get the base queryset for centerlines/projects
#     centreline_qs = Centreline.objects.filter(fid=obj.uid)
#     project_qs = Project.objects.filter(uid=obj.uid)
#
#     # Apply the same filters to geometries as were applied to bunds/guts
#     if filters.get('gut_name'):
#         centreline_qs = centreline_qs.filter(fid__name_m=filters['gut_name'])
#         project_qs = project_qs.filter(fid__fid__fid__fid__name_m=filters['gut_name'])
#
#     if filters.get('village_name'):
#         centreline_qs = centreline_qs.filter(fid__fid__name_m=filters['village_name'])
#         project_qs = project_qs.filter(fid__fid__fid__name_m=filters['village_name'])
#
#     if filters.get('taluka_name'):
#         centreline_qs = centreline_qs.filter(fid__fid__fid__name_m=filters['taluka_name'])
#         project_qs = project_qs.filter(fid__fid__name_m=filters['taluka_name'])
#
#     if filters.get('district_name'):
#         centreline_qs = centreline_qs.filter(fid__fid__fid__fid__name_m=filters['district_name'])
#         project_qs = project_qs.filter(fid__name_m=filters['district_name'])
#
#     if filters.get('project_id'):
#         centreline_qs = centreline_qs.filter(fid__fid__fid__fid__fid__uid=filters['project_id'])
#         project_qs = project_qs.filter(uid=filters['project_id'])
#
#     # Calculate length if centerlines exist, otherwise calculate area
#     if centreline_qs.exists():
#         # Get intersection with filtered area if any filter is applied
#         if any(filters.values()):
#             # Get the first bund's geometry that matches the filters
#             reference_geom = Bund.objects.filter(
#                 fid__fid__fid__fid__fid__uid=obj.uid
#             ).first().geom
#
#             # Calculate length of intersection
#             total_length = centreline_qs.annotate(
#                 intersected_length=Length(Intersection('geom', reference_geom))
#             ).aggregate(total=Sum('intersected_length'))['total']
#         else:
#             # Calculate full length if no filters
#             total_length = centreline_qs.annotate(
#                 length=Length('geom')
#             ).aggregate(total=Sum('length'))['total']
#
#         vals = total_length.m if total_length else 0
#         return {'लांबी (मी)': round(vals, 2)}
#     else:
#         # Calculate area for projects
#         if any(filters.values()):
#             # Get intersection with filtered area
#             reference_geom = Project.objects.filter(
#                 uid=filters.get('project_id', obj.uid)
#             ).first().geom
#
#             total_area = project_qs.annotate(
#                 intersected_area=Area(Intersection('geom', reference_geom))
#             ).aggregate(total=Sum('intersected_area'))['total']
#         else:
#             # Calculate full area if no filters
#             total_area = project_qs.annotate(
#                 area=Area('geom')
#             ).aggregate(total=Sum('area'))['total']
#
#         vals = total_area.sq_m if total_area else 0
#         return {'क्षेत्र चौ.मी': round(vals, 2)}

# def get_length_or_area(self, obj):
#     centreline_qs = Centreline.objects.filter(fid=obj.uid)
#     if centreline_qs.exists():
#         total_length = centreline_qs.annotate(
#             length=Length('geom')
#         ).aggregate(total=serializers.models.Sum('length'))['total']
#         vals = total_length.m if total_length else 0
#         return {'लांबी (मी)': round(vals, 2)}
#     else:
#         project_area = Project.objects.filter(uid=obj.uid).annotate(
#             area=Area('geom')
#         ).values_list('area', flat=True).first()
#         vals = project_area.sq_m if project_area else 0
#         return {'क्षेत्र चौ.मी': round(vals, 2)}


# def get_length_or_area(obj, filters):
#     """
#     Calculate length or area based on applied filters, using correct model relationships
#     """
#     # Get the base queryset for centerlines/projects
#     centreline_qs = Centreline.objects.filter(fid=obj.uid)
#     project_qs = Project.objects.filter(uid=obj.uid)
#
#     # Apply filters based on the actual model relationships
#     if filters.get('gut_name'):
#         # Centreline -> Project (no direct Gut relationship)
#         # Need to find Bunds with this gut name, then their Project
#         project_ids = Bund.objects.filter(
#             fid__name_m=filters['gut_name']
#         ).values_list('fid__fid__fid__fid__uid', flat=True).distinct()
#
#         centreline_qs = centreline_qs.filter(fid__uid__in=project_ids)
#         project_qs = project_qs.filter(uid__in=project_ids)
#
#     if filters.get('village_name'):
#         # Centreline -> Project <- District <- Taluka <- Village
#         project_ids = Village.objects.filter(
#             name_m=filters['village_name']
#         ).values_list('fid__fid__fid__uid', flat=True).distinct()
#
#         centreline_qs = centreline_qs.filter(fid__uid__in=project_ids)
#         project_qs = project_qs.filter(uid__in=project_ids)
#
#     if filters.get('taluka_name'):
#         # Centreline -> Project <- District <- Taluka
#         project_ids = Taluka.objects.filter(
#             name_m=filters['taluka_name']
#         ).values_list('fid__fid__uid', flat=True).distinct()
#
#         centreline_qs = centreline_qs.filter(fid__uid__in=project_ids)
#         project_qs = project_qs.filter(uid__in=project_ids)
#
#     if filters.get('district_name'):
#         # Centreline -> Project <- District
#         project_ids = District.objects.filter(
#             name_m=filters['district_name']
#         ).values_list('fid__uid', flat=True).distinct()
#
#         centreline_qs = centreline_qs.filter(fid__uid__in=project_ids)
#         project_qs = project_qs.filter(uid__in=project_ids)
#
#     if filters.get('project_id'):
#         centreline_qs = centreline_qs.filter(fid__uid=filters['project_id'])
#         project_qs = project_qs.filter(uid=filters['project_id'])
#
#     # Calculate length if centerlines exist, otherwise calculate area
#     if centreline_qs.exists():
#         # Calculate full length (no intersection needed since we filtered already)
#         total_length = centreline_qs.annotate(
#             length=Length('geom')
#         ).aggregate(total=Sum('length'))['total']
#
#         vals = total_length.m if total_length else 0
#         return {'लांबी (मी)': round(vals, 2)}
#     else:
#         # Calculate full area (no intersection needed since we filtered already)
#         total_area = project_qs.annotate(
#             area=Area('geom')
#         ).aggregate(total=Sum('area'))['total']
#
#         vals = total_area.sq_m if total_area else 0
#         return {'क्षेत्र चौ.मी': round(vals, 2)}
#
#

from django.contrib.gis.db.models.functions import Intersection, Area, Length, Transform

#
# def get_length_or_area(obj, filters):
#     """
#     Calculate length or area by intersecting with the filtered administrative boundary
#     """
#     # Get the base geometries
#     centreline_qs = Centreline.objects.filter(fid=obj.uid)
#     project_qs = Project.objects.filter(uid=obj.uid)
#
#     # Determine which administrative boundary to use for intersection
#     boundary_geom = None
#
#     if filters.get('gut_name'):
#         boundary = Gut.objects.filter(name_m=filters['gut_name']).first()
#         if boundary:
#             boundary_geom = boundary.geom
#     elif filters.get('village_name'):
#         boundary = Village.objects.filter(name_m=filters['village_name']).first()
#         if boundary:
#             boundary_geom = boundary.geom
#     elif filters.get('taluka_name'):
#         boundary = Taluka.objects.filter(name_m=filters['taluka_name']).first()
#         if boundary:
#             boundary_geom = boundary.geom
#     elif filters.get('district_name'):
#         boundary = District.objects.filter(name_m=filters['district_name']).first()
#         if boundary:
#             boundary_geom = boundary.geom
#
#     # Calculate length if centerlines exist, otherwise calculate area
#     if centreline_qs.exists():
#         if boundary_geom:
#             print("heheheheheheeh")
#             # Calculate length of intersection with boundary
#             total_length = centreline_qs.annotate(
#                 intersected_geom=Transform(Intersection('geom', boundary_geom),srid=32643)
#             ).annotate(
#                 length=Length('intersected_geom')
#             ).aggregate(total=Sum('length'))['total']
#             print(total_length,"total length")
#         else:
#             # Calculate full length if no boundary filter
#             total_length = centreline_qs.annotate(
#                 length=Length('geom')
#             ).aggregate(total=Sum('length'))['total']
#
#         vals = total_length.m if total_length else 0
#         return {'लांबी (मी)': round(vals, 2)}
#     else:
#         if boundary_geom:
#             # Calculate area of intersection with boundary
#             total_area = project_qs.annotate(
#                 intersected_geom=Transform(Intersection('geom', boundary_geom),srid=32643)
#             ).annotate(
#                 area=Area('intersected_geom')
#             ).aggregate(total=Sum('area'))['total']
#         else:
#             # Calculate full area if no boundary filter
#             total_area = project_qs.annotate(
#                 area=Area('geom')
#             ).aggregate(total=Sum('area'))['total']
#
#         vals = total_area.sq_m if total_area else 0
#         return {'क्षेत्र चौ.मी': round(vals, 2)}


from django.contrib.gis.db.models.functions import Intersection, Area, Length, Transform

#
# def get_length_or_area(obj, filters):
#     """
#     Calculate length or area by intersecting with the filtered administrative boundary
#     with proper SRID handling
#     """
#     # Target SRID (use either 32643 or 4326 consistently)
#     TARGET_SRID = 32643  # or 4326 if that's your preferred system
#
#     # Get the base geometries
#     centreline_qs = Centreline.objects.filter(fid=obj.uid)
#     project_qs = Project.objects.filter(uid=obj.uid)
#
#     # Determine which administrative boundary to use for intersection
#     boundary_geom = None
#
#     if filters.get('gut_name'):
#         boundary = Gut.objects.filter(name_m=filters['gut_name']).first()
#     elif filters.get('village_name'):
#         boundary = Village.objects.filter(name_m=filters['village_name']).first()
#     elif filters.get('taluka_name'):
#         boundary = Taluka.objects.filter(name_m=filters['taluka_name']).first()
#     elif filters.get('district_name'):
#         boundary = District.objects.filter(name_m=filters['district_name']).first()
#     # elif filters.get('uid'):
#     #     # print("kkkkkkkkkkkkkkkk")
#     #     boundary = Project.objects.filter(uid=filters['uid']).first()
#     if not (boundary):
#         print("yyyyyyyyyyyyyyyyyyyyyyyyyy")
#         boundary = project_qs
#
#     if boundary:
#         # Transform boundary to target SRID if needed
#         boundary_geom = Transform(boundary.geom, TARGET_SRID)
#
#     # Calculate length if centerlines exist, otherwise calculate area
#     if centreline_qs.exists():
#         print("heheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
#         if boundary_geom:
#             total_length = centreline_qs.annotate(
#                 transformed_geom=Transform('geom', TARGET_SRID),
#                 intersected_geom=Intersection('transformed_geom', boundary_geom)
#             ).annotate(
#                 length=Length('intersected_geom')
#             ).aggregate(total=Sum('length'))['total']
#
#             if total_length:
#                 # Convert to km if >= 1000 meters, otherwise keep in meters
#                 if total_length.m >= 1000:
#                     km_value = total_length.m / 1000
#                     # Round to 2 decimal places for km
#                     return {'लांबी': f"{round(km_value, 2)} किमी"}
#                 else:
#                     # Round to 2 decimal places for meters
#                     return {'लांबी': f"{round(total_length.m, 2)} मी"}
#             else:
#                 return {'लांबी': "0 मी"}
#         else:
#             total_length = centreline_qs.annotate(
#                 transformed_geom=Transform('geom', TARGET_SRID)
#             ).annotate(
#                 length=Length('transformed_geom')
#             ).aggregate(total=Sum('length'))['total']
#
#         vals = total_length.m if total_length else 0
#         return {'लांबी (मी)': round(vals, 2)}
#     else:
#         if boundary_geom:
#             print("hehpppppppppppppppppppppppppppppppppppppppppppppppppppppp")
#             total_area = project_qs.annotate(
#                 transformed_geom=Transform('geom', TARGET_SRID),
#                 intersected_geom=Intersection('transformed_geom', boundary_geom)
#             ).annotate(
#                 area=Area('intersected_geom')
#             ).aggregate(total=Sum('area'))['total']
#         else:
#             total_area = project_qs.annotate(
#                 transformed_geom=Transform('geom', TARGET_SRID)
#             ).annotate(
#                 area=Area('transformed_geom')
#             ).aggregate(total=Sum('area'))['total']
#
#         vals = total_area.sq_m if total_area else 0
#         return {'क्षेत्र चौ.मी': round(vals, 2)}
#


def get_length_or_area(obj, filters):
    """
    Calculate length or area by intersecting with the filtered administrative boundary
    with proper SRID handling and automatic unit conversion
    """
    TARGET_SRID = 32643  # UTM Zone 43N

    # Initialize boundary as None
    boundary = None

    # Determine which administrative boundary to use for intersection
    if filters.get('gut_name'):
        boundary = Gut.objects.filter(name_m=filters['gut_name']).first()
    elif filters.get('village_name'):
        boundary = Village.objects.filter(name_m=filters['village_name']).first()
    elif filters.get('taluka_name'):
        boundary = Taluka.objects.filter(name_m=filters['taluka_name']).first()
    elif filters.get('district_name'):
        boundary = District.objects.filter(name_m=filters['district_name']).first()
    elif filters.get('uid'):
        boundary = Project.objects.filter(uid=filters['uid']).first()

    # Get boundary geometry if exists
    boundary_geom = Transform(boundary.geom, TARGET_SRID) if boundary else None

    # Base querysets
    centreline_qs = Centreline.objects.filter(fid=obj.uid)
    project_qs = Project.objects.filter(uid=obj.uid)

    # Helper functions for formatting
    def format_length(meters):
        if meters >= 1000:
            return f"{round(meters / 1000, 2)} किमी"
        return f"{round(meters, 2)} मी"

    def format_area(sq_meters):
        if sq_meters >= 10000:  # 1 hectare = 10000 sqm
            return f"{round(sq_meters / 10000, 2)} हेक्टर"
        return f"{round(sq_meters, 2)} चौ.मी"

    # Calculate length if centerlines exist
    if centreline_qs.exists():
        if boundary_geom:
            total_length = centreline_qs.annotate(
                transformed_geom=Transform('geom', TARGET_SRID),
                intersected_geom=Intersection('transformed_geom', boundary_geom),
                length=Length('intersected_geom')
            ).aggregate(total=Sum('length'))['total']
        else:
            total_length = centreline_qs.annotate(
                transformed_geom=Transform('geom', TARGET_SRID),
                length=Length('transformed_geom')
            ).aggregate(total=Sum('length'))['total']

        meters = total_length.m if total_length else 0
        return {'माप': format_length(meters)}

    # Calculate area for projects
    else:
        if boundary_geom:
            total_area = project_qs.annotate(
                transformed_geom=Transform('geom', TARGET_SRID),
                intersected_geom=Intersection('transformed_geom', boundary_geom),
                area=Area('intersected_geom')
            ).aggregate(total=Sum('area'))['total']
        else:
            total_area = project_qs.annotate(
                transformed_geom=Transform('geom', TARGET_SRID),
                area=Area('transformed_geom')
            ).aggregate(total=Sum('area'))['total']

        sq_meters = total_area.sq_m if total_area else 0
        return {'माप': format_area(sq_meters)}


def get_status_counts(project_id=None, district_name=None, taluka_name=None,
                      village_name=None, gut_name=None):
    filters = {
        'project_id': project_id,
        'district_name': district_name,
        'taluka_name': taluka_name,
        'village_name': village_name,
        'gut_name': gut_name
    }
    bund_queryset = Bund.objects.all()
    gut_queryset = Gut.objects.all()

    # Build filters dynamically based on which parameters are provided
    if gut_name:
        bund_queryset = bund_queryset.filter(fid__name_m=gut_name)
        gut_queryset = gut_queryset.filter(name_m=gut_name)

    if village_name:
        bund_queryset = bund_queryset.filter(fid__fid__name_m=village_name)
        gut_queryset = gut_queryset.filter(fid__name_m=village_name)

    if taluka_name:
        bund_queryset = bund_queryset.filter(fid__fid__fid__name_m=taluka_name)
        gut_queryset = gut_queryset.filter(fid__fid__name_m=taluka_name)

    if district_name:
        bund_queryset = bund_queryset.filter(fid__fid__fid__fid__name_m=district_name)
        gut_queryset = gut_queryset.filter(fid__fid__fid__name_m=district_name)

    if project_id:
        bund_queryset = bund_queryset.filter(fid__fid__fid__fid__fid__uid=project_id)
        gut_queryset = gut_queryset.filter(fid__fid__fid__fid__uid=project_id)

    project = Project.objects.get(uid=project_id) if project_id else None
    length_or_area = {}
    if project:
        length_or_area = get_length_or_area(project, filters)

    acquiretype_counts = bund_queryset.values('acquiretype').annotate(
        count=Count('acquiretype')
    ).order_by('-count')

    if gut_name:
        total_ownerss = list(bund_queryset.values('name_m').distinct())

    else:
        total_ownerss = "Null"

    total_owners = bund_queryset.values('name_m').distinct().count()

    ownertype_counts = bund_queryset.values('ownertype').annotate(
        count=Count('ownertype')
    ).order_by('-count')

    result = bund_queryset.aggregate(
        total_valdecided=Sum('valdecided'),
        total_deduction=Sum('valdeduction')
    )

    if str(result['total_deduction']).lower() == 'nan':
        result['total_deduction'] = 0

    final_valuation = (result['total_valdecided'] or 0) - (result['total_deduction'] or 0)
    formatted_value = format_indian_currency(final_valuation)

    gut_count = gut_queryset.count()

    return {
        'filters_applied': {
            'project_id': project_id,
            'district_name': district_name,
            'taluka_name': taluka_name,
            'village_name': village_name,
            'gut_name': gut_name
        },
        'acquiretype_counts': list(acquiretype_counts),
        'ownertype_counts': list(ownertype_counts),
        'total_ownerss': total_ownerss,
        'valuation_total': formatted_value,
        'owner_counts': total_owners,
        'gut_count': gut_count,
        'measurement': length_or_area
    }