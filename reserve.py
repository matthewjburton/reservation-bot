import time
import datetime
import pytz  # Import pytz module for time zone handling
import tkinter as tk # Import tkinter for input GUI
from tkinter import ttk # Import ttk for dropdown menus
from tkinter import messagebox # Import messagebox to display success or failure

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Define maximum number of guests for each restaurant
max_guests = {
    'Prime': 6,
    'Alo': 4,
    'Kazoku': 10
}

# LOAD INPUT
def submit():
    # Retrieve user input from the entry widgets
    global username, password, phone, restaurant, guests, preferred_time  # Define these as global variables
    username = username_entry.get()
    password = password_entry.get()
    phone = phone_entry.get()
    restaurant = restaurant_combobox.get()
    guests = guests_combobox.get()
    preferred_time = time_combobox.get()

    # Convert time to military time
    hour, minute = map(int, preferred_time.split(":"))
    if hour != 12:
        hour += 12
    preferred_time = "{:02d}:{:02d}".format(hour, minute)

    # Close the Tkinter window
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Reservation System")

# Username
username_label = tk.Label(root, text="HPU Username:", font=("Helvetica", 12))
username_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
username_entry = tk.Entry(root, font=("Helvetica", 12))
username_entry.grid(row=0, column=1, padx=10, pady=5)

# Password
password_label = tk.Label(root, text="HPU Password:", font=("Helvetica", 12))
password_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
password_entry = tk.Entry(root, show="*", font=("Helvetica", 12))
password_entry.grid(row=1, column=1, padx=10, pady=5)

# Phone
phone_label = tk.Label(root, text="Phone:", font=("Helvetica", 12))
phone_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
phone_entry = tk.Entry(root, font=("Helvetica", 12))
phone_entry.grid(row=2, column=1, padx=10, pady=5)

# Restaurant
restaurant_label = tk.Label(root, text="Restaurant:", font=("Helvetica", 12))
restaurant_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
restaurant_combobox = ttk.Combobox(root, values=["Prime", "Alo", "Kazoku"], font=("Helvetica", 12), width=10)
restaurant_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
restaurant_combobox.current(0)  # Set the default value

# Guests
# Function to update the available guest options based on the selected restaurant
def update_guests_options(event):
    restaurant = restaurant_combobox.get()
    max_guest = max_guests.get(restaurant, 6)  # Default to 6 if the restaurant is not found
    guests_combobox.config(values=list(range(1, max_guest+1)))
    guests_combobox.current(max_guest - 1)  # Set default choice to the maximum number of guests

# Create a Combobox for selecting the number of guests
guests_label = tk.Label(root, text="Guests:", font=("Helvetica", 12))
guests_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
guests_combobox = ttk.Combobox(root, font=("Helvetica", 12), state="readonly", width=18)
guests_combobox.grid(row=4, column=1, padx=10, pady=5)

# Set up the event binding
restaurant_combobox.bind("<<ComboboxSelected>>", update_guests_options)

# Set default restaurant and update the available guest options
restaurant_combobox.current(0)  # Set default restaurant
update_guests_options(None)  # Update guest options based on default restaurant

# Time
# Define the available time options
times = ['4:30', '5:00', '5:30', '6:00', '6:30', '7:00', '7:30', '8:00', '8:30']

# Preferred Time
time_label = tk.Label(root, text="Preferred Time:", font=("Helvetica", 12))
time_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

# Create a Combobox for selecting the preferred time
time_combobox = ttk.Combobox(root, values=times, font=("Helvetica", 12), state="readonly", width=18)
time_combobox.grid(row=5, column=1, padx=10, pady=5)
time_combobox.current(2)  # Set the default value

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit, font=("Helvetica", 12), padx=20, pady=10)
submit_button.grid(row=6, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()


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


        # GUESTS
        # Find the dropdown element by its ID
        dropdown = Select(driver.find_element(By.ID,"noOfGuests"))

        # Select the option corresponding to the value set in the environment variable
        dropdown.select_by_value(guests)


        # DATE
        # Wait for the reservation form to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "picker-form")))

        # Get current date
        current_date = datetime.datetime.now().date()
        print(current_date)

        # Add 7 days to the current date
        seven_days_later = current_date + datetime.timedelta(days=7)
        print(seven_days_later)

        # Combine the date with the start of the day
        seven_days_later_start_of_day = datetime.datetime.combine(seven_days_later, datetime.time.min, tzinfo=pytz.utc)
        print(seven_days_later_start_of_day)

        seven_days_later_utc_start_of_day = seven_days_later_start_of_day.astimezone(pytz.utc)
        print(seven_days_later_utc_start_of_day)

        # Convert to Unix timestamp in milliseconds
        seven_days_ahead_timestamp = int(seven_days_later_utc_start_of_day.timestamp() * 1000)
        print(seven_days_ahead_timestamp)

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
        combined_datetime_str = f"{seven_days_later.strftime('%Y-%m-%d')} {preferred_time}"

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
            messagebox.showerror("Reservation failed", "No available time found.")
            return False
        

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

        return True

    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {e}")
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
        if current_time.hour == 0 and current_time.minute == 0:

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
    
    if reservation_made:
        # Show success message box
        reservation_details = f"Reservation successful!"
        messagebox.showinfo("Success", reservation_details)
    else:
        # Show failure message box
        messagebox.showerror("Failed", "A reservation could not be made.")

if __name__ == "__main__":
    main()
