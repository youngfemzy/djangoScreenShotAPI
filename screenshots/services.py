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
from PIL import Image, ImageDraw, ImageFont , ImageOps
import tempfile
import uuid
import requests

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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
    
    def capture_screenshot(self, url, devices, output_folder, project):
        """Capture screenshot for specified device type"""
        logging.info("Main capture_screenshot function entered")
        try:
            logging.info("🎬 Trying Playwright for screenshots...")
            return self._capture_with_playwright(url, devices, output_folder, project)
        except Exception as playwright_error:
            logging.error(f"[ScreenshotService] Playwright failed: {str(playwright_error)}", exc_info=True)
            logging.info("⚡ Trying ScreenshotOne API For Web Screenshots...")
            return self._capture_with_screenshotone(url, devices, output_folder)
        except Exception as e:
            logging.error(f"[ScreenshotService] All Sreenshot Methods failed")
            return [{'success': False, 'error': str(playwright_error)}]
            
            # Try Playwright first, then Selenium, finally placeholder
        #     try:
        #         logging.info("Main Function Entered")
        #         return self._capture_with_playwright(url, device_name, config, output_folder)
        #     except Exception as playwright_error:
        #         logging.warning(f"Playwright failed, trying Selenium: {str(playwright_error)}")
        #         # try:
        #         #     return self._capture_with_selenium(url, device_name, config, output_folder)
        #         # except Exception as selenium_error:
        #         #     logging.warning(f"Selenium also failed, creating placeholder: {str(selenium_error)}")
        #         return self._create_placeholder_screenshot(url, device_name, config, output_folder)
                
        # except Exception as e:
        #     logging.error(f"Error capturing screenshot: {str(e)}")
        #     return {'success': False, 'error': str(e)}
    
    
    
    # ---------------------------
    # ✅ PLAYWRIGHT
    # ---------------------------
    def _capture_with_playwright(self, url, devices, output_folder, project):
        """
        Capture multiple screenshots in one Playwright session
        (devices = list of (device_name, config, device_type))
        """
        results = []
                    
        # delay variables
        # ✅ Use DB values if available, else fallback to hardcoded defaults
        page_delay = project.page_delay if project and project.page_delay else 1000
        scroll_delay = project.scroll_delay if project and project.scroll_delay else 50
        timeout = project.timeout if project and project.timeout else 120000
        navigation_timeout = timeout + 40000  # ✅ derived value

        logging.info("[Playwright] Launching Chromium...")
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
                    '--single-process',
                ]
            )
            context = browser.new_context()
            # ✅ set global timeouts
            # ✅ get the timeout from project db through variables
            context.set_default_timeout(timeout)
            context.set_default_navigation_timeout(navigation_timeout)
            
            logging.info("Chromium Creating a Page")
            page = context.new_page()
            logging.info("Page Created")

            try:
                # ✅ Load page
                logging.info(f"[Playwright] Navigating to {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                # buffer delay for initial animations, gotten from db
                page.wait_for_timeout(page_delay)  # ✅ user-configurable - can change

                for device_name, config, device_type in devices:
                    # logging.info(f"[Playwright] Switching to device {device_name} ({config['width']}x{config['height']}) , To Capture Screenshot")
                    logging.info(f"[Playwright] Switching to device {device_name} , To Capture Screenshot")
                    # ✅ Adjust viewport for device
                    page.set_viewport_size({
                        "width": config["width"],
                        "height": config["height"]
                    })

                    # small pause for reflow
                    # small pause after viewport change
                    page.wait_for_timeout(1000)

                    # ✅ Scroll step-by-step to trigger lazy-load / animations
                    scroll_height = page.evaluate("document.body.scrollHeight")
                    for pos in range(0, scroll_height, config["height"] // 2):
                        logging.info(f" → Scrolling to each section of this website at {pos}")
                        page.evaluate(f"window.scrollTo(0, {pos})")
                        # delay per scroll section of the website
                        page.wait_for_timeout(scroll_delay) 

                    # ✅ Scroll back to top before screenshot
                    page.evaluate("window.scrollTo(0, 0)")
                    # back to top delay
                    page.wait_for_timeout(500)

                    # ✅ Save screenshot
                    safe_device_name = device_name.replace(" ", "_").lower()
                    filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
                    filepath = os.path.join(output_folder, filename)

                    logging.info(f"[Playwright] Taking screenshot → {filename}")
                    page.screenshot(
                        path=filepath,
                        full_page=True,
                        type="png",
                        timeout=timeout,
                        animations="disabled",
                        caret="hide"
                    )

                    logging.info(f"[Playwright] ✅ Screenshot saved: {filename}")
                    results.append({
                        'success': True,
                        'path': filepath,
                        'device_name': device_name,
                        'width': config['width'],
                        'height': config['height'],
                        'filename': filename,
                        'device_type': device_type,
                    })
                    
                logging.info("[Playwright] All screenshots complete ✅")

            except Exception as e:
                logging.error(f"[Playwright] ❌ Error: {str(e)}", exc_info=True)
                
            finally:
                browser.close()
                logging.info("[Playwright] Browser closed")

        return results



    # ---------------------------
    # ✅ USING SCREENSHOTONE API FOR SCREENSHOT CAPTURE
    # ---------------------------
    def _capture_with_screenshotone(self, url, devices, output_folder):
        """Fallback: ScreenshotOne API"""
        results = []
        base_api = "https://api.screenshotone.com/take"
        # 🔑 ScreenshotOne API key
        self.screenshotone_key = os.getenv("SCREENSHOTONE_KEY", "LI_FkMla6fscKA")

        logging.info("[ScreenshotOne] Starting fallback capture...")

        for device_name, config, device_type in devices:
            params = {
                "url": url,
                "access_key": self.screenshotone_key,
                "format": "png",
                "viewport_width": str(config["width"]),
                "viewport_height": str(config["height"]),
                "full_page": "true",
                "full_page_algorithm": "by_sections",
                "full_page_scroll_delay": "1000",
            }

            safe_device_name = device_name.replace(" ", "_").lower()
            filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
            filepath = os.path.join(output_folder, filename)

            try:
                logging.info(f"[ScreenshotOne] Requesting screenshot for {device_name} → {url}")
                # logging.debug(f"[ScreenshotOne] API Params: {params}")

                r = requests.get(base_api, params=params, timeout=90)
                r.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(r.content)

                logging.info(f"[ScreenshotOne] ✅ Screenshot saved: {filename}")

                results.append({
                    "success": True,
                    "path": filepath,
                    "device_name": device_name,
                    "width": config["width"],
                    "height": config["height"],
                    "filename": filename,
                    "device_type": device_type,
                    "source": "screenshotone"
                })
            except Exception as e:
                logging.error(f"[ScreenshotOne] ❌ Failed for {device_name}: {e}", exc_info=True)
                results.append({
                    "success": False,
                    "error": str(e),
                    "device_name": device_name,
                    "device_type": device_type,
                })

        logging.info("[ScreenshotOne] All devices processed ✅")
        return results

    

    # ---------------------------
    # ✅ SELENIUM CAPTURE
    # ---------------------------
    def _capture_with_selenium(self, url, devices, output_folder):
        """Capture multiple screenshots using Selenium as fallback to Playwright"""
        results = []

        for device_name, config, device_type in devices:
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
                chrome_options.add_argument(f'--user-agent={config.get("user_agent", "Mozilla/5.0")}')

                temp_dir = tempfile.mkdtemp(prefix=f'chrome_data_{uuid.uuid4().hex[:8]}_')
                chrome_options.add_argument(f'--user-data-dir={temp_dir}')

                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )

                try:
                    driver.set_window_size(config['width'], config['height'])
                    driver.get(url)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(5)

                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    for y in range(0, scroll_height, config["height"] // 2):
                        driver.execute_script(f"window.scrollTo(0, {y});")
                        time.sleep(1)

                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(3)

                    safe_device_name = device_name.replace(' ', '_').lower()
                    filename = f"{safe_device_name}_{config['width']}x{config['height']}.png"
                    filepath = os.path.join(output_folder, filename)

                    driver.save_screenshot(filepath)

                    logging.info(f"[Selenium] Screenshot captured for {device_name}: {filepath}")

                    results.append({
                        'success': True,
                        'path': filepath,
                        'device_name': device_name,
                        'width': config['width'],
                        'height': config['height'],
                        'filename': filename,
                        'device_type': device_type,
                        'source': 'selenium'
                    })

                finally:
                    driver.quit()

            except Exception as e:
                logging.error(f"[Selenium] ❌ Failed for {device_name}: {str(e)}", exc_info=True)
                results.append({
                    'success': False,
                    'error': str(e),
                    'device_name': device_name,
                    'device_type': device_type,
                    'source': 'selenium'
                })

        return results

    
    
    
    # ---------------------------
    # ✅ PLACEHOLDER CAPTURE
    # ---------------------------
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
            
            img.save(filepath, 'WEBP')
            
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



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ MOCKUP SERVICES +++++++++++++++++++++++++++++++++++



class MockupService:
    """Service for creating device mockups from screenshots using real device PNG overlays"""

    def __init__(self):
        base_dir = os.path.join(os.path.dirname(__file__), "assets", "mockups")

        # ✅ Real device PNG overlays (must have transparent screen area)
        self.template_paths = {
            "mobile": os.path.join(base_dir, "mobile.png"),
            "tablet": os.path.join(base_dir, "tablet.png"),
            "desktop": os.path.join(base_dir, "desktop.png"),
        }

        # ✅ Define where the screen area is inside those PNGs
        self.screen_positions = {
            "mobile": (255, 230, 3250, 6500),   # left, top, right, bottom
            "tablet": (255, 490, 4500, 6150),
            "desktop": (415, 120, 4300, 2350),
        }





    # ---------------------------
    # ✅ CREATE MOCKUP EACH DEVICE
    # ---------------------------
    def create_mockup(self, screenshot_path, device_type, output_folder):
        """Create a device mockup from a screenshot behind a device PNG overlay"""
        try:
            if not os.path.exists(screenshot_path):
                return {'success': False, 'error': 'Screenshot file not found'}

            if device_type not in self.template_paths:
                return {'success': False, 'error': f'Unsupported device type: {device_type}'}

            os.makedirs(output_folder, exist_ok=True)

            # ✅ Load template (device overlay with transparent screen)
            overlay = Image.open(self.template_paths[device_type]).convert("RGBA")

            # ✅ Load screenshot
            screenshot = Image.open(screenshot_path).convert("RGBA")

            # ✅ Get screen position
            left, top, right, bottom = self.screen_positions[device_type]
            screen_width = right - left
            screen_height = bottom - top

            # ✅ Resize screenshot to fit screen area
            fitted_screenshot = self._fit_screenshot_to_device(screenshot, screen_width, screen_height)

            # ✅ Create base canvas same size as overlay
            base = Image.new("RGBA", overlay.size, (0, 0, 0, 0))

            # ✅ Paste screenshot *first* (behind)
            base.paste(fitted_screenshot, (left, top))

            # ✅ Paste overlay on top (device frame)
            base.alpha_composite(overlay)

            # ✅ Save result
            base_filename = os.path.basename(screenshot_path)
            name, ext = os.path.splitext(base_filename)
            mockup_filename = f"mockup_{name}{ext}"
            mockup_path = os.path.join(output_folder, mockup_filename)
            base.save(mockup_path, "WEBP")

            return {
                'success': True,
                'path': mockup_path,
                'filename': mockup_filename
            }

        except Exception as e:
            logging.error(f"[MockupService] Error creating mockup: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}






    # ---------------------------
    # ✅ FIT SCREENSHOT TO MOCKUP DEVICE BY CUTTING IT DEPENDING ON SIZE
    # ---------------------------
    def _fit_screenshot_to_device(self, screenshot, target_width, target_height):
        """Resize + crop screenshot to fill the mockup screen area properly"""
        try:
            original_width, original_height = screenshot.size

            # Scale to match width
            scale = target_width / original_width
            new_width = target_width
            new_height = int(original_height * scale)
            resized = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Crop or pad vertically
            if new_height > target_height:
                return resized.crop((0, 0, target_width, target_height))
            else:
                background = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 255))
                background.paste(resized, (0, 0))
                return background

        except Exception as e:
            logging.error(f"Error fitting screenshot: {str(e)}")
            return screenshot.resize((target_width, target_height), Image.Resampling.LANCZOS)




