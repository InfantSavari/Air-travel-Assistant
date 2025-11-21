import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import hashlib
import json
from waitress import serve


load_dotenv(encoding='utf-8')

app = Flask(__name__)
CORS(app)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CACHE_FILE = "airport_cache.json"
REQUEST_DELAY = 1 

airport_cache = {}
try:
    with open(CACHE_FILE, 'r') as f:
        airport_cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pass


if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """You are an AI airport travel assistant specializing in global airport navigation. Provide:
1. Terminal/gate navigation tips
2. Security checkpoint advice
3. Lounge access information
4. Transportation options
5. Airport-specific amenities
6. Real-time guidance (when possible)
Keep responses under 150 words, factual, and include estimated walking times where applicable."""

def get_cache_key(query):
    return hashlib.md5(query.encode()).hexdigest()

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(airport_cache, f)

def get_ai_response(query):
    cache_key = get_cache_key(query)
    
    if cache_key in airport_cache:
        return airport_cache[cache_key]
    
    time.sleep(REQUEST_DELAY)
    
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{SYSTEM_PROMPT}\n\nQuery: {query}")
        result = response.text
        
        airport_cache[cache_key] = result
        save_cache()
        
        return result
    except Exception as e:
        if "quota" in str(e).lower():
            raise Exception("Service temporarily unavailable. Please try again later.")
        raise e

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def airport_api():
    try:
        data = request.get_json()
        user_query = data.get("query", "").strip()
        
        if not user_query:
            return jsonify({"reply": "Please enter your airport travel question."}), 400
        
        if not GEMINI_API_KEY:
            raise Exception("Service not configured")
        
        reply = get_ai_response(user_query)
        return jsonify({"reply": reply})
    
    except Exception as e:
        # Airport-specific fallbacks
        fallbacks = {
            "security": "⌛ Allow 30-45 mins for security. Pack liquids in clear bags (100ml max), remove laptops, wear easy-off shoes.",
            "lounge": "💺 Most lounges require business class tickets or priority pass. Day passes often available (~$50). Locations near gates: ",
            "connection": "🔄 Minimum connection times: Domestic 45mins, International 90mins. Use airport maps or ask staff for fastest routes.",
            "baggage": "🛄 Checked bags usually due 60mins pre-flight. Carry-on max typically 7kg (varies by airline)."
        }
        
        for term, answer in fallbacks.items():
            if term in user_query.lower():
                return jsonify({"reply": answer})
        
        return jsonify({
            "reply": "✈️ General tip: Arrive 2hrs early for domestic, 3hrs for international flights. Check airport maps for gate locations.",
            "error": str(e)
        }), 500
users = {}
sessions = {}
USER_DATA_FILE = "user_data.json"

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}
def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)        

users = load_users()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if username in users:
        return jsonify({"message": "Username already exists"}), 400

    users[username] = {
        "email": email,
        "password": hash_password(password)
    }
    save_users(users)
    return jsonify({"message": "Account created successfully"}), 201

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "All fields are required"}), 400
    
    user = users.get(username)
    if not user or user['password'] != hash_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

  
    token = hashlib.md5(username.encode()).hexdigest()
    sessions[token] = username
    return jsonify({"token": token, "user": {"username": username, "email": user['email']}}), 200

@app.route('/api/profile', methods=['GET'])
def profile():
    token = request.headers.get('x-auth-token')
    username = sessions.get(token)

    if not username:
        return jsonify({"message": "Unauthorized"}), 401

    user = users.get(username)
    return jsonify({"username": username, "email": user['email']}), 200



if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)