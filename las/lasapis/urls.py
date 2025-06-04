from django.urls import path
from .views import ProjectListView, DistrictListView, TalukaListView, VillageListView, GutListView
# from .views import GutDetailsAPIView

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='ProjectListView-list'),
    path('districts/', DistrictListView.as_view(), name='DistrictListView-list'),
    path('talukas/', TalukaListView.as_view(), name='TalukaListView-list'),
    path('villages/', VillageListView.as_view(), name='VillageListView-list'),
    path('guts/', GutListView.as_view(), name='GutListView-list'),


    ]