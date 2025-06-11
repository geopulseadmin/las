from django.urls import path
from .views import ProjectListView, DistrictListView, TalukaListView, VillageListView, GutListView, GutStatusView, MainStats, GutStats, ProjectStatsAPIView
# from .views import GutDetailsAPIView

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='ProjectListView-list'),
    path('districts/', DistrictListView.as_view(), name='DistrictListView-list'),
    path('talukas/', TalukaListView.as_view(), name='TalukaListView-list'),
    path('villages/', VillageListView.as_view(), name='VillageListView-list'),
    path('guts/', GutListView.as_view(), name='GutListView-list'),
    path('gutStats/', GutStatusView.as_view(), name='GutStatusView-list'),
    path('project-detail/', MainStats.as_view(), name='project-detail'),
    path('project-details/', ProjectStatsAPIView.as_view(), name='project-details'),


    ]