#!/usr/bin/env python3
"""
Vodafone Ultra Hub 7 Router Restart Automation Script
This script automates the restart process for the Vodafone Ultra Hub 7 router.
Designed to run unattended via cron.
"""

import sys
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuration
ROUTER_URL = "http://192.168.1.1"
ROUTER_PASSWORD = "YOUR_ROUTER_PASSWORD_HERE"  # Replace with your actual password
LOG_FILE = "/var/log/vodafone_router_restart.log"
TIMEOUT = 30

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_driver():
    """Configure and return a headless Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT)
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        sys.exit(1)


def login_to_router(driver):
    """Log into the router interface"""
    try:
        logger.info(f"Navigating to router login page: {ROUTER_URL}")
        driver.get(ROUTER_URL)
        
        # Wait for password field to be present
        password_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        
        logger.info("Entering password")
        password_field.clear()
        password_field.send_keys(ROUTER_PASSWORD)
        
        # Find and click login button
        login_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        
        logger.info("Clicking login button")
        login_button.click()
        
        # Wait for successful login by checking for Settings menu
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Settings')]"))
        )
        
        logger.info("Successfully logged in")
        return True
        
    except TimeoutException as e:
        logger.error(f"Login timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False


def navigate_to_restart_page(driver):
    """Navigate to the restart settings page"""
    try:
        restart_url = f"{ROUTER_URL}/settings/restart.jst"
        logger.info(f"Navigating to restart page: {restart_url}")
        driver.get(restart_url)
        
        # Wait for the restart button to be present
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Restart')]"))
        )
        
        logger.info("Restart page loaded successfully")
        return True
        
    except TimeoutException as e:
        logger.error(f"Failed to load restart page: {e}")
        return False
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return False


def restart_router(driver):
    """Click the restart button to reboot the router"""
    try:
        # Find the router restart button (not the factory reset button)
        # The restart button is in the "Router" section
        restart_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, 
                "//div[contains(., 'Click here to restart your router')]//following::button[contains(text(), 'Restart')][1]"))
        )
        
        logger.info("Clicking restart button")
        restart_button.click()
        
        # Wait a moment to ensure the action is processed
        time.sleep(2)
        
        # Check if there's a confirmation dialog and handle it
        try:
            confirm_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'OK') or contains(text(), 'Yes')]"))
            )
            logger.info("Confirmation dialog detected, confirming restart")
            confirm_button.click()
        except TimeoutException:
            logger.info("No confirmation dialog, restart initiated directly")
        
        logger.info("Router restart command sent successfully")
        return True
        
    except TimeoutException as e:
        logger.error(f"Failed to click restart button: {e}")
        return False
    except Exception as e:
        logger.error(f"Restart error: {e}")
        return False


def main():
    """Main execution function"""
    start_time = datetime.now()
    logger.info("=" * 70)
    logger.info(f"Vodafone Router Restart Script Started - {start_time}")
    logger.info("=" * 70)
    
    driver = None
    try:
        # Initialize browser
        driver = setup_driver()
        
        # Step 1: Login
        if not login_to_router(driver):
            logger.error("Failed to login to router")
            sys.exit(1)
        
        # Step 2: Navigate to restart page
        if not navigate_to_restart_page(driver):
            logger.error("Failed to navigate to restart page")
            sys.exit(1)
        
        # Step 3: Trigger restart
        if not restart_router(driver):
            logger.error("Failed to restart router")
            sys.exit(1)
        
        # Wait a bit to ensure command is processed
        time.sleep(3)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info(f"Router restart completed successfully in {duration:.2f} seconds")
        logger.info("Router is now rebooting. It may take 2-3 minutes to come back online.")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        if driver:
            driver.quit()
            logger.info("Browser session closed")


if __name__ == "__main__":
    main()

