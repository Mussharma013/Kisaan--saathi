import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, flash
from flask_session import Session
from datetime import datetime
from gtts import gTTS
import base64
from PIL import Image
import numpy as np
import requests
# For User Authentication
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# --- Configuration ---
app = Flask(__name__)

# --- Secret Key (CRUCIAL for Sessions and Security) ---
# Use a strong, random key. For production, use environment variables.
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_very_secret_and_complex_key_you_should_change")

# --- Session Configuration ---
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" # Or "sqlalchemy", "redis" etc. for production
Session(app)

# --- Database Configuration (SQLite example) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Flask-Login Configuration ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Route name for login page
login_manager.login_message_category = "info" # Flash message category

# --- User Model ---
# ...
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) # Corrected this line
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
# ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Language Data (from previous interactions, with new strings) ---
lang_data = {
    'en': {
        "app_title": "Kisaan Saathi",
        "smart_agri_helper": "Your Smart Agriculture Helper",
        "home": "Home",
        "weather": "Weather",
        "schemes": "Schemes",
        "prediction": "Crop Prediction",
        "login": "Login",
        "signup": "Sign Up",
        "logout": "Logout",
        "your_history": "Your History",
        "contact_support": "Contact: kisaan@support.in",
        "chatbot_title": "Chatbot",
        "type_your_query": "Type your query...",
        "send": "Send",
        "chatbot_welcome": "Hello! I am Kisaan Saathi, your AI assistant. How can I help you with your farming queries today?",
        "trusted_companion": "Your trusted companion for all farming needs.",
        "start_chat": "Start Chat",
        "mic_on": "Microphone On",
        "mic_off": "Microphone Off",
        "audio_error": "Could not generate audio.",
        "image_help": "Image Help",
        "mandi_bhav": "Mandi Bhav",
        "govt_schemes": "Government Schemes",
        "weather_title": "Weather Information",
        "weather_description": "Get real-time weather updates for your farming needs.",
        "weather_city_placeholder": "Enter City Name",
        "weather_get_button": "Get Weather",
        "weather_enter_city": "Please enter a city name.",
        "weather_fetching": "Fetching weather data",
        "weather_in": "Weather in",
        "weather_temp": "Temperature",
        "weather_desc": "Description",
        "weather_humidity": "Humidity",
        "weather_wind": "Wind Speed",
        "weather_error_fetching": "Could not fetch weather data. Please try again.",
        "prediction_title": "Crop Disease Prediction",
        "select_image": "Upload an image of your crop to predict diseases:",
        "upload_button": "Predict Disease",
        "prediction_no_file": "Please select a file first.",
        "prediction_uploading": "Uploading and predicting",
        "prediction_upload_success": "Image uploaded successfully. Getting prediction...",
        "prediction_result": "Prediction Result",
        "prediction_error": "An error occurred during prediction",
        "prediction_no_file_uploaded": "No file part in the request",
        "prediction_no_selected_file": "No selected file",
        "prediction_unknown_error": "An unknown error occurred during upload.",
        "prediction_error_network": "Network error or server issue during upload.",
        "login_title": "Login",
        "login_username_email": "Username or Email",
        "login_password": "Password",
        "login_button": "Login",
        "login_no_account": "Don't have an account?",
        "login_signup_link": "Sign Up Here",
        "signup_title": "Sign Up",
        "signup_username": "Username",
        "signup_email": "Email",
        "signup_password": "Password",
        "signup_confirm_password": "Confirm Password",
        "signup_button": "Sign Up",
        "signup_already_account": "Already have an account?",
        "signup_login_link": "Login Here",
        "error_message": "Error",
        "success_message": "Success",
        "invalid_credentials": "Invalid username/email or password.",
        "user_exists_username": "Username already exists. Please choose a different one.",
        "user_exists_email": "Email already exists. Please choose a different one.",
        "passwords_not_match": "Passwords do not match.",
        "registration_success": "Registration successful! Please log in.",
        "login_required_chatbot": "Please log in or sign up to use the chatbot.", # NEW STRING
        "chatbot_error": "Could not get response. Please try again." # NEW STRING for general chat error
    },
    'hi': {
        "app_title": "किसान साथी",
        "smart_agri_helper": "आपका स्मार्ट कृषि सहायक",
        "home": "होम",
        "weather": "मौसम",
        "schemes": "योजनाएं",
        "prediction": "फसल अनुमान",
        "login": "लॉगिन",
        "signup": "साइन अप करें",
        "logout": "लॉगआउट",
        "your_history": "आपका इतिहास",
        "contact_support": "संपर्क: kisaan@support.in",
        "chatbot_title": "चैटबॉट",
        "type_your_query": "अपना प्रश्न टाइप करें...",
        "send": "भेजें",
        "chatbot_welcome": "नमस्ते! मैं किसान साथी, आपका AI सहायक हूँ। आज मैं आपकी खेती संबंधी प्रश्नों में कैसे मदद कर सकता हूँ?",
        "trusted_companion": "आपकी सभी कृषि आवश्यकताओं के लिए आपका विश्वसनीय साथी।",
        "start_chat": "चैट शुरू करें",
        "mic_on": "माइक ऑन",
        "mic_off": "माइक ऑफ",
        "audio_error": "ऑडियो उत्पन्न नहीं किया जा सका।",
        "image_help": "छवि सहायता",
        "mandi_bhav": "मंडी भाव",
        "govt_schemes": "सरकारी योजनाएं",
        "weather_title": "मौसम की जानकारी",
        "weather_description": "अपनी खेती की जरूरतों के लिए वास्तविक समय में मौसम अपडेट प्राप्त करें।",
        "weather_city_placeholder": "शहर का नाम दर्ज करें",
        "weather_get_button": "मौसम प्राप्त करें",
        "weather_enter_city": "कृपया शहर का नाम दर्ज करें।",
        "weather_fetching": "मौसम का डेटा लाया जा रहा है",
        "weather_in": "मौसम में",
        "weather_temp": "तापमान",
        "weather_desc": "विवरण",
        "weather_humidity": "आर्द्रता",
        "weather_wind": "हवा की गति",
        "weather_error_fetching": "मौसम का डेटा नहीं लाया जा सका। कृपया पुनः प्रयास करें।",
        "prediction_title": "फसल रोग भविष्यवाणी",
        "select_image": "रोगों की भविष्यवाणी के लिए अपनी फसल की एक छवि अपलोड करें:",
        "upload_button": "रोग का अनुमान लगाएं",
        "prediction_no_file": "कृपया पहले एक फ़ाइल चुनें।",
        "prediction_uploading": "अपलोड और भविष्यवाणी हो रही है",
        "prediction_upload_success": "छवि सफलतापूर्वक अपलोड हो गई। भविष्यवाणी प्राप्त हो रही है...",
        "prediction_result": "भविष्यवाणी का परिणाम",
        "prediction_error": "भविष्यवाणी के दौरान एक त्रुटि हुई",
        "prediction_no_file_uploaded": "अनुरोध में कोई फ़ाइल भाग नहीं",
        "prediction_no_selected_file": "कोई फ़ाइल नहीं चुनी गई",
        "prediction_unknown_error": "अपलोड के दौरान एक अज्ञात त्रुटि हुई।",
        "prediction_error_network": "अपलोड के दौरान नेटवर्क त्रुटि या सर्वर समस्या।",
        "login_title": "लॉगिन",
        "login_username_email": "उपयोगकर्ता नाम या ईमेल",
        "login_password": "पासवर्ड",
        "login_button": "लॉगिन करें",
        "login_no_account": "खाता नहीं है?",
        "login_signup_link": "यहां साइन अप करें",
        "signup_title": "साइन अप करें",
        "signup_username": "उपयोगकर्ता नाम",
        "signup_email": "ईमेल",
        "signup_password": "पासवर्ड",
        "signup_confirm_password": "पासवर्ड की पुष्टि करें",
        "signup_button": "साइन अप करें",
        "signup_already_account": "पहले से ही खाता है?",
        "signup_login_link": "यहां लॉगिन करें",
        "error_message": "त्रुटि",
        "success_message": "सफलता",
        "invalid_credentials": "अमान्य उपयोगकर्ता नाम/ईमेल या पासवर्ड।",
        "user_exists_username": "उपयोगकर्ता नाम पहले से मौजूद है। कृपया कोई भिन्न चुनें।",
        "user_exists_email": "ईमेल पहले से मौजूद है। कृपया कोई भिन्न चुनें।",
        "passwords_not_match": "पासवर्ड मेल नहीं खाते।",
        "registration_success": "पंजीकरण सफल! कृपया लॉगिन करें।",
        "login_required_chatbot": "चैटबॉट का उपयोग करने के लिए कृपया लॉगिन या साइन अप करें।", # NEW STRING
        "chatbot_error": "प्रतिक्रिया प्राप्त नहीं हो सकी। कृपया पुनः प्रयास करें।" # NEW STRING
    },
    'bhojpuri': {
        "app_title": "किसान साथी",
        "smart_agri_helper": "रउआं के स्मार्ट खेती के मददगार",
        "home": "होम",
        "weather": "मौसम",
        "schemes": "योजना",
        "prediction": "फसल के अनुमान",
        "login": "लॉगिन",
        "signup": "साइन अप करीं",
        "logout": "लॉगआउट",
        "your_history": "रउआं के इतिहास",
        "contact_support": "संपर्क: kisaan@support.in",
        "chatbot_title": "चैटबॉट",
        "type_your_query": "अपना सवाल लिखीं...",
        "send": "भेजीं",
        "chatbot_welcome": "नमस्ते! हम किसान साथी बानी, रउआं के एआई सहायक। आज हम रउआं के खेती से संबंधित सवालन में कइसे मदद कर सकत बानी?",
        "trusted_companion": "आपकी सभी कृषि आवश्यकताओं के लिए आपका विश्वसनीय साथी।",
        "start_chat": "चैट शुरू करीं",
        "mic_on": "माइक चालू",
        "mic_off": "माइक बंद",
        "audio_error": "ऑडियो ना बन पावल।",
        "image_help": "फोटो के मदद",
        "mandi_bhav": "मंडी भाव",
        "govt_schemes": "सरकारी योजना",
        "weather_title": "मौसम के जानकारी",
        "weather_description": "अपना खेती के जरूरत खातिर समय पर मौसम के जानकारी पाईं।",
        "weather_city_placeholder": "शहर के नाम लिखीं",
        "weather_get_button": "मौसम जानीं",
        "weather_enter_city": "कृप्या शहर के नाम लिखीं।",
        "weather_fetching": "मौसम के डेटा आ रहल बा",
        "weather_in": "मौसम में",
        "weather_temp": "तापमान",
        "weather_desc": "विवरण",
        "weather_humidity": "नमी",
        "weather_wind": "हवा के गति",
        "weather_error_fetching": "मौसम के डेटा ना आ पावल। फिर से कोशिश करीं।",
        "prediction_title": "फसल रोग के अनुमान",
        "select_image": "बीमारी के अनुमान खातिर अपना फसल के एगो फोटो अपलोड करीं:",
        "upload_button": "बीमारी के अनुमान करीं",
        "prediction_no_file": "पहिले एगो फाइल चुनीं।",
        "prediction_uploading": "अपलोड अउरी अनुमान हो रहल बा",
        "prediction_upload_success": "फोटो अपलोड हो गइल। अनुमान आ रहल बा...",
        "prediction_result": "अनुमान के नतीजा",
        "prediction_error": "अनुमान के दौरान गलती भइल",
        "prediction_no_file_uploaded": "अनुरोध में फाइल नइखे",
        "prediction_no_selected_file": "कोनो फाइल नइखे चुनल गइल",
        "prediction_unknown_error": "अपलोड के दौरान अजूबा गलती भइल।",
        "prediction_error_network": "अपलोड के दौरान नेटवर्क के गलती भा सर्वर के समस्या।",
        "login_title": "लॉगिन",
        "login_username_email": "उपयोगकर्ता नाम भा ईमेल",
        "login_password": "पासवर्ड",
        "login_button": "लॉगिन करीं",
        "login_no_account": "खाता नइखे?",
        "login_signup_link": "इहां साइन अप करीं",
        "signup_title": "साइन अप करीं",
        "signup_username": "उपयोगकर्ता नाम",
        "signup_email": "ईमेल",
        "signup_password": "पासवर्ड",
        "signup_confirm_password": "पासवर्ड के पुष्टि करीं",
        "signup_button": "साइन अप करीं",
        "signup_already_account": "पहिले से खाता बा?",
        "signup_login_link": "इहां लॉगिन करीं",
        "error_message": "गलती",
        "success_message": "सफलता",
        "invalid_credentials": "अमान्य उपयोगकर्ता नाम/ईमेल भा पासवर्ड।",
        "user_exists_username": "उपयोगकर्ता नाम पहिले से मौजूद बा। कृपया दोसर चुनीं।",
        "user_exists_email": "ईमेल पहिले से मौजूद बा। कृपया दोसर चुनीं।",
        "passwords_not_match": "पासवर्ड मेल नइखे खात।",
        "registration_success": "पंजीकरण सफल भइल! कृपया लॉगिन करीं।",
        "login_required_chatbot": "चैटबॉट के उपयोग खातिर कृपया लॉगिन करीं भा साइन अप करीं।", # NEW STRING
        "chatbot_error": "जवाब ना मिल पावल। फेरु से कोशिश करीं।" # NEW STRING
    }
}

