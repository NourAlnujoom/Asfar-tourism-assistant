from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import random
import ollama
from datetime import datetime, timedelta
from dateutil import parser
from math import radians, cos, sin, sqrt, atan2
import joblib
import sqlite3
from contextlib import contextmanager
import joblib
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 
GOOGLE_MAPS_API = os.getenv("GOOGLE_MAPS_API")

app = Flask(__name__)

#___________________________________________________________________
# Database configuration
DATABASE_PATH = 'tourism_database.db'

# Database helper functions
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database and create tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create less_known_sites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS less_known_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collected_data_from_sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hour TEXT NOT NULL,
            site_name TEXT NOT NULL,
            count INTEGER NOT NULL
        )
    ''')
        
        conn.commit()
        print("Database initialized successfully!")

def get_all_sites():
    """Get all sites from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM less_known_sites')
        return cursor.fetchall()

def get_site_by_name(site_name):
    """Get a specific site by name"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM less_known_sites WHERE site_name = ?', (site_name,))
        return cursor.fetchone()

def get_sensor_data_by_site(site_name):
    """Retrieve sensor data for a given site"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM collected_data_from_sensors WHERE site_name = ?',
            (site_name,)
        )
        return cursor.fetchall()

def add_site(site_name, category, description):
    """Add a new site to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO less_known_sites (site_name, category, description) VALUES (?, ?, ?)',
                (site_name, category, description)
            )
            conn.commit()
            return True, "Site added successfully!"
        except sqlite3.IntegrityError:
            return False, "Site already exists!"

def add_sensor_data(date, hour, site_name, count):
    """Add a new sensor data entry to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO collected_data_from_sensors (date, hour, site_name, count)
            VALUES (?, ?, ?, ?)
            ''',
            (date, hour, site_name, count)
        )
        conn.commit()
        return True

def update_site(site_id, site_name, category, description):
    """Update an existing site"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE less_known_sites SET site_name = ?, category = ?, description = ? WHERE id = ?',
            (site_name, category, description, site_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_site(site_name):
    """Delete a site from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM less_known_sites WHERE site_name = ?', (site_name,))
        conn.commit()
        return cursor.rowcount > 0

