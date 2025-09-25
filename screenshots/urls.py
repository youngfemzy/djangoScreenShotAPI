from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'screenshots'

urlpatterns = [
    # Web interface routes
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('project/<int:project_id>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    # API routes
    path('api/projects/', views.ProjectAPIView.as_view(), name='api_projects'),
    path('api/projects/<int:project_id>/screenshots/', views.ScreenshotAPIView.as_view(), name='api_screenshots'),
    path('api/projects/<int:project_id>/delete/', views.delete_project, name='api_delete_project'),
    path("api/projects/<int:project_id>/update/", views.update_project_settings, name="update_project_settings"),

    path('api/screenshots/<int:screenshot_id>/delete', views.delete_screenshot, name='delete_screenshot'),
    path('api/screenshots/<int:screenshot_id>/regenerate/', views.regenerate_screenshot, name='regenerate_screenshot'),
]

# Serve media files during development


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)