# --- Global Context Processor ---
@app.before_request
def set_language_and_text():
    # If a lang parameter is in the URL, set session language
    lang = request.args.get('lang')
    if lang in lang_data:
        session['lang'] = lang
    elif 'lang' not in session:
        # Default language if not set in session
        session['lang'] = 'en'

    # Make current language and text data globally available via 'g' object
    g.current_lang = session.get('lang', 'en')
    g.text = lang_data.get(g.current_lang, lang_data['en']) # Fallback to English

    # Make current_user globally available
    g.current_user = current_user
    g.now_datetime = datetime.now() # Always provide datetime

# --- Create Database Tables (Run once) ---
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/')
@app.route('/home')
def home():
    # Pass all necessary variables to the template
    return render_template('home.html', text=g.text, current_lang=g.current_lang, active_page='home', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/mandi_rates')
def mandi_rates():
    return render_template('mandi_rates.html', text=g.text, current_lang=g.current_lang, active_page='mandi_rates', now_datetime=g.now_datetime, current_user=g.current_user)
@app.route('/weather')
def weather():
    return render_template('weather.html', text=g.text, current_lang=g.current_lang, active_page='weather', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/schemes')
def schemes():
    return render_template('schemes.html', text=g.text, current_lang=g.current_lang, active_page='schemes', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/prediction', methods=['GET'])
def prediction():
    return render_template('prediction.html', text=g.text, current_lang=g.current_lang, active_page='prediction', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and user.check_password(password):
            login_user(user, remember=True) # "Remember me" functionality
            flash(g.text.get('success_message', 'Success') + "! " + g.text.get('login_success', 'Logged in successfully!'), 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash(g.text.get('error_message', 'Error') + "! " + g.text.get('invalid_credentials', 'Invalid username/email or password.'), 'danger')
    return render_template('login.html', text=g.text, current_lang=g.current_lang, active_page='login', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash(g.text.get('error_message', 'Error') + "! " + g.text.get('passwords_not_match', 'Passwords do not match.'), 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash(g.text.get('error_message', 'Error') + "! " + g.text.get('user_exists_username', 'Username already exists.'), 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash(g.text.get('error_message', 'Error') + "! " + g.text.get('user_exists_email', 'Email already exists.'), 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(g.text.get('success_message', 'Success') + "! " + g.text.get('registration_success', 'Registration successful! Please log in.'), 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', text=g.text, current_lang=g.current_lang, active_page='signup', now_datetime=g.now_datetime, current_user=g.current_user)

@app.route('/logout')
@login_required # Requires user to be logged in to access
def logout():
    logout_user()
    flash(g.text.get('success_message', 'Success') + "! " + g.text.get('logged_out_message', 'You have been logged out.'), 'info')
    return redirect(url_for('home'))

# --- AI Chatbot Response (NOW PROTECTED) ---
@app.route('/get_response', methods=['POST'])
@login_required # <--- THIS IS THE KEY ADDITION
def get_response():
    user_message = request.json.get('message')
    response_type = request.json.get('response_type', 'text')

    # Mock AI response based on keywords (replace with your actual LLM integration)
    if "hello" in user_message.lower() or "hi" in user_message.lower():
        bot_response = g.text.get('chatbot_welcome', "Hello! How can I help you today?")
    elif "weather" in user_message.lower():
        bot_response = g.text.get('weather_ask', "I can provide weather updates. What city are you interested in?")
    elif "crop" in user_message.lower():
        bot_response = g.text.get('crop_ask', "I can help with crop information. What specific crop or issue are you curious about?")
    elif "schemes" in user_message.lower() or "yojana" in user_message.lower():
        bot_response = g.text.get('schemes_ask', "I have information on government schemes. What kind of scheme are you looking for?")
    else:
        bot_response = g.text.get('default_bot_response', "I am Kisaan Saathi. How can I assist you with farming-related queries?")

    if response_type == 'audio':
        try:
            tts = gTTS(text=bot_response, lang=g.current_lang)
            audio_filename = f"response_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            audio_filepath = os.path.join(app.static_folder, 'audio', audio_filename)
            os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)
            tts.save(audio_filepath)
            audio_url = url_for('static', filename=f'audio/{audio_filename}')
            return jsonify({'response': bot_response, 'audio_url': audio_url})
        except Exception as e:
            print(f"Error generating audio: {e}")
            return jsonify({'response': bot_response, 'audio_url': None, 'error': g.text.get('audio_error', 'Could not generate audio.')})
    else:
        return jsonify({'response': bot_response})

# --- Weather API (Requires API Key) ---
# Replace 'YOUR_OPENWEATHERMAP_API_KEY' with your actual key
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "your_openweathermap_api_key_here") # Get key from https://openweathermap.org/api

# --- NEW: Weather Route ---
@app.route('/get_weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'success': False, 'error': g.text.get('weather_no_city', 'City name is required.')}), 400

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={'592a88aefc717397705d60f599ad55da'}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", g.text.get('weather_city_not_found', 'City not found or API error.'))
            return jsonify({'success': False, 'error': error_message}), 404

        main = data['main']
        weather_desc = data['weather'][0]['description']
        wind = data['wind']

        weather_info = {
            'success': True,
            'city': data['name'],
            'temperature': main['temp'],
            'description': weather_desc.capitalize(),
            'humidity': main['humidity'],
            'wind_speed': wind['speed']
        }
        return jsonify(weather_info)

    except requests.exceptions.RequestException as e:
        print(f"Weather API request failed: {e}")
        return jsonify({'success': False, 'error': g.text.get('weather_api_error', 'Could not connect to weather service.')}), 500
    except Exception as e:
        print(f"Error processing weather data: {e}")
        return jsonify({'success': False, 'error': g.text.get('weather_general_error', 'An unexpected error occurred.')}), 500


# --- NEW: Mandi Rates Route (Simulated Data) ---
@app.route('/get_mandi_rates', methods=['GET'])
def get_mandi_rates():
    # In a real application, you would connect to a database or a specific Mandi API
    # Mandi rate APIs are often highly localized and may require specific partnerships.
    # For now, we'll simulate data.
    state = request.args.get('state', 'Uttar Pradesh')
    district = request.args.get('district', 'Varanasi')
    crop = request.args.get('crop', 'Wheat') # Default crop for example

    simulated_rates = {
        'Uttar Pradesh': {
            'Varanasi': {
                'Wheat': {'min': 2200, 'max': 2400, 'avg': 2300, 'unit': 'quintal'},
                'Rice': {'min': 2800, 'max': 3200, 'avg': 3000, 'unit': 'quintal'},
                'Potato': {'min': 1500, 'max': 1800, 'avg': 1650, 'unit': 'quintal'}
            },
            'Firozabad': {
                'Wheat': {'min': 2150, 'max': 2350, 'avg': 2250, 'unit': 'quintal'},
                'Mustard': {'min': 5000, 'max': 5500, 'avg': 5250, 'unit': 'quintal'}
            }
        },
        'Bihar': {
            'Patna': {
                'Rice': {'min': 2900, 'max': 3300, 'avg': 3100, 'unit': 'quintal'},
                'Maize': {'min': 1900, 'max': 2100, 'avg': 2000, 'unit': 'quintal'}
            }
        }
    }

    rates = simulated_rates.get(state, {}).get(district, {})
    specific_crop_rate = rates.get(crop)

    if specific_crop_rate:
        return jsonify({
            'success': True,
            'state': state,
            'district': district,
            'crop': crop,
            'rates': specific_crop_rate,
            'message': g.text.get('mandi_rate_found', 'Mandi rates found for {crop} in {district}, {state}.').format(crop=crop, district=district, state=state)
        })
    elif rates:
        # If specific crop not found but district exists, return all for district
        return jsonify({
            'success': True,
            'state': state,
            'district': district,
            'crop': g.text.get('all_crops', 'all crops'),
            'rates': rates, # Return all available crops for the district
            'message': g.text.get('mandi_rate_all_crops', 'Mandi rates for {district}, {state}.').format(district=district, state=state)
        })
    else:
        return jsonify({
            'success': False,
            'error': g.text.get('mandi_rate_not_found', 'No mandi rates found for the specified location or crop.'),
            'state': state, 'district': district, 'crop': crop
        }), 404


# --- NEW: Schemes Route (Simulated Data) ---
@app.route('/get_schemes_data', methods=['GET'])
def get_schemes_data():
    category = request.args.get('category', 'all').lower() # e.g., 'subsidy', 'loan', 'insurance'
    state = request.args.get('state', 'all').lower()

    simulated_schemes = [
        {
            'name_en': 'Pradhan Mantri Fasal Bima Yojana',
            'name_hi': 'प्रधानमंत्री फसल बीमा योजना',
            'name_bhojpuri': 'प्रधानमंत्री फसल बीमा योजना',
            'description_en': 'Provides crop insurance to farmers.',
            'description_hi': 'किसानों को फसल बीमा प्रदान करती है।',
            'description_bhojpuri': 'किसानन के फसल बीमा देला।',
            'category': 'insurance',
            'eligibility_en': 'Farmers growing notified crops in notified areas.',
            'eligibility_hi': 'अधिसूचित क्षेत्रों में अधिसूचित फसलें उगाने वाले किसान।',
            'eligibility_bhojpuri': 'अधिसूचित क्षेत्रन में अधिसूचित फसल उपजावे वाला किसान।',
            'state_applicability': ['all'] # Applies to all states
        },
        {
            'name_en': 'Kisan Credit Card (KCC) Scheme',
            'name_hi': 'किसान क्रेडिट कार्ड योजना',
            'name_bhojpuri': 'किसान क्रेडिट कार्ड योजना',
            'description_en': 'Provides timely and adequate credit support to farmers.',
            'description_hi': 'किसानों को समय पर और पर्याप्त ऋण सहायता प्रदान करती है।',
            'description_bhojpuri': 'किसानन के समय पर आ पूरा ऋण देला।',
            'category': 'loan',
            'eligibility_en': 'Farmers involved in agriculture and allied activities.',
            'eligibility_hi': 'कृषि और संबद्ध गतिविधियों में शामिल किसान।',
            'eligibility_bhojpuri': 'खेती आ संबंधित काम में लागल किसान।',
            'state_applicability': ['all']
        },
        {
            'name_en': 'PM-KISAN Samman Nidhi Yojana',
            'name_hi': 'पीएम-किसान सम्मान निधि योजना',
            'name_bhojpuri': 'पीएम-किसान सम्मान निधि योजना',
            'description_en': 'Income support scheme for farmers.',
            'description_hi': 'किसानों के लिए आय सहायता योजना।',
            'description_bhojpuri': 'किसानन खातिर आय मदद योजना।',
            'category': 'subsidy',
            'eligibility_en': 'All landholding farmer families.',
            'eligibility_hi': 'सभी भूमिधारक किसान परिवार।',
            'eligibility_bhojpuri': 'सभ जमीन रखले किसान परिवार।',
            'state_applicability': ['all']
        },
        {
            'name_en': 'Uttar Pradesh Krishak Samridhi Aayog',
            'name_hi': 'उत्तर प्रदेश कृषक समृद्धि आयोग',
            'name_bhojpuri': 'उत्तर प्रदेश कृषक समृद्धि आयोग',
            'description_en': 'Aimed at doubling farmers\' income in Uttar Pradesh.',
            'description_hi': 'उत्तर प्रदेश में किसानों की आय दोगुनी करने का लक्ष्य।',
            'description_bhojpuri': 'उत्तर प्रदेश में किसानन के आमदनी दुगुना करे के लक्ष्य।',
            'category': 'development',
            'eligibility_en': 'Farmers in Uttar Pradesh.',
            'eligibility_hi': 'उत्तर प्रदेश के किसान।',
            'eligibility_bhojpuri': 'उत्तर प्रदेश के किसान।',
            'state_applicability': ['uttar pradesh', 'all'] # Specific to UP, but include 'all' for broad searches
        }
    ]

    filtered_schemes = []
    current_lang = g.current_lang

    for scheme in simulated_schemes:
        match_category = (category == 'all' or scheme['category'] == category)
        match_state = (state == 'all' or state in scheme['state_applicability'])

        if match_category and match_state:
            # Prepare scheme data for the current language
            scheme_data = {
                'name': scheme.get(f'name_{current_lang}', scheme['name_en']), # Fallback to English
                'description': scheme.get(f'description_{current_lang}', scheme['description_en']),
                'category': scheme['category'],
                'eligibility': scheme.get(f'eligibility_{current_lang}', scheme['eligibility_en']),
                'state_applicability': scheme['state_applicability']
            }
            filtered_schemes.append(scheme_data)

    if filtered_schemes:
        return jsonify({
            'success': True,
            'schemes': filtered_schemes,
            'message': g.text.get('schemes_found', 'Found {count} schemes.').format(count=len(filtered_schemes))
        })
    else:
        return jsonify({
            'success': False,
            'error': g.text.get('schemes_not_found', 'No schemes found for the specified criteria.'),
            'category': category, 'state': state
        }), 404


# --- UPDATE: Add new language strings to lang_data in app.py ---
# (Make sure to integrate these into your existing lang_data dictionary)

# Example additions:
# Inside 'en':
# "weather_no_city": "City name is required.",
# "weather_city_not_found": "City not found or API error.",
# "weather_api_error": "Could not connect to weather service.",
# "weather_general_error": "An unexpected error occurred.",
# "mandi_rate_found": "Mandi rates found for {crop} in {district}, {state}.",
# "mandi_rate_all_crops": "Mandi rates for {district}, {state}.",
# "mandi_rate_not_found": "No mandi rates found for the specified location or crop.",
# "all_crops": "all crops",
# "schemes_found": "Found {count} schemes.",
# "schemes_not_found": "No schemes found for the specified criteria.",
# "select_state": "Select State",
# "select_district": "Select District",
# "select_crop": "Select Crop",
# "get_rates": "Get Rates",
# "select_category": "Select Category",
# "get_schemes": "Get Schemes",
# "all_categories": "All Categories",
# "all_states": "All States",


# Inside 'hi':
# "weather_no_city": "शहर का नाम आवश्यक है।",
# "weather_city_not_found": "शहर नहीं मिला या एपीआई त्रुटि।",
# "weather_api_error": "मौसम सेवा से कनेक्ट नहीं हो सका।",
# "weather_general_error": "एक अनपेक्षित त्रुटि हुई।",
# "mandi_rate_found": "{state} के {district} में {crop} के लिए मंडी दरें मिलीं।",
# "mandi_rate_all_crops": "{state} के {district} के लिए मंडी दरें।",
# "mandi_rate_not_found": "निर्दिष्ट स्थान या फसल के लिए कोई मंडी दर नहीं मिली।",
# "all_crops": "सभी फसलें",
# "schemes_found": "{count} योजनाएँ मिलीं।",
# "schemes_not_found": "निर्दिष्ट मानदंडों के लिए कोई योजना नहीं मिली।",
# "select_state": "राज्य चुनें",
# "select_district": "जिला चुनें",
# "select_crop": "फसल चुनें",
# "get_rates": "दरें प्राप्त करें",
# "select_category": "श्रेणी चुनें",
# "get_schemes": "योजनाएं प्राप्त करें",
# "all_categories": "सभी श्रेणियां",
# "all_states": "सभी राज्य",

# Inside 'bhojpuri':
# "weather_no_city": "शहर के नाम जरूरी बा।",
# "weather_city_not_found": "शहर ना मिलल भा एपीआई में गलती बा।",
# "weather_api_error": "मौसम सेवा से जुड़ ना पावल।",
# "weather_general_error": "अचानक कुछ गलती हो गइल।",
# "mandi_rate_found": "{state} के {district} में {crop} खातिर मंडी के रेट मिलल।",
# "mandi_rate_all_crops": "{state} के {district} खातिर मंडी के रेट।",
# "mandi_rate_not_found": "बतावल जगह भा फसल खातिर कवनो मंडी के रेट ना मिलल।",
# "all_crops": "सभ फसल",
# "schemes_found": "{count} गो योजना मिलल।",
# "schemes_not_found": "बतावल मानदंड खातिर कवनो योजना ना मिलल।",
# "select_state": "राज्य चुनीं",
# "select_district": "जिला चुनीं",
# "select_crop": "फसल चुनीं",
# "get_rates": "रेट पावीं",
# "select_category": "श्रेणी चुनीं",
# "get_schemes": "योजना पावीं",
# "all_categories": "सभ श्रेणी",
# "all_states": "सभ राज्य",

def get_crop_prediction(image_path):
    """
    This is a placeholder function for your actual machine learning prediction.
    Replace this with your model loading, image preprocessing, and inference logic.
    """
    if not os.path.exists(image_path):
        return "Error: Image file not found for prediction."

    try:
        img = Image.open(image_path).convert('RGB')
        # Preprocessing steps would go here, e.g., resizing, normalization
        # Example: img = img.resize((224, 224)) # Resize to model's input size
        # Example: img_array = np.asarray(img) / 255.0 # Normalize pixel values
        # Example: img_array = np.expand_dims(img_array, axis=0) # Add batch dimension

        # Mock predictions for demonstration
        mock_results = {
            "apple": "Apple Scab",
            "corn": "Corn Common Rust",
            "potato": "Potato Early Blight",
            "tomato": "Tomato Bacterial Spot",
            "grape": "Grape Black Rot",
            "healthy": "Healthy Crop"
        }
        # A very basic mock based on file name or random choice
        filename_lower = os.path.basename(image_path).lower()
        if "apple" in filename_lower:
            prediction = "Apple Scab (Mock)"
        elif "corn" in filename_lower:
            prediction = "Corn Common Rust (Mock)"
        elif "potato" in filename_lower:
            prediction = "Potato Early Blight (Mock)"
        elif "tomato" in filename_lower:
            prediction = "Tomato Bacterial Spot (Mock)"
        elif "grape" in filename_lower:
            prediction = "Grape Black Rot (Mock)"
        elif "healthy" in filename_lower: # Based on your screenshot, it predicted 'Healthy Crop'
             prediction = "Healthy Crop (Mock)"
        else:
            prediction = np.random.choice(list(mock_results.values())) + " (Mock)"

        # If you had a real model:
        # if model:
        #     predictions_array = model.predict(img_array)
        #     predicted_class_index = np.argmax(predictions_array)
        #     # Map index to actual crop/disease name (you'd have a list of class names)
        #     class_names = ["Class1", "Class2", "Healthy", ...]
        #     prediction = class_names[predicted_class_index]
        # else:
        #     prediction = "No model loaded. Using mock prediction."

        return f"{prediction}" # Return just the prediction string

    except Exception as e:
        return f"Error during image processing or mock prediction: {e}"

@app.route('/upload_crop_image', methods=['POST'])
def upload_crop_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': g.text.prediction_no_file_uploaded})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': g.text.prediction_no_selected_file})
    if file:
        try:
            # Create a 'temp_uploads' directory if it doesn't exist
            temp_dir = os.path.join(app.root_path, 'temp_uploads')
            os.makedirs(temp_dir, exist_ok=True)

            filename = f"uploaded_crop_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)

            # Get prediction using your model (or mock function)
            prediction_result = get_crop_prediction(filepath)

            # Convert image to base64 for display (optional, can also serve static)
            with open(filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{encoded_string}" # Assuming JPEG

            # Clean up the temporary file (optional, but good practice)
            # os.remove(filepath) # Uncomment this if you don't need to keep uploaded files

            return jsonify({
                'success': True,
                'message': g.text.prediction_upload_success,
                'prediction': prediction_result,
                'image_url': image_url
            })
        except Exception as e:
            print(f"Error during image upload/prediction: {e}")
            return jsonify({'success': False, 'error': f"{g.text.prediction_error}: {str(e)}"})
    return jsonify({'success': False, 'error': g.text.prediction_unknown_error})

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    # Pass all necessary variables to the 404 template as well
    return render_template('404.html', text=g.text, current_lang=g.current_lang, active_page='404', now_datetime=g.now_datetime, current_user=g.current_user), 404

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in production