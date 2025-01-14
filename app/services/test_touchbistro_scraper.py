import unittest
import os
from datetime import datetime, timedelta
from .touchbistro_scraper import TouchBistroScraper
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TestTouchBistroScraper(unittest.TestCase):
    def setUp(self):
        # Get the absolute path to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Build the absolute path to credentials
        self.test_credentials = os.path.join(project_root, "credentials", "burgertone-credentials.json")
        
        # Get environment variables with validation
        self.test_username = os.getenv("TOUCHBISTRO_TEST_USERNAME")
        if not self.test_username:
            raise ValueError("TOUCHBISTRO_TEST_USERNAME environment variable must be set in .env file")
            
        self.test_password = os.getenv("TOUCHBISTRO_TEST_PASSWORD")
        if not self.test_password:
            raise ValueError("TOUCHBISTRO_TEST_PASSWORD environment variable must be set in .env file")
            
        self.test_bucket = os.getenv("GCP_TEST_BUCKET", "test-bucket")
        
        # Print debug information
        print(f"Username set: {'Yes' if self.test_username else 'No'}")
        print(f"Password set: {'Yes' if self.test_password else 'No'}")
        print(f"Using credentials file: {self.test_credentials}")
        
        # Initialize scraper
        self.scraper = TouchBistroScraper(
            gcs_bucket_name=self.test_bucket,
            credentials_path=self.test_credentials
        )
    
    def tearDown(self):
        if hasattr(self, 'scraper'):
            self.scraper.close()

    def test_login(self):
        """Test login functionality"""
        try:
            self.scraper.login(self.test_username, self.test_password)
            current_url = self.scraper.driver.current_url
            self.assertIn("admin.touchbistro.com", current_url)
        except Exception as e:
            self.fail(f"Login failed with error: {e}")

    def test_download_report(self):
        """Test downloading a single report"""
        try:
            # Login first
            self.scraper.login(self.test_username, self.test_password)
            
            # Try downloading yesterday's report
            test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            self.scraper.download_report(test_date)
            
            # Check if file exists in GCS
            blob = self.scraper.bucket.blob(f"reports/{test_date}.csv")
            self.assertTrue(blob.exists())
        except Exception as e:
            self.fail(f"Download failed with error: {e}")

    def test_csv_validation(self):
        """Test CSV content validation"""
        test_date = "2025-01-12"
        
        # Download report
        self.scraper.login(self.test_username, self.test_password)
        self.scraper.download_report(test_date)
        
        # Get the CSV content from GCS
        blob = self.scraper.bucket.blob(f"reports/{test_date}.csv")
        content = blob.download_as_text()
        
        # Split into lines and clean up
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Look for sales total in the SALES TOTALS section
        sales_total = None
        in_sales_section = False
        
        for i, line in enumerate(lines):
            if 'SALES TOTALS' in line:
                in_sales_section = True
                continue
            
            if in_sales_section and '"$' in line:
                # Get the full line before splitting
                print(f"Processing line: {line}")
                
                # Extract the first quoted value
                if '"$' in line:
                    # Find the first complete quoted value
                    start = line.find('"$') + 1  # Skip the opening quote
                    end = line.find('"', start)  # Find the closing quote
                    if start > 0 and end > start:
                        value = line[start:end]  # Extract everything between quotes
                        print(f"Extracted value: {value}")
                        # Clean and convert to float
                        value = value.replace('$', '').replace(',', '')
                        try:
                            sales_total = float(value)
                            print(f"Converted to number: {sales_total}")
                            if sales_total > 100:  # Basic sanity check
                                break
                        except ValueError as e:
                            print(f"Error converting value: {e}")
                            continue
        
        self.assertIsNotNone(sales_total, "Could not find valid sales total")
        self.assertGreater(sales_total, 0, "Sales total should be greater than 0")
        
        # Verify it matches the expected total ($1,573.25)
        expected_total = 1573.25
        self.assertAlmostEqual(sales_total, expected_total, places=2,
                              msg=f"Expected total ${expected_total}, but found ${sales_total}")

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)
