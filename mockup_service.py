import os
import logging
from PIL import Image, ImageDraw, ImageFilter
import math

class MockupService:
    """Service for creating device mockups from screenshots"""
    
    def __init__(self):
        # Device mockup configurations with colors and dimensions
        self.mockup_configs = {
            'mobile': {
                'frame_color': '#1a1a1a',
                'screen_color': '#000000',
                'frame_width': 30,
                'corner_radius': 25,
                'button_radius': 3,
                'camera_radius': 8
            },
            'tablet': {
                'frame_color': '#2a2a2a',
                'screen_color': '#000000',
                'frame_width': 40,
                'corner_radius': 15,
                'button_radius': 2,
                'camera_radius': 0
            },
            'desktop': {
                'frame_color': '#333333',
                'screen_color': '#000000',
                'frame_width': 20,
                'corner_radius': 8,
                'button_radius': 0,
                'camera_radius': 0,
                'stand_height': 100
            }
        }
    
    def create_mockup(self, screenshot_path, device_type, output_folder):
        """Create a device mockup from a screenshot"""
        try:
            if not os.path.exists(screenshot_path):
                return {'success': False, 'error': 'Screenshot file not found'}
            
            if device_type not in self.mockup_configs:
                return {'success': False, 'error': f'Unsupported device type for mockup: {device_type}'}
            
            config = self.mockup_configs[device_type]
            
            # Load the screenshot
            screenshot = Image.open(screenshot_path)
            screenshot_width, screenshot_height = screenshot.size
            
            # Calculate mockup dimensions
            frame_width = config['frame_width']
            mockup_width = screenshot_width + (frame_width * 2)
            mockup_height = screenshot_height + (frame_width * 2)
            
            # Add extra height for desktop stand
            if device_type == 'desktop':
                mockup_height += config['stand_height']
            
            # Create mockup canvas
            mockup = Image.new('RGBA', (mockup_width, mockup_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(mockup)
            
            # Draw device frame
            if device_type == 'mobile':
                self._draw_mobile_frame(draw, mockup_width, mockup_height, config)
            elif device_type == 'tablet':
                self._draw_tablet_frame(draw, mockup_width, mockup_height, config)
            elif device_type == 'desktop':
                self._draw_desktop_frame(draw, mockup_width, mockup_height, config)
            
            # Paste screenshot onto the mockup
            screen_x = frame_width
            screen_y = frame_width
            mockup.paste(screenshot, (screen_x, screen_y))
            
            # Add shadow effect
            mockup = self._add_shadow(mockup)
            
            # Generate output filename
            base_filename = os.path.basename(screenshot_path)
            name, ext = os.path.splitext(base_filename)
            mockup_filename = f"mockup_{name}{ext}"
            mockup_path = os.path.join(output_folder, mockup_filename)
            
            # Save mockup
            mockup.save(mockup_path, 'PNG')
            
            logging.info(f"Mockup created: {mockup_path}")
            
            return {
                'success': True,
                'path': mockup_path,
                'filename': mockup_filename
            }
            
        except Exception as e:
            logging.error(f"Error creating mockup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _draw_mobile_frame(self, draw, width, height, config):
        """Draw mobile device frame"""
        frame_width = config['frame_width']
        corner_radius = config['corner_radius']
        
        # Draw main frame with rounded corners
        self._draw_rounded_rectangle(
            draw, 0, 0, width, height - config.get('stand_height', 0),
            corner_radius, config['frame_color']
        )
        
        # Draw home button
        button_y = height - frame_width + 5
        button_x = width // 2
        button_radius = config['button_radius']
        draw.ellipse([
            button_x - button_radius, button_y - button_radius,
            button_x + button_radius, button_y + button_radius
        ], fill='#666666')
        
        # Draw front camera
        camera_y = frame_width // 2
        camera_x = width // 2
        camera_radius = config['camera_radius']
        draw.ellipse([
            camera_x - camera_radius, camera_y - camera_radius,
            camera_x + camera_radius, camera_y + camera_radius
        ], fill='#333333')
    
    def _draw_tablet_frame(self, draw, width, height, config):
        """Draw tablet device frame"""
        frame_width = config['frame_width']
        corner_radius = config['corner_radius']
        
        # Draw main frame with rounded corners
        self._draw_rounded_rectangle(
            draw, 0, 0, width, height,
            corner_radius, config['frame_color']
        )
        
        # Draw home button
        button_size = 20
        button_y = height - frame_width // 2
        button_x = width // 2
        draw.ellipse([
            button_x - button_size//2, button_y - button_size//2,
            button_x + button_size//2, button_y + button_size//2
        ], fill='#666666')
    
    def _draw_desktop_frame(self, draw, width, height, config):
        """Draw desktop monitor frame with stand"""
        frame_width = config['frame_width']
        corner_radius = config['corner_radius']
        stand_height = config['stand_height']
        
        # Draw monitor frame
        monitor_height = height - stand_height
        self._draw_rounded_rectangle(
            draw, 0, 0, width, monitor_height,
            corner_radius, config['frame_color']
        )
        
        # Draw monitor stand
        stand_width = width // 4
        stand_x = (width - stand_width) // 2
        stand_y = monitor_height - 10
        
        # Stand pole
        pole_width = 10
        pole_x = (width - pole_width) // 2
        draw.rectangle([
            pole_x, stand_y, pole_x + pole_width, stand_y + stand_height - 30
        ], fill=config['frame_color'])
        
        # Stand base
        base_width = width // 3
        base_x = (width - base_width) // 2
        base_y = height - 30
        draw.ellipse([
            base_x, base_y, base_x + base_width, base_y + 30
        ], fill=config['frame_color'])
    
    def _draw_rounded_rectangle(self, draw, x1, y1, x2, y2, radius, fill):
        """Draw a rounded rectangle"""
        # Draw the main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        
        # Draw corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)
    
    def _add_shadow(self, image):
        """Add shadow effect to the mockup"""
        try:
            # Create shadow
            shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            
            # Draw shadow shape (slightly offset)
            offset = 10
            shadow_alpha = 50
            
            # Create a simple shadow by drawing a semi-transparent rectangle
            shadow_draw.rectangle([
                offset, offset, 
                image.size[0] - offset, image.size[1] - offset
            ], fill=(0, 0, 0, shadow_alpha))
            
            # Blur the shadow
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
            
            # Composite shadow with original image
            result = Image.new('RGBA', image.size, (255, 255, 255, 0))
            result.paste(shadow, (0, 0))
            result.paste(image, (0, 0), image)
            
            return result
            
        except Exception as e:
            logging.warning(f"Could not add shadow effect: {str(e)}")
            return image
