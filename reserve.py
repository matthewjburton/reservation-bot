import os
from dotenv import load_dotenv
import time
import datetime
import pytz  # Import pytz module for time zone handling
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# LOAD INPUT
# Load environment variables from .env file
load_dotenv()

# Access environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
phone = os.getenv("PHONE")
restaurant = os.getenv("RESTAURANT")
guests = os.getenv("GUESTS")
preferred_time = os.getenv("TIME")


# INPUT VALIDATION
# Phone
# Truncate the phone number if it's longer than 10 characters
if len(phone) > 10:
    phone = phone[:10]

# Restaurant
# Stop the program if the restaurant is not in the list of avaiable restaurants
if restaurant not in ('Prime', 'Alo', 'Kazoku'):
    print("Restaurant not found.")
    # Terminate the program
    sys.exit()

# Guests
# Stop the program if the number of guests is less than 1
if int(guests) < 1:
    print("Can't make a reservation for less than one guest.")
    # Terminate the program
    sys.exit()

# Define maximum number of guests for each restaurant
max_guests = {
    'Prime': 6,
    'Alo': 4,
    'Kazoku': 10
}

# Clamp the number of guests
guests = min(int(guests), max_guests.get(restaurant))
guests = str(guests)

# Time
# Define the minimum and maximum times as datetime objects
min_time = datetime.datetime.strptime("16:30", "%H:%M")
max_time = datetime.datetime.strptime("20:30", "%H:%M")

# Convert the preferred_time to a datetime object
preferred_time_dt = datetime.datetime.strptime(preferred_time, "%H:%M")

# Check if the preferred time falls within the available range
if preferred_time_dt < min_time:
    preferred_time_dt = min_time
if preferred_time_dt > max_time:
    preferred_time_dt = max_time

# Convert the preferred_time back to string format
preferred_time = preferred_time_dt.strftime("%H:%M")


# URL
# Define restaurant URLs
restaurant_urls = {
    'Prime' : 'https://finedining.highpoint.edu/1924-Prime/reservation',
    'Alo' : 'https://finedining.highpoint.edu/alo/reservation',
    'Kazoku' : 'https://finedining.highpoint.edu/kazoku/reservation',
}
url = restaurant_urls.get(restaurant)


def make_reservation():
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    try:
        # Open the website URL
        driver.get(url)


        # LOGIN
        # Find and fill in the login form
        username_field = driver.find_element(By.ID, "login-username")
        password_field = driver.find_element(By.ID, "login-password")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()


        # REDIRECT
        # See if the Prime image shows up again
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@alt='1924 PRIME']")))
        
        # After logging in
        if driver.current_url == "https://finedining.highpoint.edu/":
            # Navigate to the restaurant URL
            driver.get(url)
            print ("Login Successful.")


        # GUESTS
        # Find the dropdown element by its ID
        dropdown = Select(driver.find_element(By.ID,"noOfGuests"))

        # Select the option corresponding to the value set in the environment variable
        dropdown.select_by_value(guests)


        # DATE
        # Wait for the reservation form to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "picker-form")))

        # Get current UTC date
        current_date_utc = datetime.datetime.now(pytz.utc).date()

        #print(current_date_utc)

        # Add 7 days to the current UTC date
        seven_days_later_utc = current_date_utc + datetime.timedelta(days=7)

        #print(seven_days_later_utc)

        # Combine the date with the start of the day
        seven_days_later_utc_start_of_day = datetime.datetime.combine(seven_days_later_utc, datetime.time.min, tzinfo=pytz.utc)

        # Convert to Unix timestamp in milliseconds
        seven_days_ahead_timestamp = int(seven_days_later_utc_start_of_day.timestamp() * 1000)

        #print(seven_days_ahead_timestamp)

        date_td = driver.find_element(By.XPATH, f"//td[@data-date='{seven_days_ahead_timestamp}']")
        date_td.click()


        # FIND TABLE
        # Wait for the progress indicator to disappear
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "progress-indicator")))

        # Find and click the button
        find_table_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", find_table_button)  # Scroll to the button
        find_table_button.click()

        
        # TIME
        # Combine the date and time into the desired format
        combined_datetime_str = f"{seven_days_later_utc.strftime('%Y-%m-%d')} {preferred_time}"

        # Parse the combined datetime string into a datetime object     
        combined_datetime = datetime.datetime.strptime(combined_datetime_str, "%Y-%m-%d %H:%M")

        # Find all button elements
        buttons = driver.find_elements(By.XPATH, "//button[@class='timeslot btn btn-primary']")

        # Initialize variables to store the closest button and its difference in time
        closest_button = None
        min_time_diff = datetime.timedelta(seconds=999999999)

        # Iterate over each button element
        for button in buttons:
            # Extract the time value from the button
            button_time_str = button.get_attribute("value")
            button_time = datetime.datetime.strptime(button_time_str, "%Y-%m-%d %H:%M")
            
            # Extract the available seats from the corresponding paragraph element
            seats_paragraph = button.find_element(By.XPATH, "./following-sibling::p")
            available_seats = int(seats_paragraph.text.split()[0])
            
            # Check if the button is enabled and has enough available seats
            if available_seats >= int(guests) and button.is_enabled():
                # Calculate the difference in time
                time_diff = abs(combined_datetime - button_time)
                
                # Update the closest button if the time difference is smaller
                if time_diff.total_seconds() < min_time_diff.total_seconds():
                    min_time_diff = time_diff
                    closest_button = button

        # Click the closest button
        if closest_button:
            closest_button.click()
        else:
            print("No suitable time found.")
            # Terminate the program
            sys.exit()
        

        # PHONE
        # Find the telephone input field by its ID
        telephone_input = driver.find_element(By.ID, "telephone")

        # Clear any existing value in the input field (optional)
        telephone_input.clear()

        # Send the phone number to the input field
        telephone_input.send_keys(phone)
        
        
        # COMPLETE RESERVATION
        # Find the "Complete Reservation" button by its class name
        complete_reservation_button = driver.find_element(By.CLASS_NAME, "btn.btn-primary.btn-block.btn-lg")

        # Click the "Complete Reservation" button
        complete_reservation_button.click()
        
        print("Reservation successful!")
        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False
    
    finally:
        # Close the browser window
        driver.quit()

def main():
    # The maximum number of attempts to make a reservation
    maximum_attempts = 5

    # A counter to track how many attempts have been made at making a reservation
    attempt_counter = 0

    # Tracks whether a reservation has been made
    reservation_made = False

    # Wait to make a reservation until it is midnight
    while not reservation_made and attempt_counter < maximum_attempts:

        # Get current time
        current_time = datetime.datetime.now().time()

        # Check if current time is midnight
        if current_time.hour == 14 and current_time.minute == 37:
            
            # Attempt to make a reservation
            reservation_made = make_reservation()

            # Increment the attempt counter
            attempt_counter += 1 

            # Continue to attempt to make a reservation up to five times
            while not reservation_made and attempt_counter < maximum_attempts:
                # Wait for 1 minute before checking again
                time.sleep(60)       

                # Try to make another reservation
                reservation_made = make_reservation()  

                # Increment the attempt counter
                attempt_counter += 1     

if __name__ == "__main__":
    main()
