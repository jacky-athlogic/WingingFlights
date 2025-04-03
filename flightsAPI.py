import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import time
import os

# Configuration
SERPAPI_KEY = "SERP_API_KEY"  # Replace with your SerpApi key
EMAIL_SENDER = "Your_email@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "APP_PASSWORD"   # Use an App Password if using Gmail
EMAIL_RECEIVER = "Receiver_email@email.com"  # Replace with receiver email - could be the same as sender email 
MAX_PRICE = 350 # What is the most in USD you'd want to spend on a flight
MIN_DURATION = 14 # What is the least amt of days you'd want to travel for
MAX_DURATION = 28 # What is the most amt of days you'd want to travel for 

# Major NYC airports (More airports/codes = more API requests = more $)
DEPARTURE_AIRPORTS = [
    "JFK", "LGA", "EWR"
    ]

# Major European airports (More airports/codes = more API requests = more $)
ARRIVAL_AIRPORTS = [
    "LHR", "CDG", "AMS", "FRA", "MUC", "MAD", "BCN", "FCO", "DUB", "ZRH",
    "CPH", "OSL", "ARN", "HEL", "VIE", "BRU", "LIS", "ATH", "PRG", "BUD"
]

def get_flight_data():
    today = datetime.now()
    results = []
    
    for origin in DEPARTURE_AIRPORTS:
        for destination in ARRIVAL_AIRPORTS:
            # Try different trip lengths between 14-28 days
            for days in range(MIN_DURATION, MAX_DURATION + 1):
                return_date = today + timedelta(days=days)
                
                params = {
                    "api_key": SERPAPI_KEY,
                    "engine": "google_flights",
                    "departure_id": origin,
                    "arrival_id": destination,
                    "outbound_date": today.strftime("%Y-%m-%d"),
                    "return_date": return_date.strftime("%Y-%m-%d"),
                    "currency": "USD",
                    "type": "1",  # Roundtrip
                    "max_price": str(MAX_PRICE)
                }
                
                try:
                    response = requests.get("https://serpapi.com/search", params=params)
                    data = response.json()
                    
                    if "best_flights" in data:
                        for flight in data["best_flights"]:
                            price = flight.get("price", float("inf"))
                            if price <= MAX_PRICE:
                                flight_info = {
                                    "origin": origin,
                                    "destination": destination,
                                    "price": price,
                                    "duration": days,
                                    "departure_date": today.strftime("%Y-%m-%d"),
                                    "return_date": return_date.strftime("%Y-%m-%d"),
                                    "google_flights_url": f"https://www.google.com/flights?hl=en#flt={origin}.{destination}.{today.strftime('%Y-%m-%d')}*{destination}.{origin}.{return_date.strftime('%Y-%m-%d')}"
                                }
                                results.append(flight_info)
                except Exception as e:
                    print(f"Error fetching data for {origin} to {destination}: {e}")
    
    return results

def send_email(flights):
    if not flights:
        subject = "No Cheap Flights Found Today"
        body = f"No roundtrip flights under ${str(MAX_PRICE)} found for trips between ${str(MIN_DURATION)}-${str(MAX_DURATION)} days."
    else:
        subject = f"Found {len(flights)} Cheap Flights from NYC to Europe!"
        body = "Here are today's cheap flight options:\n\n"
        for flight in flights:
            body += (f"From {flight['origin']} to {flight['destination']}: ${flight['price']}\n"
                    f"Trip Length: {flight['duration']} days\n"
                    f"Depart: {flight['departure_date']}, Return: {flight['return_date']}\n"
                    f"Book here: {flight['google_flights_url']}\n\n")
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
        
## This main() executes when code is run (easier for testing)
def main():
    print("Searching for flights...")
    flights = get_flight_data()
    send_email(flights)

## This main() executes daily at 5 AM est (I think)
# def main():
#     while True:
#         now = datetime.now()
#         # Schedule to run at 5 AM EST
#         target_time = now.replace(hour=5, minute=0, second=0, microsecond=0)
#         if now > target_time:
#             target_time += timedelta(days=1)
        
#         seconds_to_wait = (target_time - now).total_seconds()
#         print(f"Waiting {seconds_to_wait/3600:.2f} hours until 5 AM EST...")
#         time.sleep(seconds_to_wait)
        
#         print("Searching for flights...")
#         flights = get_flight_data()
#         send_email(flights)

if __name__ == "__main__":
    main()