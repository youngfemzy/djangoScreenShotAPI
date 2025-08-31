from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator
import json
import os
import logging

from .models import Project, Screenshot
from .services import ScreenshotService, MockupService


class ProjectListView(View):
    """View for listing all projects and creating new ones"""
    
    def get(self, request):
        """Render the main page with projects list"""
        projects = Project.objects.all()
        return render(request, 'screenshots/index.html', {'projects': projects})


class ProjectDetailView(View):
    """View for project details"""
    
    def get(self, request, project_id):
        """Render project detail page"""
        project = get_object_or_404(Project, id=project_id)
        screenshots = project.screenshots.all()
        return render(request, 'screenshots/project_detail.html', {
            'project': project,
            'screenshots': screenshots
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProjectAPIView(View):
    """API view for creating projects"""
    
    def get(self, request):
        """Get all projects"""
        projects = Project.objects.all()
        projects_data = []
        
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'website_url': project.website_url,
                'screenshot_count': project.screenshot_count,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            })
        
        return JsonResponse({'projects': projects_data})
    
    def post(self, request):
        """Create a new project"""
        try:
            data = json.loads(request.body)
            name = data.get('name')
            website_url = data.get('website_url')
            
            if not name or not website_url:
                return JsonResponse({'error': 'Name and website_url are required'}, status=400)
            
            project = Project.objects.create(
                name=name,
                website_url=website_url
            )
            
            logging.info(f"Created project: {name} with ID: {project.id}")
            
            return JsonResponse({
                'message': 'Project created successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'website_url': project.website_url,
                    'screenshot_count': project.screenshot_count,
                    'created_at': project.created_at.isoformat(),
                    'updated_at': project.updated_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logging.error(f"Error creating project: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScreenshotAPIView(View):
    """API view for generating screenshots"""
    
    def post(self, request, project_id):
        """Generate screenshots for a project"""
        try:
            project = get_object_or_404(Project, id=project_id)
            data = json.loads(request.body)
            devices = data.get('devices', ['mobile', 'tablet', 'desktop'])
            
            if not isinstance(devices, list):
                return JsonResponse({'error': 'devices must be a list'}, status=400)
            
            # Create folders for this project
            normal_folder = project.get_normal_screenshots_folder()
            mockup_folder = project.get_mockup_screenshots_folder()
            os.makedirs(normal_folder, exist_ok=True)
            os.makedirs(mockup_folder, exist_ok=True)
            
            screenshot_service = ScreenshotService()
            mockup_service = MockupService()
            
            screenshots_created = []
            
            for device_type in devices:
                if device_type not in ['mobile', 'tablet', 'desktop']:
                    continue
                
                # Capture screenshot
                screenshot_result = screenshot_service.capture_screenshot(
                    project.website_url,
                    device_type,
                    normal_folder
                )
                
                if screenshot_result['success']:
                    # Create mockup
                    mockup_result = mockup_service.create_mockup(
                        screenshot_result['path'],
                        device_type,
                        mockup_folder
                    )
                    
                    # Save screenshot record to database
                    screenshot = Screenshot.objects.create(
                        project=project,
                        device_type=device_type,
                        device_name=screenshot_result['device_name'],
                        width=screenshot_result['width'],
                        height=screenshot_result['height'],
                        original_path=screenshot_result['path'],
                        mockup_path=mockup_result['path'] if mockup_result['success'] else ''
                    )
                    
                    screenshots_created.append({
                        'id': screenshot.id,
                        'device_type': device_type,
                        'device_name': screenshot_result['device_name'],
                        'width': screenshot_result['width'],
                        'height': screenshot_result['height'],
                        'original_path': screenshot_result['path'],
                        'mockup_path': mockup_result['path'] if mockup_result['success'] else '',
                        'project_id': project.id,
                        'created_at': screenshot.created_at.isoformat()
                    })
                    
                    logging.info(f"Generated screenshot for {device_type}: {screenshot_result['path']}")
                else:
                    logging.error(f"Failed to generate screenshot for {device_type}: {screenshot_result.get('error')}")
            
            return JsonResponse({
                'message': f'Generated {len(screenshots_created)} screenshots',
                'screenshots': screenshots_created
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logging.error(f"Error generating screenshots: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_project(request, project_id):
    """Delete a project and its screenshots"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Delete associated files
        project_folder = project.get_project_folder()
        if os.path.exists(project_folder):
            import shutil
            shutil.rmtree(project_folder)
        
        project_name = project.name
        project.delete()
        
        logging.info(f"Deleted project: {project_name}")
        
        return JsonResponse({'message': f'Project "{project_name}" deleted successfully'})
        
    except Exception as e:
        logging.error(f"Error deleting project: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)