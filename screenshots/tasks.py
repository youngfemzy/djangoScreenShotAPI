# screenshots/tasks.py
import logging
from celery import shared_task
from .services import ScreenshotService, MockupService
from .models import Project, Screenshot
from django.conf import settings
import os

def make_relative_path(abs_path):
    return os.path.relpath(abs_path, settings.MEDIA_ROOT).replace("\\", "/")

@shared_task(bind=True)
def generate_screenshots(self, project_id, devices=None):
    """Background task to generate screenshots + mockups"""
    try:
        project = Project.objects.get(id=project_id)
        devices = devices or ['mobile', 'tablet', 'desktop']

        normal_folder = project.get_normal_screenshots_folder()
        mockup_folder = project.get_mockup_screenshots_folder()
        os.makedirs(normal_folder, exist_ok=True)
        os.makedirs(mockup_folder, exist_ok=True)

        screenshot_service = ScreenshotService()
        mockup_service = MockupService()

        # ✅ Build all device configs in one list
        device_list = []
        for device_type in devices:
            if device_type not in screenshot_service.device_configs:
                continue

            device_name = list(screenshot_service.device_configs[device_type].keys())[0]
            config = screenshot_service.device_configs[device_type][device_name]
            device_list.append((device_name, config, device_type))

        
        logging.info("Celery Task Started : taking screenshot")
        # ✅ Capture screenshots through wrapper
        screenshot_results = screenshot_service.capture_screenshot(
            project.website_url,
            device_list,
            normal_folder,
            project
        )
        logging.info("Celery Task Continues : screenshot gotten")


        results = []
        for sr in screenshot_results:
            if sr['success']:
                
                logging.info(f"[celery] Generating Mockup For → {sr['device_type']}")
                mockup_result = mockup_service.create_mockup(
                    sr['path'],
                    sr['device_type'],
                    mockup_folder
                )

                screenshot = Screenshot.objects.create(
                    project=project,
                    device_type=sr['device_type'],
                    device_name=sr['device_name'],
                    width=sr['width'],
                    height=sr['height'],
                    original_path=make_relative_path(sr['path']),
                    mockup_path=make_relative_path(mockup_result['path']) if mockup_result['success'] else ''
                )

                results.append({
                    "id": screenshot.id,
                    "device_type": sr['device_type'],
                    "original_path": screenshot.original_path,
                    "mockup_path": screenshot.mockup_path,
                })

        logging.info("Celery Task Completed")
        return {"success": True, "screenshots": results}

    except Exception as e:
        logging.error(f"[Celery] Error: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}



@shared_task(bind=True)
def regenerate_single_screenshot(self, screenshot_id):
    """Regenerate screenshot + mockup for one device (override files in place)"""
    try:
        screenshot = Screenshot.objects.get(id=screenshot_id)
        project = screenshot.project

        logging.info(f"[Task] Regenerating screenshot {screenshot_id} for {project.website_url}")

        screenshot_service = ScreenshotService()
        mockup_service = MockupService()

        # keep the same folders as before
        normal_folder = project.get_normal_screenshots_folder()
        mockup_folder = project.get_mockup_screenshots_folder()
        os.makedirs(normal_folder, exist_ok=True)
        os.makedirs(mockup_folder, exist_ok=True)

        device_config = {
            "width": screenshot.width,
            "height": screenshot.height,
        }

        # Always overwrite into the SAME FILE path
        original_abs_path = os.path.join(settings.MEDIA_ROOT, screenshot.original_path)
        mockup_abs_path   = os.path.join(settings.MEDIA_ROOT, screenshot.mockup_path) if screenshot.mockup_path else None

        # capture screenshot → force overwrite
        results = screenshot_service.capture_screenshot(
            url=project.website_url,
            devices=[(screenshot.device_name, device_config, screenshot.device_type)],
            output_folder=normal_folder,
            project = project,
            # force_filename=os.path.basename(original_abs_path)  # 👈 reuse same filename
        )

        if results and results[0]["success"]:
            res = results[0]

            # overwrite original file (replace existing content)
            if res["path"] != original_abs_path:
                import shutil
                shutil.move(res["path"], original_abs_path)

            # regenerate mockup at same path
            if mockup_abs_path:
                mockup_service.create_mockup(original_abs_path, screenshot.device_type, mockup_folder)
            else:
                mockup_result = mockup_service.create_mockup(original_abs_path, screenshot.device_type, mockup_folder)
                if mockup_result["success"]:
                    screenshot.mockup_path = make_relative_path(mockup_result["path"])

            screenshot.save()

            logging.info(f"[Task] Screenshot {screenshot_id} regenerated ✅ (overwritten in place)")

            return {"success": True, "screenshot_id": screenshot.id}

        else:
            logging.error(f"[Task] Failed regenerating screenshot {screenshot_id}")
            return {"success": False, "screenshot_id": screenshot.id}

    except Screenshot.DoesNotExist:
        logging.error(f"[Task] Screenshot {screenshot_id} not found")
        return {"success": False, "error": "Not found"}
    except Exception as e:
        logging.error(f"[Task] Error regenerating screenshot {screenshot_id}: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
