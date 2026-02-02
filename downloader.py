#!/usr/bin/env python3
"""
Downloader module for downloading WAV files from YouTube via y2down.cc
Based on test_downloadsample.py workflow
"""

import logging
import time
import os
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests

logger = logging.getLogger(__name__)

# Module identifier to confirm we're using the correct downloader
MODULE_PATH = os.path.abspath(__file__)
logger.info(f"Loaded downloader module from: {MODULE_PATH} (y2down.cc version)")


def wait_for_window(driver, window_handles_before, timeout=2):
    """Wait for a new window to open."""
    time.sleep(round(timeout / 1000))
    wh_now = driver.window_handles
    if len(wh_now) > len(window_handles_before):
        return set(wh_now).difference(set(window_handles_before)).pop()
    return None


def get_download_url(youtube_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get download URL from y2down.cc using Selenium automation.
    Based on test_downloadsample.py workflow.
    
    Args:
        youtube_url: YouTube video URL to download
        
    Returns:
        Tuple of (download_url, video_title) or (None, None) on error
    """
    driver = None
    try:
        base_url = "https://y2down.cc/enV8/youtube-wav"
        logger.info(f"Starting download process for: {youtube_url}")
        
        # Setup Chrome options for headless browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Setup download preferences to intercept download URLs
        prefs = {
            "download.default_directory": "/tmp",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"ChromeDriverManager failed: {e}, trying default Chrome")
            driver = webdriver.Chrome(options=chrome_options)
        
        logger.info("Headless browser started")
        
        # Navigate to y2down.cc
        driver.get(base_url)
        logger.info(f"Loaded page: {driver.current_url}")
        
        wait = WebDriverWait(driver, 20)
        
        # Step 1: Click the input URL field
        try:
            input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".input-url")))
            input_field.click()
            logger.info("Clicked input URL field")
        except TimeoutException:
            logger.error("Could not find .input-url field")
            return None, None
        
        # Step 2: Select WAV format from dropdown
        try:
            quality_btn = driver.find_element(By.CSS_SELECTOR, ".btn-quality")
            quality_btn.click()
            logger.info("Clicked quality button")
            
            # Select WAV option
            wav_option = driver.find_element(By.XPATH, "//option[. = 'WAV']")
            wav_option.click()
            logger.info("Selected WAV format")
            
            # Also click the specific option mentioned in test script
            try:
                specific_option = driver.find_element(By.CSS_SELECTOR, "optgroup:nth-child(2) > option:nth-child(8)")
                specific_option.click()
            except:
                pass
        except Exception as e:
            logger.warning(f"Error selecting WAV format: {e}")
        
        # Step 3: Click input field again and enter YouTube URL
        try:
            input_field = driver.find_element(By.CSS_SELECTOR, ".input-url")
            input_field.click()
            input_field.clear()
            input_field.send_keys(youtube_url)
            logger.info(f"Entered YouTube URL: {youtube_url}")
        except Exception as e:
            logger.error(f"Error entering URL: {e}")
            return None, None
        
        # Step 4: Click the load button
        window_handles_before = driver.window_handles
        try:
            load_button = driver.find_element(By.CSS_SELECTOR, "#load > span")
            load_button.click()
            logger.info("Clicked load button")
        except Exception as e:
            logger.error(f"Error clicking load button: {e}")
            return None, None
        
        # Step 5: Wait for new window and handle it
        time.sleep(2)
        new_window = wait_for_window(driver, window_handles_before, 2000)
        if new_window:
            root_window = driver.current_window_handle
            driver.switch_to.window(new_window)
            logger.info("Switched to new window")
            driver.close()
            driver.switch_to.window(root_window)
            logger.info("Closed new window and switched back")
        
        # Wait for page to process
        time.sleep(5)
        
        # Step 6: Click download button and get download URL
        try:
            download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-download:nth-child(3) > span")))
            
            # Before clicking, try to get the download URL from the button's attributes or page
            download_url = None
            video_title = None
            
            # Check if button has href or data attributes
            try:
                href = download_button.get_attribute('href')
                if href and href.startswith('http'):
                    download_url = href
            except:
                pass
            
            # If no href, check parent element
            if not download_url:
                try:
                    parent = download_button.find_element(By.XPATH, "..")
                    href = parent.get_attribute('href')
                    if href and href.startswith('http'):
                        download_url = href
                except:
                    pass
            
            # If still no URL, click and check page source or network
            if not download_url:
                download_button.click()
                logger.info("Clicked download button")
                
                # Wait longer for page to process and download link to appear
                time.sleep(5)
                
                # Check current URL - might have redirected to download
                current_url = driver.current_url
                if current_url != base_url and any(ext in current_url.lower() for ext in ['.wav', '.mp3', '.mp4', 'savenow', 'download']):
                    download_url = current_url
                    logger.info(f"Redirected to download URL: {download_url}")
                else:
                    # Wait a bit more and check again
                    time.sleep(3)
                    current_url = driver.current_url
                    if current_url != base_url and 'y2down.cc/en' not in current_url:
                        # Check if it's a download URL
                        if any(keyword in current_url.lower() for keyword in ['download', 'get', 'file', 'savenow', 'pacific']):
                            download_url = current_url
                            logger.info(f"Found download URL after redirect: {download_url}")
                    
                    # Try to find download link in page source with more patterns
                    if not download_url:
                        page_source = driver.page_source
                        import re
                        patterns = [
                            r'https?://[^\s"\'<>]+\.wav',
                            r'https?://[^\s"\'<>]*savenow[^\s"\'<>]+',
                            r'https?://[^\s"\'<>]*pacific[^\s"\'<>]+',
                            r'["\'](https?://[^"\']*download[^"\']*\.wav[^"\']*)["\']',
                            r'["\'](https?://[^"\']*savenow[^"\']*)["\']',
                            r'downloadUrl["\']?\s*[:=]\s*["\'](https?://[^"\']+)["\']',
                            r'href\s*=\s*["\'](https?://[^"\']*download[^"\']*)["\']',
                            r'window\.location\s*=\s*["\'](https?://[^"\']+)["\']',
                        ]
                        for pattern in patterns:
                            matches = re.findall(pattern, page_source, re.IGNORECASE)
                            for match in matches:
                                if match and len(match) > 30:
                                    # Filter out ad/tracking URLs
                                    if any(exclude in match.lower() for exclude in ['/ajax/ad/', '/ad/', 'tracking', 'analytics', 'pixel']):
                                        continue
                                    # Prioritize URLs that look like actual download links
                                    if any(keyword in match.lower() for keyword in ['pacific', '.wav', '?']):
                                        download_url = match
                                        logger.info(f"Found download URL in page source: {download_url}")
                                        break
                                    # Fallback to other savenow URLs (but not ad URLs)
                                    elif 'savenow' in match.lower() and '/ajax/' not in match.lower():
                                        download_url = match
                                        logger.info(f"Found download URL in page source: {download_url}")
                                        break
                            if download_url:
                                break
                        
                        # Also check all links on the page
                        if not download_url:
                            try:
                                all_links = driver.find_elements(By.TAG_NAME, "a")
                                for link in all_links:
                                    href = link.get_attribute('href')
                                    if href and href.startswith('http') and len(href) > 30:
                                        # Filter out ad/tracking URLs
                                        if any(exclude in href.lower() for exclude in ['/ajax/ad/', '/ad/', 'tracking', 'analytics']):
                                            continue
                                        # Prioritize actual download URLs
                                        if any(keyword in href.lower() for keyword in ['pacific', '.wav', '?']):
                                            download_url = href
                                            logger.info(f"Found download URL in link element: {download_url}")
                                            break
                                        # Fallback to other savenow URLs (but not ad URLs)
                                        elif 'savenow' in href.lower() and '/ajax/' not in href.lower():
                                            download_url = href
                                            logger.info(f"Found download URL in link element: {download_url}")
                                            break
                            except Exception as e:
                                logger.debug(f"Error checking links: {e}")
            
            # Try to get video title
            try:
                title_element = driver.find_element(By.CSS_SELECTOR, "h1, .title, [class*='title']")
                video_title = title_element.text
            except:
                pass
            
            if download_url:
                logger.info(f"Successfully obtained download URL: {download_url}")
                return download_url, video_title
            else:
                logger.warning("Could not extract download URL")
                return None, None
                
        except TimeoutException:
            logger.error("Download button not found or not clickable")
            return None, None
        except Exception as e:
            logger.error(f"Error getting download URL: {e}")
            return None, None
            
    except Exception as e:
        logger.error(f"Error in download process: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def stream_download(download_url: str, chunk_size: int = 8192):
    """
    Stream download from a URL.
    
    Args:
        download_url: URL to download from
        chunk_size: Size of chunks to stream
        
    Yields:
        Chunks of file data
    """
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Referer': 'https://y2down.cc/',
        })
        
        response = session.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
                
    except Exception as e:
        logger.error(f"Error streaming download: {e}")
        raise

