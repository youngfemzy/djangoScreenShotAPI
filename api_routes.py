import os
import logging
from flask import Blueprint, request, jsonify, send_file
from models import Project, Screenshot, db
from screenshot_service import ScreenshotService
from mockup_service import MockupService

api_bp = Blueprint('api', __name__)
screenshot_service = ScreenshotService()
mockup_service = MockupService()

@api_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'website_url' not in data:
            return jsonify({'error': 'Name and website_url are required'}), 400
        
        # Validate URL format
        if not data['website_url'].startswith(('http://', 'https://')):
            data['website_url'] = 'https://' + data['website_url']
        
        project = Project()
        project.name = data['name']
        project.website_url = data['website_url']
        
        db.session.add(project)
        db.session.commit()
        
        logging.info(f"Created project: {project.name} with ID: {project.id}")
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating project: {str(e)}")
        return jsonify({'error': 'Failed to create project'}), 500

@api_bp.route('/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        })
    except Exception as e:
        logging.error(f"Error listing projects: {str(e)}")
        return jsonify({'error': 'Failed to retrieve projects'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project with its screenshots"""
    try:
        project = Project.query.get_or_404(project_id)
        screenshots = Screenshot.query.filter_by(project_id=project_id).all()
        
        return jsonify({
            'project': project.to_dict(),
            'screenshots': [screenshot.to_dict() for screenshot in screenshots]
        })
    except Exception as e:
        logging.error(f"Error getting project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve project'}), 500

@api_bp.route('/projects/<int:project_id>/screenshots', methods=['POST'])
def generate_screenshots(project_id):
    """Generate screenshots for a project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        selected_devices = data.get('devices', ['mobile', 'tablet', 'desktop'])
        
        # Create folder structure
        base_folder = os.path.join('users', 'user1', f'project_{project_id}')
        normal_folder = os.path.join(base_folder, 'normal_screenshots')
        mockup_folder = os.path.join(base_folder, 'mockup_screenshots')
        
        os.makedirs(normal_folder, exist_ok=True)
        os.makedirs(mockup_folder, exist_ok=True)
        
        generated_screenshots = []
        
        for device_type in selected_devices:
            try:
                # Generate screenshot
                screenshot_result = screenshot_service.capture_screenshot(
                    project.website_url, device_type, normal_folder
                )
                
                if screenshot_result['success']:
                    # Generate mockup
                    mockup_result = mockup_service.create_mockup(
                        screenshot_result['path'], device_type, mockup_folder
                    )
                    
                    # Save to database
                    screenshot = Screenshot()
                    screenshot.project_id = project_id
                    screenshot.device_type = device_type
                    screenshot.device_name = screenshot_result['device_name']
                    screenshot.original_path = screenshot_result['path']
                    screenshot.mockup_path = mockup_result['path'] if mockup_result['success'] else None
                    screenshot.width = screenshot_result['width']
                    screenshot.height = screenshot_result['height']
                    
                    db.session.add(screenshot)
                    db.session.flush()  # Flush to get the ID and timestamp
                    generated_screenshots.append(screenshot.to_dict())
                    
                    logging.info(f"Generated screenshot for {device_type}: {screenshot_result['path']}")
                
            except Exception as e:
                logging.error(f"Error generating screenshot for {device_type}: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Generated {len(generated_screenshots)} screenshots',
            'screenshots': generated_screenshots
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating screenshots for project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to generate screenshots'}), 500

@api_bp.route('/projects/<int:project_id>/screenshots', methods=['GET'])
def list_screenshots(project_id):
    """List all screenshots for a project"""
    try:
        Project.query.get_or_404(project_id)  # Verify project exists
        screenshots = Screenshot.query.filter_by(project_id=project_id).all()
        
        return jsonify({
            'screenshots': [screenshot.to_dict() for screenshot in screenshots]
        })
    except Exception as e:
        logging.error(f"Error listing screenshots for project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve screenshots'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project and all its files"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Delete folder structure
        import shutil
        base_folder = os.path.join('users', 'user1', f'project_{project_id}')
        if os.path.exists(base_folder):
            shutil.rmtree(base_folder)
        
        # Delete from database (cascade will handle screenshots)
        db.session.delete(project)
        db.session.commit()
        
        logging.info(f"Deleted project: {project.name}")
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete project'}), 500

@api_bp.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve screenshot files"""
    try:
        file_path = os.path.join('users', filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'Failed to serve file'}), 500
