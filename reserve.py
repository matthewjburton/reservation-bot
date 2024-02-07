import os
from dotenv import load_dotenv
import time
import datetime
import pytz  # Import pytz module for time zone handling
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from .env file
load_dotenv()

# Access environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
restaurant = os.getenv("RESTAURANT")
number_of_seats = os.getenv("SEATS")
preferred_time = os.getenv("TIME")

# Define restaurant URLs
restaurant_urls = {
    'Prime': os.getenv("PRIME_RESERVATION_URL"),
    'Alo': os.getenv("ALO_RESERVATION_URL"),
    'Kazoku': os.getenv("KAZOKU_RESERVATION_URL"),
}

def make_reservation():
    url = restaurant_urls.get(restaurant)
    
    if not url:
        print("Restaurant URL not found.")
        return None

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    try:
        # Open the website URL
        driver.get(url)

        # Find and fill in the login form
        username_field = driver.find_element(By.ID, "login-username")
        password_field = driver.find_element(By.ID, "login-password")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # See if the prime image shows up again
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@alt='1924 PRIME']")))
        
        # After logging in
        if driver.current_url == "https://finedining.highpoint.edu/":
            # Navigate to the restaurant URL
            driver.get(url)
            print ("Redirecting to reservation page.")

        # Wait for the reservation form to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "picker-form")))

        print ("Login successful.")

        # Get current UTC date
        current_date_utc = datetime.datetime.now(pytz.utc).date()

        # Add 7 days to the current UTC date
        seven_days_later_utc = current_date_utc + datetime.timedelta(days=6)

        # Combine the date with the start of the day
        seven_days_later_utc_start_of_day = datetime.datetime.combine(seven_days_later_utc, datetime.time.min, tzinfo=pytz.utc)

        # Convert to Unix timestamp in milliseconds
        seven_days_ahead_timestamp = int(seven_days_later_utc_start_of_day.timestamp() * 1000)

        date_td = driver.find_element(By.XPATH, f"//td[@data-date='{seven_days_ahead_timestamp}']")
        date_td.click()

        # Wait for the new HTML to be loaded after selecting the date
        WebDriverWait(driver, 10).until(EC.staleness_of(date_td))

        # Submit the reservation form
        #submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")  # Adjust the locator as needed
        #submit_button.click()

        print("Reservation successful!")
    
    except Exception as e:
        print(f"Error occurred: {e}")
    
    #finally:
        # Close the browser window
        driver.quit()

def main():
    make_reservation()

if __name__ == "__main__":
    main()
