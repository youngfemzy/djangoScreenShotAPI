from django.urls import path
from . import views

app_name = 'screenshots'

urlpatterns = [
    # Web interface routes
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('project/<int:project_id>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    # API routes
    path('api/projects/', views.ProjectAPIView.as_view(), name='api_projects'),
    path('api/projects/<int:project_id>/screenshots/', views.ScreenshotAPIView.as_view(), name='api_screenshots'),
    path('api/projects/<int:project_id>/delete/', views.delete_project, name='api_delete_project'),
]