import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime

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
url = restaurant_urls.get(restaurant)

def make_reservation():
    if not url:
        print("Restaurant URL not found.")
        return None
    
    # Create a session to persist cookies across requests
    session = requests.Session()

    session = login(session)
    if session:
        reservation_data = reserve_date(session, number_of_seats)
        if reservation_data:
            reserve_time(session, reservation_data, preferred_time)

def login(session):
    # Send a GET request to the login page to get CSRF token
    login_page_response = session.get(url)
    login_page_soup = BeautifulSoup(login_page_response.content, 'html.parser')

    # Extract the CSRF token from the login page
    csrf_input = login_page_soup.find('input', {'name': '_csrf'})
    csrf_token = csrf_input['value'] if csrf_input else None

    # Prepare the login data with CSRF token
    login_data = {
        'username': username,
        'password': password,
        '_csrf': csrf_token
    }

    # Send a POST request to login
    login_response = session.post(url, data=login_data)

    # Check if login was successful
    if login_response.status_code == 200:
        print("Login successful!")        
        return session
    else:
        print("Login failed. Please check your credentials.")
        return None

def reserve_date(session, seats):
    # Send a GET request to the reservation page to get the form data
    response = session.get(url)
    reservation_page_soup = BeautifulSoup(response.content, 'html.parser')

    # Find the form based on the action attribute
    reservation_form = reservation_page_soup.find('form', {'id': 'picker-form'})

    if not reservation_form:
        print("Form not found.")
        return None

    # Find the CSRF token in the meta tag
    csrf_token = reservation_page_soup.find('meta', {'name': 'csrf-token'})['content']

    # Prepare the reservation data
    reservation_data = {
        'picker_step': '2',
        'location': '2',
        'date': date,
        'guest': seats,
        '_csrf': csrf_token
    }

    # Send a POST request to make the reservation
    reservation_response = session.post(url, data=reservation_data)

    # Check if reservation was successful
    if reservation_response.status_code == 200:
        print("Date reservation successful!")
        return reservation_data  # Return reservation data for reserving time
    else:
        print("Date reservation failed.")
        return None

def reserve_time(session, reservation_data, time):
    # Construct the URL for reserving the time
    url += "?" + "&".join([f"{key}={value}" for key, value in reservation_data.items()])

    # Send a GET request to the reservation URL
    response = session.get(url)

    # Check if reservation was successful
    if response.status_code == 200:
        print("Time reservation successful!")
    else:
        print("Time reservation failed.")

def main():
    make_reservation()

    """
    # Get restaurant URL based on user input
    restaurant_url = restaurant_urls.get(restaurant)

    # Schedule reservation task
    schedule.every().day.at("00:00").do(make_reservation, restaurant_url)

    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
    """

if __name__ == "__main__":
    main()
