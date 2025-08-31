from django.contrib import admin
from .models import Project, Screenshot


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url', 'screenshot_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'website_url')
    readonly_fields = ('created_at', 'updated_at')
    
    def screenshot_count(self, obj):
        return obj.screenshot_count
    screenshot_count.short_description = 'Screenshots'


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_type', 'project', 'width', 'height', 'created_at')
    list_filter = ('device_type', 'created_at', 'project')
    search_fields = ('device_name', 'project__name')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')