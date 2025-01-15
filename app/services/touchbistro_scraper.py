from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime, timedelta
from google.cloud import storage
import requests
import json
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class TouchBistroScraper:
    def __init__(self, gcs_bucket_name, credentials_path):
        self.logger = logging.getLogger('TouchBistroScraper')
        # Initialize Google Cloud Storage client
        self.storage_client = storage.Client.from_service_account_json(credentials_path)
        self.bucket = self.storage_client.bucket(gcs_bucket_name)

        # Set up Selenium with Chrome (no headless)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        
        # Enable cookies
        chrome_options.add_argument("--enable-cookies")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_settings.cookies": 1,
            "profile.block_third_party_cookies": False,
            "download.default_directory": "/mnt/c/Users/nehad/Downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        })
        
        # Use the system-installed chromedriver
        service = Service("/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set base URL for reports
        self.base_url = "https://admin.touchbistro.com/venue-management/bases/36232/reports/dashboard/sales-dashboard"
        self.wait = WebDriverWait(self.driver, 20)

        # Add this line to debug Chrome options
        print("Chrome options:", chrome_options.arguments)

    def login(self, username, password):
        try:
            self.driver.get("https://login.touchbistro.com")
            
            # Wait up to 10 seconds for page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find username field using Okta's specific ID
            username_field = wait.until(EC.presence_of_element_located(
                (By.ID, "okta-signin-username")
            ))
            username_field.clear()
            username_field.send_keys(username)
            
            # Find password field using Okta's specific ID
            password_field = wait.until(EC.presence_of_element_located(
                (By.ID, "okta-signin-password")
            ))
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click the submit button using Okta's specific ID
            submit_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "okta-signin-submit")
            ))
            submit_button.click()
            
            # Wait for redirect after login
            wait.until(lambda driver: "admin.touchbistro.com" in driver.current_url)
            
            print("Successfully logged in!")
            
        except Exception as e:
            print(f"Error during login: {e}")
            self.driver.save_screenshot("login_error.png")
            print(f"Page source: {self.driver.page_source}")
            self.driver.quit()
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_report(self, date):
        try:
            # Navigate to the report page for the specified date
            report_url = f"{self.base_url}?start={date}&end={date}"
            print(f"Navigating to: {report_url}")
            self.driver.get(report_url)
            
            wait = WebDriverWait(self.driver, 30)
            
            # Wait for page load
            print("Waiting for page load...")
            wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                "[data-pw='dashboard-table']"
            )))
            
            # Find and click the reports dropdown
            print("Looking for reports dropdown...")
            button = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                "[data-pw='reports-options-dropdown']"
            )))
            
            # Click the reports dropdown
            print("Clicking reports dropdown...")
            self.driver.execute_script("arguments[0].click();", button)
            
            # Wait for menu to be present
            print("Waiting for menu to appear...")
            menu = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "ul.MuiList-root.MuiList-padding.MuiMenu-list"
            )))
            
            # Find Download option by exact path
            print("Looking for Download option...")
            download_item = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "li.MuiButtonBase-root.MuiMenuItem-root.tss-18xw57d-selectedMenuItemParent div.tss-brgrr8-itemStyle"
            )))
            
            # Verify it's the Download option by checking inner HTML
            inner_html = download_item.get_attribute('innerHTML')
            print(f"Found menu item with HTML: {inner_html}")
            
            if 'Download' in inner_html:
                print("Confirmed Download option, clicking...")
                # Click the parent li element
                parent = download_item.find_element(By.XPATH, "..")
                self.driver.execute_script("arguments[0].click();", parent)
            else:
                raise Exception("Found element but it's not the Download option")
            
            # Wait for CSV option menu
            print("Waiting for CSV option menu...")
            time.sleep(1)  # Short delay for menu transition
            
            # Find and click CSV option with more specific selector
            print("Looking for CSV option...")
            csv_option = wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//p[contains(text(), 'CSV')]"
            )))
            
            print("Found CSV option, clicking parent element...")
            parent = csv_option.find_element(By.XPATH, "..")
            self.driver.execute_script("arguments[0].click();", parent)
            
            # After clicking CSV
            print("Waiting for download to complete...")
            expected_filename = f"Burgertone-SalesDashboard-{date}-{date}.csv"
            
            # Use WSL path format
            download_path = f"/mnt/c/Users/nehad/Downloads/{expected_filename}"
            windows_path = f"C:\\Users\\nehad\\Downloads\\{expected_filename}"
            
            print(f"Looking for file in WSL path: {download_path}")
            print(f"Windows path equivalent: {windows_path}")
            
            # Wait up to 30 seconds for file
            timeout = time.time() + 30
            while time.time() < timeout:
                if os.path.exists(download_path):
                    print(f"Found downloaded file at: {download_path}")
                    break
                print("Waiting for download...", end="\r")
                time.sleep(2)
            else:
                print("\nDownload failed. Debug info:")
                print(f"Current URL: {self.driver.current_url}")
                print("Checking Downloads directory contents:")
                try:
                    for file in os.listdir("/mnt/c/Users/nehad/Downloads"):
                        print(f"- {file}")
                except Exception as e:
                    print(f"Error listing directory: {e}")
                raise Exception(f"Download timeout - file not found at {download_path}")
                
            # Upload to Google Cloud Storage
            print(f"Uploading file to GCS: reports/{date}.csv")
            blob = self.bucket.blob(f"reports/{date}.csv")
            
            print(f"Uploading file from: {download_path}")
            blob.upload_from_filename(download_path)
            
            # Verify upload
            if not blob.exists():
                raise Exception("File upload to GCS failed")
            
            print(f"Successfully uploaded to GCS: {blob.name}")
            
            # Clean up local file
            os.remove(download_path)
            
            return True
            
        except Exception as e:
            print(f"Error downloading report for {date}: {e}")
            self.driver.save_screenshot(f"error_screenshot_{date}.png")
            print(f"Current URL at error: {self.driver.current_url}")
            raise

    def upload_to_gcs(self, download_url, date):
        # Download the CSV file into memory
        try:
            response = requests.get(download_url)
            if response.status_code == 200:
                blob = self.bucket.blob(f"reports/{date}.csv")
                blob.upload_from_string(response.content)
                print(f"Uploaded report for {date} to GCS")
            else:
                print(f"Failed to download CSV for {date}")
        except Exception as e:
            print(f"Error uploading to GCS: {e}")

    def download_all_reports(self, start_date, end_date):
        """Download reports for a date range"""
        print(f"Starting bulk download from {start_date} to {end_date}")
        
        # Calculate total days
        total_days = (end_date - start_date).days + 1
        completed = 0
        
        current_date = start_date
        while current_date <= end_date:
            try:
                date_str = current_date.strftime("%Y-%m-%d")
                print(f"\nProcessing {date_str} ({completed}/{total_days})")
                
                # Check if report already exists
                blob = self.bucket.blob(f"reports/{date_str}.csv")
                if blob.exists():
                    print(f"Report for {date_str} already exists, skipping...")
                else:
                    # Download report
                    self.download_report(date_str)
                    print(f"Successfully downloaded report for {date_str}")
                
                completed += 1
                
                # Add a small delay between downloads
                time.sleep(2)
                
            except Exception as e:
                print(f"Error downloading report for {date_str}: {e}")
                # Continue with next date even if one fails
            
            current_date += timedelta(days=1)
        
        print(f"\nBulk download completed. Processed {completed}/{total_days} days")

    def close(self):
        self.driver.quit()

    def validate_csv(self, file_path):
        """Validate the downloaded CSV file"""
        try:
            with open(file_path, 'r') as f:
                # Read first few lines to verify format
                header = f.readline().strip().split(',')
                required_columns = ['Date', 'Sales', 'Items']  # Add your required columns
                
                if not all(col in header for col in required_columns):
                    raise ValueError(f"CSV missing required columns: {required_columns}")
                    
                # Verify file size
                if os.path.getsize(file_path) < 100:  # Minimum expected size
                    raise ValueError("CSV file appears to be empty or too small")
                    
            return True
        except Exception as e:
            print(f"CSV validation failed: {e}")
            return False

    def test_gcs_connection(self):
        """Test GCS connection and permissions"""
        try:
            test_blob = self.bucket.blob('test_connection')
            test_blob.upload_from_string('test')
            test_blob.delete()
            self.logger.info("GCS connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"GCS connection test failed: {e}")
            return False

    def test_download_report(self):
        date = "2025-01-12"
        self.scraper.download_report(date)
        
        # List all blobs in the bucket to see where file might be
        bucket = self.storage_client.bucket('burgertone')
        print("Files in bucket:")
        for blob in bucket.list_blobs():
            print(f"- {blob.name}")
        
        blob = bucket.blob(f"reports/{date}.csv")
        self.assertTrue(blob.exists())

# Usage Example
if __name__ == "__main__":
    username = "jamil.shikhtrab@gmail.com"  # TouchBistro login email
    password = "N/A"  # TouchBistro password
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 11)
    gcs_bucket_name = "burgertone"  # GCS bucket name
    credentials_path = "/mnt/c/Users/nehad/Burgertone-IMS/credentials/burgertone-credentials.json"  # JSON Credentials

    # Initialize the scraper
    scraper = TouchBistroScraper(gcs_bucket_name, credentials_path)
    
    try:
        # Test GCS connection first
        if not scraper.test_gcs_connection():
            raise Exception("Failed to connect to GCS")
            
        # Login to TouchBistro
        scraper.login(username, password)
        
        # Download and upload reports
        scraper.download_all_reports(start_date, end_date)
        
    except Exception as e:
        logging.error(f"Scraper failed: {e}")
    finally:
        scraper.close()