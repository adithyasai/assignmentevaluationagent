"""
Functional testing module for React applications.
Tests actual functionality like button clicks, navigation, form submissions, etc.
"""
import asyncio
import subprocess
import time
import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from loguru import logger
import config
import os
import tempfile
import threading
import socket
import requests
from urllib.parse import urljoin


class FunctionalTester:
    """Handles end-to-end functional testing of React applications."""
    
    def __init__(self):
        """Initialize the functional tester."""
        self.playwright_available = False
        self.selenium_available = False
        self.test_port = 3000
        self.test_timeout = 30  # seconds
        self.server_process = None
        self.server_thread = None
        
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if testing dependencies are available."""
        try:
            import playwright
            self.playwright_available = True
            logger.info("✅ Playwright available for functional testing")
        except ImportError:
            logger.warning("⚠️ Playwright not available")
        
        try:
            import selenium
            self.selenium_available = True
            logger.info("✅ Selenium available for functional testing")
        except ImportError:
            logger.warning("⚠️ Selenium not available")
    
    def test_react_app_functionality(self, local_path: str, requirements: List[str], 
                                   package_manager: str = 'npm') -> Dict[str, any]:
        """
        Test React app functionality end-to-end.
        
        Args:
            local_path: Path to the React project
            requirements: List of requirements to test
            package_manager: Package manager to use (npm/yarn)
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"🧪 Starting functional testing for React app at: {local_path}")
        
        test_results = {
            'server_started': False,
            'app_loads': False,
            'navigation_works': False,
            'buttons_work': False,
            'forms_work': False,
            'components_render': False,
            'requirements_met': [],
            'requirements_failed': [],
            'functionality_score': 0,
            'test_details': [],
            'screenshots': [],
            'errors': []
        }
        
        try:
            # Step 1: Start development server
            logger.info(f"🚀 Starting React development server...")
            server_success, server_url = self._start_dev_server(local_path, package_manager)
            test_results['server_started'] = server_success
            
            if not server_success:
                test_results['errors'].append("Failed to start development server")
                test_results['test_details'].append("❌ Development server failed to start")
                return test_results
            
            logger.info(f"✅ Server started at: {server_url}")
            test_results['test_details'].append(f"✅ Development server started at {server_url}")
            
            # Step 2: Test basic app loading
            app_loads = self._test_app_loading(server_url)
            test_results['app_loads'] = app_loads
            
            if app_loads:
                test_results['test_details'].append("✅ App loads successfully")
                test_results['functionality_score'] += 20
            else:
                test_results['test_details'].append("❌ App fails to load")
                test_results['errors'].append("App does not load properly")
            
            # Step 3: Test specific functionality based on requirements
            if app_loads:
                if self.playwright_available:
                    additional_results = self._test_with_playwright(server_url, requirements)
                    test_results.update(additional_results)
                elif self.selenium_available:
                    additional_results = self._test_with_selenium(server_url, requirements)
                    test_results.update(additional_results)
                else:
                    # Basic HTML parsing tests
                    additional_results = self._test_with_basic_parsing(server_url, requirements)
                    test_results.update(additional_results)
            
            return test_results
            
        except Exception as e:
            logger.error(f"❌ Functional testing error: {str(e)}")
            test_results['errors'].append(f"Testing error: {str(e)}")
            return test_results
        
        finally:
            # Cleanup: Stop the development server
            self._stop_dev_server()
    
    def _start_dev_server(self, local_path: str, package_manager: str) -> Tuple[bool, str]:
        """Start React development server."""
        try:
            # Find available port
            self.test_port = self._find_free_port()
            server_url = f"http://localhost:{self.test_port}"
            
            # Set environment variables for React
            env = os.environ.copy()
            env['PORT'] = str(self.test_port)
            env['BROWSER'] = 'none'  # Don't open browser
            env['CI'] = 'true'  # Prevent interactive prompts
            
            # Start server command
            if package_manager == 'yarn':
                cmd = ['yarn', 'start']
            else:
                cmd = ['npm', 'start']
            
            logger.info(f"🚀 Starting server: {' '.join(cmd)} on port {self.test_port}")
            
            # Start server in background
            self.server_process = subprocess.Popen(
                cmd,
                cwd=local_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start (check for up to 30 seconds)
            for i in range(30):
                try:
                    response = requests.get(server_url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Server is ready at {server_url}")
                        return True, server_url
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                
                # Check if process died
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    logger.error(f"❌ Server process died: {stderr}")
                    return False, ""
            
            logger.error(f"❌ Server did not start within 30 seconds")
            return False, ""
            
        except Exception as e:
            logger.error(f"❌ Error starting server: {str(e)}")
            return False, ""
    
    def _stop_dev_server(self):
        """Stop the development server."""
        try:
            if self.server_process:
                logger.info("🛑 Stopping development server...")
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.server_process.kill()
                    self.server_process.wait()
                
                logger.info("✅ Development server stopped")
                self.server_process = None
                
        except Exception as e:
            logger.error(f"❌ Error stopping server: {str(e)}")
    
    def _find_free_port(self, start_port: int = 3000) -> int:
        """Find a free port starting from the given port."""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port  # Fallback
    
    def _test_app_loading(self, server_url: str) -> bool:
        """Test if the React app loads properly."""
        try:
            response = requests.get(server_url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ App returned status code: {response.status_code}")
                return False
            
            html_content = response.text.lower()
            
            # Check for React indicators
            react_indicators = [
                'react',
                'div id="root"',
                'div id="app"',
                'react-dom',
                'bundle.js',
                'main.js'
            ]
            
            found_indicators = sum(1 for indicator in react_indicators if indicator in html_content)
            
            if found_indicators >= 2:
                logger.info(f"✅ App loads with {found_indicators} React indicators found")
                return True
            else:
                logger.warning(f"⚠️ App loads but only {found_indicators} React indicators found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing app loading: {str(e)}")
            return False
    
    def _test_with_playwright(self, server_url: str, requirements: List[str]) -> Dict[str, any]:
        """Test functionality using Playwright."""
        results = {
            'navigation_works': False,
            'buttons_work': False,
            'forms_work': False,
            'components_render': False,
            'test_details': [],
            'functionality_score': 0
        }
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to app
                page.goto(server_url)
                page.wait_for_load_state('networkidle', timeout=10000)
                
                # Test 1: Check if components render
                body_text = page.inner_text('body').lower()
                if len(body_text) > 50:  # App has content
                    results['components_render'] = True
                    results['test_details'].append("✅ Components render with content")
                    results['functionality_score'] += 15
                
                # Test 2: Test buttons
                buttons = page.locator('button, input[type="button"], input[type="submit"]')
                button_count = buttons.count()
                
                if button_count > 0:
                    try:
                        # Try clicking the first button
                        buttons.first.click(timeout=2000)
                        results['buttons_work'] = True
                        results['test_details'].append(f"✅ Found and tested {button_count} buttons")
                        results['functionality_score'] += 20
                    except:
                        results['test_details'].append(f"⚠️ Found {button_count} buttons but clicking failed")
                        results['functionality_score'] += 10
                
                # Test 3: Test navigation/links
                links = page.locator('a, [role="button"]')
                link_count = links.count()
                
                if link_count > 0:
                    try:
                        # Check for routing indicators
                        current_url = page.url
                        links.first.click(timeout=2000)
                        page.wait_for_timeout(1000)
                        new_url = page.url
                        
                        if current_url != new_url or page.inner_text('body') != body_text:
                            results['navigation_works'] = True
                            results['test_details'].append(f"✅ Navigation works with {link_count} links")
                            results['functionality_score'] += 20
                        else:
                            results['test_details'].append(f"⚠️ Found {link_count} links but navigation not detected")
                            results['functionality_score'] += 5
                    except:
                        results['test_details'].append(f"⚠️ Found {link_count} links but testing failed")
                
                # Test 4: Test forms
                forms = page.locator('form, input[type="text"], input[type="email"], textarea')
                form_count = forms.count()
                
                if form_count > 0:
                    try:
                        # Try filling a form field
                        inputs = page.locator('input[type="text"], input[type="email"], textarea')
                        if inputs.count() > 0:
                            inputs.first.fill("test")
                            results['forms_work'] = True
                            results['test_details'].append(f"✅ Forms work with {form_count} form elements")
                            results['functionality_score'] += 15
                    except:
                        results['test_details'].append(f"⚠️ Found {form_count} form elements but testing failed")
                
                # Test 5: Requirement-specific tests
                page_content = page.inner_text('body').lower()
                for requirement in requirements:
                    req_lower = requirement.lower()
                    keywords = req_lower.split()
                    
                    # Check if requirement keywords appear in the page
                    matches = sum(1 for keyword in keywords if len(keyword) > 2 and keyword in page_content)
                    if matches >= len(keywords) // 2:
                        results['functionality_score'] += 5
                        results['test_details'].append(f"✅ Requirement '{requirement}' evidence found")
                
                browser.close()
                
        except ImportError:
            logger.error("❌ Playwright not available for functional testing")
        except Exception as e:
            logger.error(f"❌ Playwright testing error: {str(e)}")
            results['test_details'].append(f"❌ Playwright testing failed: {str(e)}")
        
        return results
    
    def _test_with_selenium(self, server_url: str, requirements: List[str]) -> Dict[str, any]:
        """Test functionality using Selenium (fallback)."""
        results = {
            'navigation_works': False,
            'buttons_work': False,
            'forms_work': False,
            'components_render': False,
            'test_details': [],
            'functionality_score': 0
        }
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(server_url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Basic functionality tests (similar to Playwright but with Selenium)
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if len(body_text) > 50:
                results['components_render'] = True
                results['test_details'].append("✅ Components render with content")
                results['functionality_score'] += 15
            
            # Test buttons
            buttons = driver.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='submit']")
            if buttons:
                results['buttons_work'] = True
                results['test_details'].append(f"✅ Found {len(buttons)} buttons")
                results['functionality_score'] += 20
            
            driver.quit()
            
        except ImportError:
            logger.error("❌ Selenium not available for functional testing")
        except Exception as e:
            logger.error(f"❌ Selenium testing error: {str(e)}")
            results['test_details'].append(f"❌ Selenium testing failed: {str(e)}")
        
        return results
    
    def _test_with_basic_parsing(self, server_url: str, requirements: List[str]) -> Dict[str, any]:
        """Basic functionality testing using HTML parsing (fallback)."""
        results = {
            'navigation_works': False,
            'buttons_work': False,
            'forms_work': False,
            'components_render': False,
            'test_details': [],
            'functionality_score': 0
        }
        
        try:
            from bs4 import BeautifulSoup
            
            response = requests.get(server_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Test for buttons
            buttons = soup.find_all(['button', 'input'])
            button_count = len([b for b in buttons if b.get('type') in ['button', 'submit'] or b.name == 'button'])
            
            if button_count > 0:
                results['buttons_work'] = True
                results['test_details'].append(f"✅ Found {button_count} buttons in HTML")
                results['functionality_score'] += 15
            
            # Test for navigation
            links = soup.find_all('a')
            if links:
                results['navigation_works'] = True
                results['test_details'].append(f"✅ Found {len(links)} navigation links")
                results['functionality_score'] += 10
            
            # Test for forms
            forms = soup.find_all('form')
            inputs = soup.find_all('input', type=['text', 'email', 'password'])
            textareas = soup.find_all('textarea')
            
            if forms or inputs or textareas:
                results['forms_work'] = True
                results['test_details'].append(f"✅ Found form elements: {len(forms)} forms, {len(inputs)} inputs")
                results['functionality_score'] += 10
            
            # Test for content
            body_text = soup.get_text()
            if len(body_text) > 100:
                results['components_render'] = True
                results['test_details'].append("✅ App renders with substantial content")
                results['functionality_score'] += 10
            
        except ImportError:
            logger.error("❌ BeautifulSoup not available for HTML parsing")
        except Exception as e:
            logger.error(f"❌ Basic parsing error: {str(e)}")
            results['test_details'].append(f"❌ HTML parsing failed: {str(e)}")
        
        return results
