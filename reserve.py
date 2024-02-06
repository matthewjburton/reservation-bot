import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import schedule
import time

# Load environment variables from .env file
load_dotenv()

# Access environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
restaurant = os.getenv("RESTAURANT")
number_of_seats = os.getenv("SEATS")
preferred_time = os.getenv("TIME")

def select_restaurant(restaurant_url):
    if not restaurant_url:
        print("Restaurant URL not found.")
        return None
    
    session = login(restaurant_url)
    if session:
        reserve_table(session, number_of_seats, preferred_time)

def login(login_url, username, password):
    if not login_url:
        print("Login URL not found.")
        return None

    # Create a session to persist cookies across requests
    session = requests.Session()

    # Send a GET request to the login page to get CSRF token
    login_page_response = session.get(login_url)
    login_page_soup = BeautifulSoup(login_page_response.content, 'html.parser')

    # Extract the CSRF token from the login page
    csrf_token = login_page_soup.find('input', {'name': '_csrf'})['value']

    # Prepare the login data with CSRF token
    login_data = {
        'username': username,
        'password': password,
        '_csrf': csrf_token
    }

    # Send a POST request to login
    login_response = session.post(login_url, data=login_data)

    # Check if login was successful
    if login_response.status_code == 200:
        print("Login successful!")
        return session
    else:
        print("Login failed. Please check your credentials.")
        return None

def reserve_table(session, seats, time):
    # Base URL for making reservation
    reservation_url = 'https://finedining.highpoint.edu/1924-Prime/reservation'

    # Send a GET request to the reservation page to get the form data
    response = session.get(reservation_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the CSRF token from the form
    csrf_token = soup.find('input', {'name': '_csrf'})['value']

    # Extract the date from the form
    date_input = soup.find('input', {'name': 'date'})['value']

    # Prepare the reservation data
    reservation_data = {
        'picker_step': '2',
        'location': '2',
        'date': date_input,  # Use the extracted date
        'guest': seats,
        '_csrf': csrf_token
    }

    # Send a POST request to make the reservation
    reservation_response = session.post(reservation_url, data=reservation_data)

    # Check if reservation was successful
    if reservation_response.status_code == 200:
        print("Reservation successful!")
    else:
        print("Reservation failed.")

def main():
    # Define restaurant URLs
    restaurant_urls = {
        'Prime': 'https://finedining.highpoint.edu/1924-Prime/reservation',
        'Alo': 'https://finedining.highpoint.edu/alo/reservation',
        'Kazoku': 'https://finedining.highpoint.edu/kazoku/reservation',
    }

    # Get restaurant URL based on user input
    restaurant_url = restaurant_urls.get(restaurant)

    # Schedule reservation task
    schedule.every().day.at("00:00").do(select_restaurant, restaurant_url)

    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
