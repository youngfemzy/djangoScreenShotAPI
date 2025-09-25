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


from django.conf import settings

# for celery screenshot generation
# in views.py
from .tasks import generate_screenshots, regenerate_single_screenshot


def make_relative_path(abs_path):
    """
    Convert absolute path on disk into relative path under MEDIA_ROOT.
    Example:
      C:/project/media/users/p1/file.png
    -> users/p1/file.png
    """
    return os.path.relpath(abs_path, settings.MEDIA_ROOT).replace("\\", "/")



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
            creator_id = data.get('creator_id')
            creator_name = data.get('creator_name')
            
            if not all([name, website_url, creator_id, creator_name]):
                return JsonResponse({'error': 'Name and website_url are required'}, status=400)
            
            project = Project.objects.create(
                name=name,
                website_url=website_url,
                creator_id=creator_id,
                creator_name=creator_name
            )
            
            logging.info(f"Created project: {name} with ID: {project.id}")
            
            return JsonResponse({
                'message': 'Project created successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'website_url': project.website_url,
                    'creator_id': project.creator_id,
                    'creator_name': project.creator_name,
                    'page_delay': project.page_delay,
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
        try:
            project = get_object_or_404(Project, id=project_id)
            data = json.loads(request.body)
            devices = data.get('devices', ['mobile', 'tablet', 'desktop'])

            task = generate_screenshots.delay(project.id, devices)

            return JsonResponse({
                "message": "Screenshots task queued",
                "task_id": task.id
            })

        except Exception as e:
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
    
    
    
@require_http_methods(["DELETE"])
@csrf_exempt
def delete_screenshot(request, screenshot_id):
    """Delete individual screenshot (full + mockup)"""
    try:
        screenshot = get_object_or_404(Screenshot, id=screenshot_id)
        
        # Delete files
        if screenshot.original_path and os.path.exists(screenshot.original_path):
            os.remove(screenshot.original_path)
        if screenshot.mockup_path and os.path.exists(screenshot.mockup_path):
            os.remove(screenshot.mockup_path)

        project = screenshot.project
        screenshot.delete()

        # update project screenshot count
        # project.screenshot_count = project.screenshots.count()
        # project.save(update_fields=["screenshot_count"])

        logging.info(f"[Delete] Screenshot {screenshot_id} deleted for project {project.id}")

        return JsonResponse({"message": f"Screenshot {screenshot_id} deleted successfully"})
    
    except Exception as e:
        logging.error(f"Error deleting screenshot {screenshot_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def regenerate_screenshot(request, screenshot_id):
    """Regenerate an individual screenshot + mockup"""
    try:
        screenshot = get_object_or_404(Screenshot, id=screenshot_id)
        project = screenshot.project

        # queue Celery regeneration
        task = regenerate_single_screenshot.delay(screenshot.id)

        return JsonResponse({
            "message": f"Regeneration queued for screenshot {screenshot.id}",
            "task_id": task.id
        })

    except Exception as e:
        logging.error(f"Error queuing regeneration for screenshot {screenshot_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def update_project_settings(request, project_id):
    logging.info("updatting project.....")
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        project = Project.objects.get(id=project_id)
        data = json.loads(request.body)

        project.page_delay = data.get("page_delay", project.page_delay)
        project.scroll_delay = data.get("scroll_delay", project.scroll_delay)
        project.timeout = data.get("timeout", project.timeout)
        project.save()
        logging.info("project data updatted")

        return JsonResponse({
            "success": True,
            "project_id": project.id,
            "settings": {
                "page_delay": project.page_delay,
                "scroll_delay": project.scroll_delay,
                "timeout": project.timeout,
            }
        })

    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)