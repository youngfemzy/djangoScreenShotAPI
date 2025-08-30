from app import db
from datetime import datetime
from sqlalchemy import Text, DateTime, Integer, String

class Project(db.Model):
    """Model for storing project information"""
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    website_url = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with screenshots
    screenshots = db.relationship('Screenshot', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        from app import db
        screenshot_count = db.session.query(Screenshot).filter_by(project_id=self.id).count()
        return {
            'id': self.id,
            'name': self.name,
            'website_url': self.website_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'screenshot_count': screenshot_count
        }

class Screenshot(db.Model):
    """Model for storing screenshot information"""
    id = db.Column(Integer, primary_key=True)
    project_id = db.Column(Integer, db.ForeignKey('project.id'), nullable=False)
    device_type = db.Column(String(50), nullable=False)  # mobile, tablet, desktop
    device_name = db.Column(String(100), nullable=False)  # iPhone 12, iPad Pro, etc.
    original_path = db.Column(String(500), nullable=False)
    mockup_path = db.Column(String(500))
    width = db.Column(Integer, nullable=False)
    height = db.Column(Integer, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'device_type': self.device_type,
            'device_name': self.device_name,
            'original_path': self.original_path,
            'mockup_path': self.mockup_path,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat()
        }
