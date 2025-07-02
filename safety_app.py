pip install yagmail

import streamlit as st
import yagmail
import datetime
import time
import threading
import webbrowser

# ------ CONFIG ------
TRUSTED_CONTACT_EMAILS = ['butwalgic@gmail.com', 'bhat.dittakavi@gmail.com']  # Change to actual emails
YOUR_EMAIL = 'butwalgic@gmail.com'    # Must be Gmail for yagmail
YOUR_EMAIL_APP_PASSWORD = 'Alwaaru7'  # Set up an app password in Google Account

# ------ EMAIL SENDER FUNCTION ------
def send_alert_email(location_url, eta):
    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_EMAIL_APP_PASSWORD)
    subject = "Safety Alert: Contact didn't arrive in time!"
    contents = [
        f"Alert! Your contact did not confirm arrival by the ETA: {eta}.",
        f"Last known location: {location_url}",
        "Please check in with them as soon as possible."
    ]
    yag.send(TRUSTED_CONTACT_EMAILS, subject, contents)

# ------ STREAMLIT APP ------
st.title("SafeCommute - Safety for College Girls in Butwal")
st.markdown("Share your live location and ETA. If you don't confirm arrival, your trusted contacts will be alerted automatically.")

user_name = st.text_input("Your Name")
contact_emails = st.text_input("Trusted Contacts' Emails (comma separated)", value=", ".join(TRUSTED_CONTACT_EMAILS))
eta = st.time_input("Set your ETA (Estimated Time of Arrival)", datetime.time(hour=datetime.datetime.now().hour + 1))

# JavaScript to get user location
get_location = st.button("Share My Current Location")

if get_location:
    st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const url = `https://www.google.com/maps?q=${lat},${lon}`;
            window.parent.postMessage({lat, lon, url}, "*");
        }
    );
    </script>
    """, unsafe_allow_html=True)
    st.info("Fetching location... Please allow location access.")

# Receive location from JS
location_url = st.session_state.get('location_url', None)
if 'location_url' not in st.session_state:
    st.session_state['location_url'] = None

def receive_location():
    # JavaScript communicates via window.postMessage, which Streamlit does not natively listen for.
    # For a real deployment, use a custom component or ask user to paste the URL generated in their browser.
    pass

st.markdown("""
**If prompted, please allow location access.**
""")

location_url_input = st.text_input("Or paste your Google Maps link here (from 'Share My Current Location')")

if location_url_input:
    st.session_state['location_url'] = location_url_input

if st.session_state['location_url']:
    st.success(f"Location shared! [View on Map]({st.session_state['location_url']})")

confirmed_arrival = st.checkbox("I have arrived at my destination")

def schedule_alert(eta, location_url):
    now = datetime.datetime.now()
    eta_dt = datetime.datetime.combine(now.date(), eta)
    if eta_dt < now:
        eta_dt += datetime.timedelta(days=1)  # If ETA is for next day
    wait_seconds = (eta_dt - now).total_seconds()
    time.sleep(wait_seconds)
    if not st.session_state.get('arrived', False):
        send_alert_email(location_url, eta_dt.strftime("%H:%M"))

if st.button("Start Safety Timer"):
    if not st.session_state['location_url']:
        st.error("Please share your location first.")
    else:
        st.success(f"Timer set! Alert will be sent if you don't confirm arrival by {eta.strftime('%H:%M')}.")
        st.session_state['arrived'] = False
        thread = threading.Thread(target=schedule_alert, args=(eta, st.session_state['location_url']))
        thread.start()

if confirmed_arrival:
    st.session_state['arrived'] = True
    st.success("Arrival confirmed. No alert will be sent.")

st.markdown("---")
st.caption("Built for the safety of college girls in Butwal. Stay safe!")
