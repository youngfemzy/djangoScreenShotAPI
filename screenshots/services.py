import os
import logging
from playwright.sync_api import sync_playwright
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image, ImageDraw, ImageFont
import tempfile
import uuid


class ScreenshotService:
    """Service for capturing website screenshots using browser automation"""
    
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
            
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Select first device in category
            device_name = list(self.device_configs[device_type].keys())[0]
            config = self.device_configs[device_type][device_name]
            
            # Try Playwright first, then Selenium, finally placeholder
            try:
                return self._capture_with_playwright(url, device_name, config, output_folder)
            except Exception as playwright_error:
                logging.warning(f"Playwright failed, trying Selenium: {str(playwright_error)}")
                try:
                    return self._capture_with_selenium(url, device_name, config, output_folder)
                except Exception as selenium_error:
                    logging.warning(f"Selenium also failed, creating placeholder: {str(selenium_error)}")
                    return self._create_placeholder_screenshot(url, device_name, config, output_folder)
                
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _capture_with_playwright(self, url, device_name, config, output_folder):
        """Capture screenshot using Playwright"""
        with sync_playwright() as p:
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
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-field-trial-config',
                    '--disable-ipc-flooding-protection',
                    '--single-process',
                    '--no-default-browser-check',
                    '--no-experiments'
                ]
            )
            context = browser.new_context(
                viewport={'width': config['width'], 'height': config['height']},
                user_agent=config['user_agent']
            )
            
            page = context.new_page()
            
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(2000)
            except Exception as e:
                logging.warning(f"Navigation warning for {url}: {str(e)}")
            
            # Generate filename
            safe_device_name = device_name.replace(' ', '_').lower()
            filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
            filepath = os.path.join(output_folder, filename)
            
            # Take screenshot
            page.screenshot(path=filepath, full_page=True, type='png')
            browser.close()
            
            logging.info(f"Playwright screenshot captured: {filepath}")
            
            return {
                'success': True,
                'path': filepath,
                'device_name': device_name,
                'width': config['width'],
                'height': config['height'],
                'filename': filename
            }
    
    def _capture_with_selenium(self, url, device_name, config, output_folder):
        """Capture screenshot using Selenium as fallback to Playwright"""
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument(f'--window-size={config["width"]},{config["height"]}')
            chrome_options.add_argument(f'--user-agent={config["user_agent"]}')
            
            # Create unique temporary user data directory
            temp_dir = tempfile.mkdtemp(prefix=f'chrome_data_{uuid.uuid4().hex[:8]}_')
            chrome_options.add_argument(f'--user-data-dir={temp_dir}')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.set_window_size(config['width'], config['height'])
                driver.get(url)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)
                
                # Generate filename
                safe_device_name = device_name.replace(' ', '_').lower()
                filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
                filepath = os.path.join(output_folder, filename)
                
                driver.save_screenshot(filepath)
                
                logging.info(f"Selenium screenshot captured: {filepath}")
                
                return {
                    'success': True,
                    'path': filepath,
                    'device_name': device_name,
                    'width': config['width'],
                    'height': config['height'],
                    'filename': filename
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            logging.error(f"Selenium screenshot failed: {str(e)}")
            raise e
    
    def _create_placeholder_screenshot(self, url, device_name, config, output_folder):
        """Create a placeholder screenshot when browsers are unavailable"""
        try:
            # Generate filename
            safe_device_name = device_name.replace(' ', '_').lower()
            filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
            filepath = os.path.join(output_folder, filename)
            
            # Create placeholder image
            img = Image.new('RGB', (config['width'], config['height']), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
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
            return {'success': False, 'error': str(e)}


class MockupService:
    """Service for creating device mockups from screenshots"""
    
    def __init__(self):
        self.mockup_configs = {
            'mobile': {
                'device_width': 200,
                'device_height': 400,
                'screen_width': 160,
                'screen_height': 300,
                'frame_width': 20,
                'corner_radius': 15
            },
            'tablet': {
                'device_width': 300,
                'device_height': 400,
                'screen_width': 260,
                'screen_height': 320,
                'frame_width': 20,
                'corner_radius': 10
            },
            'desktop': {
                'device_width': 400,
                'device_height': 300,
                'screen_width': 360,
                'screen_height': 220,
                'frame_width': 20,
                'stand_height': 80,
                'corner_radius': 5
            }
        }
    
    def create_mockup(self, screenshot_path, device_type, output_folder):
        """Create a device mockup from a screenshot with standard device dimensions"""
        try:
            if not os.path.exists(screenshot_path):
                return {'success': False, 'error': 'Screenshot file not found'}
            
            if device_type not in self.mockup_configs:
                return {'success': False, 'error': f'Unsupported device type for mockup: {device_type}'}
            
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            config = self.mockup_configs[device_type]
            screenshot = Image.open(screenshot_path)
            
            # Use standard device dimensions
            device_width = config['device_width']
            device_height = config['device_height']
            screen_width = config['screen_width']
            screen_height = config['screen_height']
            
            # Add extra height for desktop stand
            total_height = device_height
            if device_type == 'desktop':
                total_height += config['stand_height']
            
            # Create mockup canvas with standard device size
            mockup = Image.new('RGBA', (device_width, total_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(mockup)
            
            # Draw device frame with standard dimensions
            if device_type == 'mobile':
                self._draw_mobile_frame(draw, device_width, device_height, config)
            elif device_type == 'tablet':
                self._draw_tablet_frame(draw, device_width, device_height, config)
            elif device_type == 'desktop':
                self._draw_desktop_frame(draw, device_width, total_height, config)
            
            # Resize/crop screenshot to fit in the device screen area
            screenshot_resized = self._fit_screenshot_to_device(screenshot, screen_width, screen_height)
            
            # Calculate screen position (centered in device frame)
            screen_x = (device_width - screen_width) // 2
            screen_y = (device_height - screen_height) // 2
            
            # Adjust for top bezel
            if device_type == 'mobile':
                screen_y = 60
            elif device_type == 'tablet':
                screen_y = 50
            elif device_type == 'desktop':
                screen_y = 40
            
            # Paste resized screenshot onto the mockup
            mockup.paste(screenshot_resized, (screen_x, screen_y))
            
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
            return {'success': False, 'error': str(e)}
    
    def _fit_screenshot_to_device(self, screenshot, target_width, target_height):
        """Resize and crop screenshot to fit device screen dimensions"""
        try:
            original_width, original_height = screenshot.size
            
            # Calculate scale to fit width while maintaining aspect ratio
            scale_x = target_width / original_width
            scale_y = target_height / original_height
            scale = min(scale_x, scale_y)
            
            # Resize screenshot
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            screenshot_resized = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create target canvas
            result = Image.new('RGB', (target_width, target_height), color='#ffffff')
            
            # Center the resized screenshot
            x = (target_width - new_width) // 2
            y = 0  # Align to top for scrollable effect
            
            result.paste(screenshot_resized, (x, y))
            
            return result
            
        except Exception as e:
            logging.error(f"Error fitting screenshot to device: {str(e)}")
            return screenshot.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def _draw_mobile_frame(self, draw, width, height, config):
        """Draw mobile device frame"""
        frame_width = config['frame_width']
        # Draw device body
        draw.rounded_rectangle([0, 0, width, height], radius=config['corner_radius'], fill='#2c3e50', outline='#34495e', width=2)
        # Home button
        button_y = height - 25
        draw.ellipse([width//2-10, button_y, width//2+10, button_y+20], fill='#34495e')
        # Speaker
        speaker_width = 60
        speaker_x = (width - speaker_width) // 2
        draw.rounded_rectangle([speaker_x, 15, speaker_x + speaker_width, 25], radius=5, fill='#34495e')
    
    def _draw_tablet_frame(self, draw, width, height, config):
        """Draw tablet device frame"""
        # Draw device body
        draw.rounded_rectangle([0, 0, width, height], radius=config['corner_radius'], fill='#34495e', outline='#2c3e50', width=2)
        # Home button
        button_y = height - 25
        draw.rounded_rectangle([width//2-20, button_y, width//2+20, button_y+15], radius=8, fill='#2c3e50')
    
    def _draw_desktop_frame(self, draw, width, height, config):
        """Draw desktop monitor frame"""
        monitor_height = height - config['stand_height']
        # Monitor
        draw.rounded_rectangle([0, 0, width, monitor_height], radius=config['corner_radius'], fill='#2c3e50', outline='#34495e', width=2)
        # Stand base
        base_width = width // 3
        base_x = (width - base_width) // 2
        draw.rectangle([base_x, monitor_height + 40, base_x + base_width, monitor_height + 60], fill='#34495e')
        # Stand neck
        neck_width = 20
        neck_x = (width - neck_width) // 2
        draw.rectangle([neck_x, monitor_height - 10, neck_x + neck_width, monitor_height + 50], fill='#34495e')
    
    def _add_shadow(self, image):
        """Add drop shadow effect to the mockup"""
        try:
            # Create shadow
            shadow = Image.new('RGBA', (image.width + 20, image.height + 20), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            
            # Draw shadow (offset and blurred effect simulation)
            for i in range(10):
                alpha = 20 - (i * 2)
                shadow_draw.rectangle([10+i, 10+i, image.width+10+i, image.height+10+i], fill=(0, 0, 0, alpha))
            
            # Paste original image on top
            shadow.paste(image, (0, 0), image)
            
            return shadow
        except:
            # Fallback: return original image if shadow creation fails
            return image