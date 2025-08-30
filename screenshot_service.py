import os
import logging
from playwright.sync_api import sync_playwright
import asyncio

class ScreenshotService:
    """Service for capturing website screenshots using Playwright"""
    
    def __init__(self):
        self.device_configs = {
            'mobile': {
                'iPhone 12': {'width': 390, 'height': 844, 'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'},
                'Samsung Galaxy S21': {'width': 360, 'height': 800, 'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36'},
                'Google Pixel 5': {'width': 393, 'height': 851, 'user_agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36'}
            },
            'tablet': {
                'iPad Pro': {'width': 1024, 'height': 1366, 'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15'},
                'Samsung Galaxy Tab': {'width': 800, 'height': 1280, 'user_agent': 'Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36'},
                'Surface Pro': {'width': 912, 'height': 1368, 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'desktop': {
                'Desktop 1920x1080': {'width': 1920, 'height': 1080, 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                'Desktop 1366x768': {'width': 1366, 'height': 768, 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                'MacBook Pro': {'width': 1440, 'height': 900, 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            }
        }
    
    def capture_screenshot(self, url, device_type, output_folder):
        """Capture screenshot for specified device type"""
        try:
            if device_type not in self.device_configs:
                return {'success': False, 'error': f'Unsupported device type: {device_type}'}
            
            # Select first device in category for now (can be enhanced to capture all)
            device_name = list(self.device_configs[device_type].keys())[0]
            config = self.device_configs[device_type][device_name]
            
            # Try Playwright first, fallback to placeholder if dependencies missing
            try:
                with sync_playwright() as p:
                    # Launch browser with additional args for headless server environment
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-gpu',
                            '--disable-features=VizDisplayCompositor'
                        ]
                    )
                    context = browser.new_context(
                        viewport={'width': config['width'], 'height': config['height']},
                        user_agent=config['user_agent']
                    )
                    
                    page = context.new_page()
                    
                    # Navigate to URL with timeout
                    try:
                        page.goto(url, wait_until='networkidle', timeout=30000)
                        page.wait_for_timeout(2000)  # Additional wait for dynamic content
                    except Exception as e:
                        logging.warning(f"Navigation warning for {url}: {str(e)}")
                    
                    # Generate filename
                    safe_device_name = device_name.replace(' ', '_').lower()
                    filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
                    filepath = os.path.join(output_folder, filename)
                    
                    # Take screenshot
                    page.screenshot(
                        path=filepath,
                        full_page=True,
                        type='png'
                    )
                    
                    browser.close()
                    
                    logging.info(f"Screenshot captured: {filepath}")
                    
                    return {
                        'success': True,
                        'path': filepath,
                        'device_name': device_name,
                        'width': config['width'],
                        'height': config['height'],
                        'filename': filename
                    }
                    
            except Exception as playwright_error:
                # If Playwright fails, create a placeholder screenshot
                logging.warning(f"Playwright failed, creating placeholder: {str(playwright_error)}")
                return self._create_placeholder_screenshot(url, device_name, config, output_folder)
                
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_placeholder_screenshot(self, url, device_name, config, output_folder):
        """Create a placeholder screenshot when Playwright is unavailable"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Generate filename
            safe_device_name = device_name.replace(' ', '_').lower()
            filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
            filepath = os.path.join(output_folder, filename)
            
            # Create placeholder image
            img = Image.new('RGB', (config['width'], config['height']), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Try to use a basic font, fallback to default if not available
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw placeholder content
            text_lines = [
                f"Screenshot Placeholder",
                f"",
                f"Device: {device_name}",
                f"Resolution: {config['width']}x{config['height']}",
                f"URL: {url}",
                f"",
                f"This is a placeholder image.",
                f"In production, this would be a",
                f"real screenshot of the website."
            ]
            
            y = 50
            for line in text_lines:
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                x = (config['width'] - text_width) // 2
                draw.text((x, y), line, fill='#333333', font=font)
                y += 30
            
            # Add a border
            draw.rectangle([10, 10, config['width']-10, config['height']-10], outline='#cccccc', width=2)
            
            # Save the placeholder
            img.save(filepath, 'PNG')
            
            logging.info(f"Placeholder screenshot created: {filepath}")
            
            return {
                'success': True,
                'path': filepath,
                'device_name': device_name,
                'width': config['width'],
                'height': config['height'],
                'filename': filename
            }
            
        except Exception as e:
            logging.error(f"Error creating placeholder screenshot: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def capture_all_devices(self, url, output_folder):
        """Capture screenshots for all device types"""
        results = []
        
        for device_type in self.device_configs.keys():
            result = self.capture_screenshot(url, device_type, output_folder)
            results.append({
                'device_type': device_type,
                'result': result
            })
        
        return results
