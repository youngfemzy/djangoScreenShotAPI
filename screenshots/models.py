from django.db import models
from django.utils import timezone
import os


class Project(models.Model):
    """Model to store website screenshot projects"""
    
    name = models.CharField(max_length=200, help_text="Project name")
    website_url = models.URLField(help_text="Website URL to capture")
    creator_id = models.CharField(max_length=100, help_text="User ID who created the project", default=1)
    creator_name = models.CharField(max_length=200, help_text="Name of the creator", default="femi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ✅ new fields for delays 
    page_delay = models.IntegerField(default=3000, help_text="Delay after page load in ms")
    scroll_delay = models.IntegerField(default=100, help_text="Delay per scroll step in ms")
    timeout = models.IntegerField(default=120000, help_text="Global timeout in ms")

    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} (by {self.creator_name})"

    
    @property
    def screenshot_count(self):
        """Get the number of screenshots for this project"""
        return self.screenshots.count()
    
    def get_project_folder(self):
        """Get the folder path for this project"""
        from django.conf import settings
        return os.path.join(settings.MEDIA_ROOT, f'users_projects/{self.creator_name}_{self.creator_id}/{self.name}/project_{self.id}')
    
    def get_normal_screenshots_folder(self):
        """Get the folder path for normal screenshots"""
        return os.path.join(self.get_project_folder(), 'normal_screenshots')
    
    def get_mockup_screenshots_folder(self):
        """Get the folder path for mockup screenshots"""
        return os.path.join(self.get_project_folder(), 'mockup_screenshots')


class Screenshot(models.Model):
    """Model to store individual screenshots"""
    
    DEVICE_TYPES = [
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='screenshots')
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    device_name = models.CharField(max_length=100, help_text="Specific device name (e.g., iPhone 12)")
    width = models.IntegerField(help_text="Screenshot width in pixels")
    height = models.IntegerField(help_text="Screenshot height in pixels")
    original_path = models.CharField(max_length=500, help_text="Path to original screenshot")
    mockup_path = models.CharField(max_length=500, help_text="Path to mockup image")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.device_name} - {self.project.name}"
    
    @property
    def original_filename(self):
        """Get the filename from original_path"""
        return os.path.basename(str(self.original_path)) if self.original_path else None
    
    @property
    def mockup_filename(self):
        """Get the filename from mockup_path"""
        return os.path.basename(str(self.mockup_path)) if self.mockup_path else None