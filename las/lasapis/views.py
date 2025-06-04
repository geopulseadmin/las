

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project
from .serializers import projects

class ProjectListView(APIView):
    def get(self, request):
        self.projectlists = Project.objects.all()
        self.serializer = projects.ProjectSerializer(self.projectlists, many=True)
        # print(serializer.data.uid)
        return Response(self.serializer.data)





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
