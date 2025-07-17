import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, redirect, request, session, url_for
import os
import time
import serial
import serial.tools.list_ports
import threading
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = "user-read-playback-state user-read-currently-playing"

token_info = None
last_track_info = {"name": None, "artist": None}

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

ser = None

TOKEN_FILE = "spotify_token_info.json"

def save_token_info(token_data):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)
    print("Tokens saved to file.")

def load_token_info():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def get_spotify_oauth():
    return SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE,
                        cache_path=None)

def get_spotify_client():
    global token_info
    sp_oauth = get_spotify_oauth()

    if token_info:
        if sp_oauth.is_token_expired(token_info):
            print("Access token expired, refreshing...")
            new_token = sp_oauth.refresh_access_token(token_info['refresh_token'])
            if new_token:
                token_info = new_token
                save_token_info(token_info)
                print("Token refreshed.")
            else:
                print("Failed to refresh token. Re-authorization required.")
                token_info = None
    
    if not token_info:
        print("No token or failed refresh. Please authorize the application.")
        return None

    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/')
def index():
    global token_info
    token_info = load_token_info()

    if not token_info:
        sp_oauth = get_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        print(f"Open in your browser to authorize: {auth_url}")
        return redirect(auth_url)
    return "You are already authorized. You can close this page and run the Spotify monitor script."

@app.route('/callback')
def callback():
    global token_info
    code = request.args.get('code')
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)
    save_token_info(token_info)
    return "Authorization successful! You can close this page and run the Spotify monitor script."

def spotify_monitor_thread():
    global last_track_info, ser

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Successfully opened serial port {SERIAL_PORT} at {BAUD_RATE}.")
    except serial.SerialException as e:
        print(f"Error opening serial port {SERIAL_PORT}: {e}")
        print("Check if the port is correct and not in use.")
        print("Available ports:")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"- {p.device} ({p.description})")
        return

    print("Starting Spotify monitor...")
    while True:
        sp = get_spotify_client()
        if sp:
            try:
                current_playback = sp.current_playback()
                if current_playback and current_playback['is_playing'] and current_playback['item']:
                    track_name = current_playback['item']['name']
                    artist_name = current_playback['item']['artists'][0]['name'] if current_playback['item']['artists'] else "Unknown Artist"
                    
                    if track_name != last_track_info['name'] or artist_name != last_track_info['artist']:
                        last_track_info['name'] = track_name
                        last_track_info['artist'] = artist_name
                        
                        display_string = f"{track_name}|{artist_name}"
                        
                        try:
                            ser.write((display_string + '\n').encode('utf-8'))
                            print(f"Sent to microcontroller: {display_string}")
                        except serial.SerialException as e:
                            print(f"Error writing to serial port: {e}")
                            try:
                                ser.close()
                                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                                print(f"Re-opened port {SERIAL_PORT}.")
                            except serial.SerialException as e_reopen:
                                print(f"Failed to re-open port: {e_reopen}")
                                ser = None
                                time.sleep(5)
                                continue
                elif not current_playback:
                    if last_track_info['name'] is not None:
                        last_track_info['name'] = None
                        last_track_info['artist'] = None
                        try:
                            ser.write("Nothing playing|".encode('utf-8'))
                            print("Sent: Nothing playing")
                        except serial.SerialException as e:
                            print(f"Error writing to serial port (nothing playing): {e}")

            except spotipy.SpotifyException as e:
                print(f"Spotify API error: {e}")
                if "The access token expired" in str(e) or "Invalid access token" in str(e):
                    print("Spotify token expired or invalid. Re-authorization required.")
                else:
                    print(f"Other Spotify error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during Spotify monitoring: {e}")
        else:
            print("No Spotify authorization. Start Flask server and authorize.")
        
        time.sleep(3)

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=spotify_monitor_thread)
    monitor_thread.daemon = True
    monitor_thread.start()

    app.run(port=8888)