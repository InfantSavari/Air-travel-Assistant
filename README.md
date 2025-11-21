# Air-travel-Assistant
✈️ AI Airport Travel Assistant (Flask + Gemini API)

A Flask-based web application that provides intelligent airport guidance using Google’s Gemini AI. The system offers navigation help, lounge information, security tips, transportation advice, and airport amenities — all in under 150 words per response.

It also includes user authentication (signup, signin, profile) and a local caching system to reduce API usage.

🚀 Features
🔹 AI Airport Assistant

Real-time airport queries answered using Gemini 1.5 Flash

Tips on terminals, gate navigation, security, lounges, transportation, and amenities

Response caching via airport_cache.json

Automatic fallbacks for common airport topics

🔹 User Authentication

Signup & Signin using hashed passwords

Session tokens for authenticated profile access

Persistent storage in user_data.json

🔹 Backend Framework

Built using Flask

CORS enabled

Served using Waitress (optional)

.env support via python-dotenv

📁 Project Structure
/project
 ├── app.py
 ├── airport_cache.json
 ├── user_data.json
 ├── templates/
 │    └── index.html
 ├── .env
 └── README.md

🔧 Installation
1️⃣ Clone the repository
git clone <your-repo-url>
cd <project-folder>

2️⃣ Install dependencies
pip install -r requirements.txt


(Requirements:
Flask, flask-cors, google-generativeai, python-dotenv, waitress)

3️⃣ Add your Gemini API key

Create a .env file:

GEMINI_API_KEY=your_api_key_here

▶️ Running the Application
Development mode
python app.py


Runs on:
http://127.0.0.1:5000

Production mode (Waitress)
waitress-serve --host=0.0.0.0 --port=5000 app:app

🧠 API Routes
GET /

Serves the homepage (index.html)

POST /api

Main AI airport assistant endpoint.

Request:
{
  "query": "How do I reach Terminal 2 from Gate 14 at JFK?"
}

Response:
{
  "reply": "AI-generated airport guidance..."
}

POST /api/signup

User account creation.

{
  "username": "john",
  "email": "john@mail.com",
  "password": "mypassword"
}

POST /api/signin

Login and get a session token.

GET /api/profile

Requires header:

x-auth-token: <token>


Returns user info.

🧩 Caching System

All AI responses are stored in airport_cache.json using MD5 hashing.
This reduces API calls and speeds up repeat queries.

🔐 Security Notes

Passwords are SHA-256 hashed

Tokens are MD5-based (not suitable for production use)

For real deployment, replace with JWT or OAuth

🤝 Contributions

Feel free to submit issues or pull requests.

📜 License

MIT License
