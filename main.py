import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'screenshot_generator.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# For gunicorn compatibility  
app = application