def clear_sites_table():
    """Delete all rows from the less_known_sites table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM less_known_sites')
        conn.commit()

# Initialize database on startup
init_database()
#___________________________________________________________________


if os.path.exists("location_cache.json"):
    with open("location_cache.json", "r") as f:
        location_cache = json.load(f)
else:
    location_cache = {}


def run_model(prompt, role="user"):
    print('run_model function entered')
    response = ollama.chat(model='llama3', messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": role, "content": prompt}
    ])
    print(response)
    return response['message']['content']


def extract_info_using_llm(field, user_input):
    prompt = f"""
    You are an information extractor, I will give you a sentence and your job is to extract information from that sentence.
    "{user_input}" What is the user's {field}?
    Just answer with the {field} alone with no explanation. If not specified, say "None".
    """
    print(f"extract_info_using_llm is entered with field = {field}")
    print("from extract_info_using_llm, run_model will be entered")
    response = run_model(prompt)
    if 'None' in response: return None
    print(response)
    return response.strip()

def predict_crowd(site,time):
    if isinstance(time, str):  # If it's a string, parse it
        time = datetime.fromisoformat(time)
    date = datetime.today().date()
    visit_datetime = datetime.combine(date, time.time() if isinstance(time, datetime) else time)
    model = joblib.load("linear_regression_petramodel.pkl")
    scaler = joblib.load("scaler.pkl")

    df = pd.read_csv("petra_counts_to_august.csv", parse_dates=['datetime'])
    df['scaled_count'] = scaler.transform(df[['count']])
    idx = df.index[df['datetime'] == visit_datetime]
    idx = idx[0]
    n_hours = 24
    X_input = df['scaled_count'].iloc[idx - n_hours:idx].values.reshape(1, -1)
    pred_scaled = model.predict(X_input)[0]
    prediction = scaler.inverse_transform([[pred_scaled]])[0, 0]

    if prediction >= 80:  # Peak hours
        return "High"
    elif prediction < 10:
        return "Low"
    else:
        return "Moderate"

def save_location_cache():
    with open("location_cache.json", "w") as f:
        json.dump(location_cache, f)


def get_coordinates(site):
    print("get_coordinates entered")
    site = site.lower().strip()
    print(f"[DEBUG] Fetching coordinates for site: {site}")
    if site in location_cache:
        print(f"[DEBUG] Found in cache: {location_cache[site]}")
        return location_cache[site] #to reduce api calls
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": site,
        "key": GOOGLE_MAPS_API
    }
    response = requests.get(url, params=params).json()

    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        lat, lon = location["lat"], location["lng"]
        location_cache[site] = (lat, lon)
        save_location_cache()
        return lat,lon
    return None, None


def get_todays_weather(site):
    print("get_todays_weather entered")
    lat, lon = get_coordinates(site)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,weathercode"
        "&timezone=auto"
    )
    response = requests.get(url)
    data = response.json()
    print(f"[DEBUG] Weather API called for {site} (lat: {lat}, lon: {lon})")
    times = data['hourly']['time']
    temps = data['hourly']['temperature_2m']
    codes = data['hourly']['weathercode']

    return times, temps, codes

def choose_weather(site, time, flag=False):
    # idea of the flag variable: to suggest another time with better temperature 
    # based on getting weather forcasting for times after the specified one
    # (check all hours > time until not hot) and before closing_time for that site
    date = datetime.today().date()
    print(f"date = {date}")
    visit_datetime = datetime.combine(date, time)
    print(f"visit_datetime = {visit_datetime}")
    target_time = visit_datetime.strftime("%Y-%m-%dT%H:00")
    print(f"target_time = {target_time}")
    times, temps, codes = get_todays_weather(site)
    if flag:
        print(f"[DEBUG] choose_weather entered with flag = {flag}")
        closing_time = datetime.combine(date, datetime.strptime("18:00", "%H:%M").time())
        print(f"closing_time = {closing_time}")
        print(f"times.index(target_time)+1 = {times.index(target_time)+1}")
        print(f"len(times) = {len(times)}")
        for perfect_time_index in range(times.index(target_time)+1,len(times)):
            forecast_time = datetime.fromisoformat(times[perfect_time_index])
            print(f'forecast_time = {forecast_time}')
            if forecast_time < closing_time and (temps[perfect_time_index] < 35 or codes[perfect_time_index] not in [61, 63, 65, 95]):
                return {
                "time": forecast_time,
                "temperature": temps[perfect_time_index],
                "weather_code": codes[perfect_time_index]
            }
            else:
                return None # ask user to avoid going that day

    elif target_time in times:
            idx = times.index(target_time)
            return {
                "temperature": temps[idx],
                "weather_code": codes[idx]
            }
    return None
    
#used to know if suggesting a better time is required
def analyze_weather(weather):
    temp = weather["temperature"]
    code = weather["weather_code"]
    print(f"[DEBUG] Analyzing weather: temp = {temp}, code = {code}")

    if temp > 35:
        return "very hot.", True
    elif code in [61, 63, 65, 95]:
        return "Rain or thunderstorms expected", True
    elif temp < 10:
        return "cold. suggest dressing warmly or considering indoor sites.", False
    else:
        return "good for a visit.", False


def haversine_distance(lat1, lon1, lat2, lon2):
    print(f"[DEBUG] Calculating distance between ({lat1},{lon1}) and ({lat2},{lon2})")
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # in km


def get_route_polyline_points(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_MAPS_API
    }
    response = requests.get(url, params=params).json()
    print(f"[DEBUG] Fetching route from {origin} to {destination}")
    if response["status"] != "OK":
        print(f"[ERROR] Directions API failed: {response}")
        return []
    
    points = []
    for step in response["routes"][0]["legs"][0]["steps"]:
        loc = step["end_location"]
        points.append((loc["lat"], loc["lng"]))
    return points


def filter_sites_on_the_way(user_location, lesser_known_sites, site):
    print(f"[DEBUG] User location: {user_location}")
    print(f"[DEBUG] Main site: {site}")
    print(f"[DEBUG] Available lesser known sites: {lesser_known_sites}")
    origin_coords = get_coordinates(user_location)
    dest_coords = get_coordinates(site)
    if not origin_coords or not dest_coords:
        print(f"[DEBUG] Origin coords: {origin_coords}, Dest coords: {dest_coords}, place is not found on google maps")
        return None #the place is not found on google maps

    route_points = get_route_polyline_points(user_location, site)
    if not route_points:
        print(f"[DEBUG] Route points: {route_points}")
        return None #i dont know what could be the problem 
        #If it's None, the issue is inside get_route_polyline_points() — you may want to log the response or error from the API there.
    
    on_the_way = []
    distance= {}
    for lesser_site in lesser_known_sites:
        site_coords = get_coordinates(lesser_site)
        if not site_coords: continue
        for route_lat, route_lon in route_points:
            dist = haversine_distance(site_coords[0], site_coords[1], route_lat, route_lon)
            distance[lesser_site] = dist
            if dist < 5:  # within 5km of the route
                on_the_way.append(lesser_site)
                break

    print(f"[DEBUG] Distance map: {distance}, On-the-way sites: {on_the_way}")
    print(f"[DEBUG] Lesser-known site '{lesser_site}' distance = {dist} km")
    if on_the_way:
        return random.choice(on_the_way)
    else:
        # return the site with the least distination
        return min(distance, key=distance.get)


def query_site_info(site):
    print(f"[DEBUG] Querying info for site: {site}")    
    site_data = get_site_by_name(site)
    if site_data:
        return (site_data['description'], site_data['category'])
    else:
        return ("a place of interest", "General")


def build_prompt(site, time, crowd_level, weather, suggested_site):
    print('build_prompt emtered')
    print(f'site = {site}')
    print(f'time = {time}')
    print(f'crowd = {crowd_level}')
    print(f'weather = {weather}')
    print(f'suggested_site = {suggested_site}')
    
    if isinstance(time, str):
        try:
            time = datetime.fromisoformat(time)
        except ValueError:
            print("[WARN] Time string not ISO format, skipping formatting.")
            pass

    if isinstance(time, datetime):
        time = time.strftime("%I:%M %p")
        
    weather_descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 
        61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Light snow", 95: "Thunderstorm"
    }

    prompt = """You are a helpful tourism assistant for visitors to Jordan, You previously said:
    "Hello! I'm your Jordan travel assistant.Please enter the place you plan to visit,
    your intended time, and your current location. I'll help you find the best time to go and
    suggest other interesting stops along the way."
    Now, the user has provided all the required information.
    Do not talk too much, be professional.
    Thank them for sharing these details, and proceed to offer personalized advice based on their input.\n
    """
   
    text, flag = analyze_weather(weather)
    prompt += f"\nAt {time}, the temperature at {site} is expected to be {weather['temperature']}°C, which is considered {text.lower()}."

    if flag: #weather is not good
        suggested_weather = choose_weather(site,time,flag)
        if suggested_weather == None:
            prompt += f"\nDue to unfavorable weather conditions, it is not advisable to visit {site} today."
            crowd_level = 'low'
        else:
            weather_desc = weather_descriptions.get(suggested_weather["weather_code"], "unavailable")
            prompt += (
                f"\nInstead, I recommend visiting {site} at {suggested_weather['time']}, "
                f"when weather conditions are expected to be more suitable. "
                f"The weather at that time is described as: {weather_desc}."
            )
            crowd_level = predict_crowd(site,suggested_weather['time'])
            if crowd_level == "High":
                prompt += (
                    f" However, please note that {site} is expected to be very crowded at that time. "
                    "If you prefer a less crowded experience, you may wish to postpone your visit."
                )
    else: #weather is good
        print("[DEBUG] Weather is suitable for visit")
        weather_desc = weather_descriptions.get(weather["weather_code"], "unavailable")
        prompt += f"\nThe weather is generally suitable for visiting. Conditions are described as: {weather_desc}."

        print(f"[DEBUG] Initial crowd level = {crowd_level}")
        if crowd_level.lower() == 'high':
            print(f"[DEBUG] High crowd detected at {site} at {time}")
            prompt += f"\nHowever, {site} is expected to be very crowded at {time}."

            perfect_time = datetime.combine(datetime.today(), time)
            closing_time = datetime.strptime("18:00", "%H:%M")
            closing_datetime = datetime.combine(datetime.today(), closing_time.time())

            found_better_time = False
            while perfect_time <= closing_datetime:
                candidate_time = perfect_time.time()
                print(f"[DEBUG] Checking alternative time: {candidate_time}")
                alt_crowd = predict_crowd(site, candidate_time)
                print(f"[DEBUG] Predicted crowd at {candidate_time} = {alt_crowd}")
                if alt_crowd.lower() in ["moderate", "low"]:
                    found_better_time = True
                    break
                perfect_time += timedelta(hours=1)
            if found_better_time:
                prompt += f"\nTo avoid large crowds, I suggest visiting {site} at {perfect_time.time()} instead."
            else:
                print("[DEBUG] No less crowded time found before closing.")
                prompt += f"\nUnfortunately, it seems there is no less crowded time slot before closing hours."
        else:
            print("[DEBUG] Crowd level is not high, no alternative suggestion needed.")


    if suggested_site:
        desc, category = query_site_info(suggested_site)
        prompt += (
            f"\nAs an additional recommendation, you may consider visiting {suggested_site}, "
            f"a nearby destination known for {desc.lower()}. It is categorized under '{category.lower()}' "
            "and could enrich your journey."
        )
        prompt += "\n notes: 1.write times as AM/PM format not as given, and dont mention the date at all. 2.let this sentence be at the end of your answer: Have a wonderful time exploring Jordan. You are most welcome!"

    return prompt.strip()



def is_off_topic(user_input):
    print(f"[DEBUG] Checking if off-topic: {user_input}")
    prompt = f"""You are a strict tourism assistant focused on planning visits to places in Jordan.
    Decide if the following user message contains concrete information about at least one of:
    - the user's current location,
    - their planned time of visit,
    - or their desired destination in Jordan.

    If the message does NOT contain any of these, answer "Yes" (it is off-topic).
    If the message DOES contain at least one of these, answer "No" (it is on-topic).

    User message: "{user_input}"
    
    Answer with "Yes" or "No" only.
    """
    result = run_model(prompt).strip()
    print(f"[DEBUG] LLM response: {result}")
    return result.lower() == "yes"
    


def causal_talk(user_input):
    print(f"[DEBUG] Casual talk mode for input: {user_input}")
    prompt = f"""
    You are a helpful tourism assistant for visitors to Jordan, You previously said:
    "Hello! I'm your Jordan travel assistant.Please enter the place you plan to visit,
    your intended time, and your current location. I'll help you find the best time to go and
    suggest other interesting stops along the way.
    The user said: "{user_input}"
    Looks like the user is not providing any information and is talking to you about something else,
    Respond in a friendly, casual way. You are a chatbot assisting tourists in Jordan, so keep the reply short and light.
    and remind them to provide the information needed to find the best time to go and suggest other interesting stops along the way.

    note: you are not allowed to offer suggesting any of these 
    """
    response = run_model(prompt)
    return response.strip()


def generate_chatbot_response(user_input):
    print("[DEBUG] generate_chatbot_response entered")
    sites_data = get_all_sites()
    lesser_known_sites = [site['site_name'] for site in sites_data] 

    #extract target site and time from user_input
    user_location = extract_info_using_llm('current location',user_input)
    print(f"[DEBUG] Extracted user_location: {user_location}")
    time_raw = extract_info_using_llm('visit time',user_input)
    if time_raw is None:
        return """Please enter the place you plan to visit, your intended time, and your current location in one message. """
    time = parser.parse(time_raw).time()
    print(f"[DEBUG] Extracted visit time: {time_raw} → {time}")
    site = extract_info_using_llm('destination',user_input)
    print(f"[DEBUG] Extracted destination site: {site}")
    if not site or not user_location:
        return """Please enter the place you plan to visit, your intended time, and your current location in one message."""

    #predict crowd level at the site
    crowd_level = predict_crowd(site,time)
    print(f"[DEBUG] Predicted crowd level: {crowd_level}")

    #fetch weather from weatherAPI
    weather = choose_weather(site,time)
    print(f"[DEBUG] Weather info: {weather}")
    if weather is None:
        return f"I couldn't fetch the weather for {site}. Please check the site name."

    #use google maps to check which are on the way
    suggested_site = filter_sites_on_the_way(user_location, lesser_known_sites, site)
    print(f"[DEBUG] Suggested site: {suggested_site}")

    #build prompt dynamically based on all data
    prompt = build_prompt(site, time, crowd_level, weather, suggested_site)
    print(f"[DEBUG] Final prompt: \n{prompt}")

    #send to local llm
    response = run_model(prompt)
    print(f"[DEBUG] Final response from LLM: {response}")
    
    return response


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/audio-guide')
def audio_guide():
    return render_template('audio-guide.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        print(f"[DEBUG] Received user message: {user_message}")

        isofftopic = is_off_topic(user_message)
        print(f"[DEBUG] Off-topic check result: {isofftopic}")
        if isofftopic: response = causal_talk(user_message)

        else:
            response = generate_chatbot_response(user_message)

        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({
            'response': 'Sorry, I encountered an error. Please try again.',
            'status': 'error'
        }), 500

#_________________________________________________________________
# Database management routes
@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Get all sites from database"""
    try:
        sites = get_all_sites()
        return jsonify({
            'sites': [dict(site) for site in sites],
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sites', methods=['POST'])
def add_new_site():
    """Add a new site to database"""
    try:
        data = request.get_json()
        site_name = data.get('site_name')
        category = data.get('category')
        description = data.get('description')
        
        if not all([site_name, category, description]):
            return jsonify({
                'status': 'error', 
                'message': 'All fields (site_name, category, description) are required'
            }), 400
        
        success, message = add_site(site_name, category, description)
        
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sites/<int:site_id>', methods=['PUT'])
def update_existing_site(site_id):
    """Update an existing site"""
    try:
        data = request.get_json()
        site_name = data.get('site_name')
        category = data.get('category')
        description = data.get('description')
        
        if not all([site_name, category, description]):
            return jsonify({
                'status': 'error', 
                'message': 'All fields (site_name, category, description) are required'
            }), 400
        
        success = update_site(site_id, site_name, category, description)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Site updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Site not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sites/<int:site_id>', methods=['DELETE'])
def delete_existing_site(site_id):
    """Delete a site from database"""
    try:
        success = delete_site(site_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Site deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Site not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
#____________________________________________________________________________________________

if __name__ == '__main__':
    print("[INFO] Flask app is starting at http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 
