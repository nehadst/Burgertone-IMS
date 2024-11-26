from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class TouchBistroScraper:
    def __init__(self):
        # Initialize the Chrome WebDriver
        self.driver = webdriver.Chrome()  # Ensure PATH or full path is set

    def login(self, username, password):
        # Open the TouchBistro login page
        self.driver.get("https://www.touchbistro.com/login")
        time.sleep(2)

        # Find and fill the username and password fields
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

    def download_csv(self, date):
        # Navigate to the reports section
        self.driver.get("https://www.touchbistro.com/reports")
        time.sleep(2)

        # Set the date range (example for a single date)
        date_field = self.driver.find_element(By.ID, "datePicker")
        date_field.clear()
        date_field.send_keys(date)

        # Click the "Export CSV" button
        export_button = self.driver.find_element(By.XPATH, "//button[text()='Export CSV']")
        export_button.click()
        time.sleep(5)  # Wait for download to complete

    def close(self):
        self.driver.quit()

# Example Usage
if __name__ == "__main__":
    scraper = TouchBistroScraper()
    scraper.login("your_username", "your_password")
    scraper.download_csv("2024-11-01")
    scraper.close()
