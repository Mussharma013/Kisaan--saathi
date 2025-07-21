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
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

from flask_sqlalchemy import SQLAlchemy # Assuming you're using Flask-SQLAlchemy

# ... (your app and db setup) ...

@login_manager.user_loader
def load_user(user_id):
    # The recommended way is to use db.session.get()
    # Ensure 'db' is your Flask-SQLAlchemy instance (e.g., db = SQLAlchemy(app))
    return db.session.get(User, int(user_id))
# Example in app.py or a separate translations.py
TRANSLATIONS = {
    'en': {
        'Uttar Pradesh': 'Uttar Pradesh',
        'Bihar': 'Bihar',
        'Varanasi': 'Varanasi',
        'Wheat': 'Wheat',
        'Min. Price': 'Min. Price',
        'Government Schemes Found': 'Government Schemes Found',
        # ... all your messages and data ...
    },
    'hi': {
        'Uttar Pradesh': 'उत्तर प्रदेश',
        'Bihar': 'बिहार',
        'Varanasi': 'वाराणसी',
        'Wheat': 'गेहूं',
        'Min. Price': 'न्यूनतम मूल्य',
        'Government Schemes Found': 'सरकारी योजनाएं मिलीं',
        # ... all Hindi translations ...
    },
    'bho': {
        'Uttar Pradesh': 'उत्तर प्रदेश',
        'Bihar': 'बिहार',
        'Varanasi': 'वाराणसी',
        'Wheat': 'गेहूँ',
        'Min. Price': 'न्यूनतम दाम',
        'Government Schemes Found': 'सरकारी योजना मिलल',
        # ... all Bhojpuri translations ...
    }
}

def _(key, lang='en'):
    """Simple translation lookup function."""
    return TRANSLATIONS.get(lang, {}).get(key, key) # Fallback to English, then key itself
# --- Language Data (Updated with 'bho' key and new strings) ---
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
        "login_required_chatbot": "Please log in or sign up to use the chatbot.",
        "chatbot_error": "Could not get response. Please try again.",
        "login_success": "Logged in successfully!",
        "logged_out_message": "You have been logged out.",
        "weather_no_city": "City name is required.",
        "weather_city_not_found": "City not found or API error.",
        "weather_api_error": "Could not connect to weather service.",
        "weather_general_error": "An unexpected error occurred.",
        "fetching_weather": "Fetching weather for {city}...",
        "weather_in": "Weather in",
        "temperature": "Temperature",
        "description": "Description",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "select_state_district_prompt": "Please select both State and District.",
        "fetching_mandi_rates": "Fetching mandi rates...",
        "mandi_rates_for": "Mandi Rates for",
        "min_price": "Min. Price",
        "max_price": "Max. Price",
        "avg_price": "Avg. Price",
        "no_specific_rates": "No specific rates found for this crop, displaying available rates for the district.",
        "mandi_general_error": "An error occurred fetching mandi rates.",
        "fetching_schemes": "Fetching schemes...",
        "schemes_found_title": "Found Schemes",
        "category": "Category",
        "eligibility": "Eligibility",
        "schemes_general_error": "An error occurred fetching schemes.",
        "weather_ask": "I can provide weather updates. What city are you interested in?", # Added for chatbot
        "crop_ask": "I can help with crop information. What specific crop or issue are you curious about?", # Added for chatbot
        "schemes_ask": "I have information on government schemes. What kind of scheme are you looking for?", # Added for chatbot
        "default_bot_response": "I am Kisaan Saathi. How can I assist you with farming-related queries?", # Added for chatbot
        "state_name_up": "Uttar Pradesh", # for data localization
        "state_name_br": "Bihar",
        "dist_name_vns": "Varanasi",
        "dist_name_pna": "Patna",
        "dist_name_fzd": "Firozabad",
        "crop_name_wheat": "Wheat",
        "crop_name_rice": "Rice",
        "crop_name_potato": "Potato",
        "crop_name_mustard": "Mustard",
        "crop_name_maize": "Maize",
        "scheme_cat_insurance": "Insurance",
        "scheme_cat_credit": "Credit",
        "scheme_cat_organic_farming": "Organic Farming",
        "scheme_cat_soil_health": "Soil Health",
        "scheme_cat_irrigation": "Irrigation",
        "unit_quintal": "quintal" # For mandi rates unit
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
        "login_required_chatbot": "चैटबॉट का उपयोग करने के लिए कृपया लॉगिन या साइन अप करें।",
        "chatbot_error": "प्रतिक्रिया प्राप्त नहीं हो सकी। कृपया पुनः प्रयास करें।",
        "login_success": "सफलतापूर्वक लॉग इन किया गया!",
        "logged_out_message": "आप लॉग आउट हो गए हैं।",
        "weather_no_city": "शहर का नाम आवश्यक है।",
        "weather_city_not_found": "शहर नहीं मिला या API त्रुटि।",
        "weather_api_error": "मौसम सेवा से कनेक्ट नहीं हो सका।",
        "weather_general_error": "एक अप्रत्याशित त्रुटि हुई।",
        "fetching_weather": "शहर {city} के लिए मौसम लाया जा रहा है...",
        "weather_in": "में मौसम",
        "temperature": "तापमान",
        "description": "विवरण",
        "humidity": "आर्द्रता",
        "wind_speed": "हवा की गति",
        "select_state_district_prompt": "कृपया राज्य और जिला दोनों का चयन करें।",
        "fetching_mandi_rates": "मंडी दरें लाई जा रही हैं...",
        "mandi_rates_for": "के लिए मंडी दरें",
        "min_price": "न्यूनतम मूल्य",
        "max_price": "अधिकतम मूल्य",
        "avg_price": "औसत मूल्य",
        "no_specific_rates": "इस फसल के लिए कोई विशिष्ट दरें नहीं मिलीं, जिले के लिए उपलब्ध दरें प्रदर्शित की जा रही हैं।",
        "mandi_general_error": "मंडी दरें लाने में एक त्रुटि हुई।",
        "fetching_schemes": "योजनाएं लाई जा रही हैं...",
        "schemes_found_title": "मिली योजनाएं",
        "category": "श्रेणी",
        "eligibility": "पात्रता",
        "schemes_general_error": "योजनाएं लाने में एक त्रुटि हुई।",
        "weather_ask": "मैं मौसम के अपडेट प्रदान कर सकता हूँ। आप किस शहर में रुचि रखते हैं?",
        "crop_ask": "मैं फसल की जानकारी में मदद कर सकता हूँ। आप किस विशिष्ट फसल या मुद्दे के बारे में उत्सुक हैं?",
        "schemes_ask": "मेरे पास सरकारी योजनाओं की जानकारी है। आप किस तरह की योजना की तलाश कर रहे हैं?",
        "default_bot_response": "मैं किसान साथी हूँ। मैं खेती संबंधी प्रश्नों में आपकी कैसे सहायता कर सकता हूँ?",
        "state_name_up": "उत्तर प्रदेश",
        "state_name_br": "बिहार",
        "dist_name_vns": "वाराणसी",
        "dist_name_pna": "पटना",
        "dist_name_fzd": "फ़िरोज़ाबाद",
        "crop_name_wheat": "गेहूं",
        "crop_name_rice": "चावल",
        "crop_name_potato": "आलू",
        "crop_name_mustard": "सरसों",
        "crop_name_maize": "मक्का",
        "scheme_cat_insurance": "बीमा",
        "scheme_cat_credit": "ऋण",
        "scheme_cat_organic_farming": "जैविक खेती",
        "scheme_cat_soil_health": "मिट्टी का स्वास्थ्य",
        "scheme_cat_irrigation": "सिंचाई",
        "unit_quintal": "क्विंटल"
    },
    'bho': { # Changed key from 'bhojpuri' to 'bho' for consistency
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
        "login_required_chatbot": "चैटबॉट के उपयोग खातिर कृपया लॉगिन करीं भा साइन अप करीं।",
        "chatbot_error": "जवाब ना मिल पावल। फेरु से कोशिश करीं।",
        "login_success": "सफलतापूर्वक लॉगिन भइल!",
        "logged_out_message": "रउआं लॉगआउट हो गइल बानी।",
        "weather_no_city": "शहर के नाम चाहीं।",
        "weather_city_not_found": "शहर ना मिलल भा एपीआई के गलती।",
        "weather_api_error": "मौसम सेवा से जुड़ ना पावल।",
        "weather_general_error": "एक अजूबा गलती भइल।",
        "fetching_weather": "शहर {city} खातिर मौसम ले आवल जात बा...",
        "weather_in": "में मौसम",
        "temperature": "तापमान",
        "description": "विवरण",
        "humidity": "नमी",
        "wind_speed": "हवा के गति",
        "select_state_district_prompt": "कृपया राज्य आ जिला दुनो चुनीं।",
        "fetching_mandi_rates": "मंडी दरें ले आवल जात बा...",
        "mandi_rates_for": "खातिर मंडी दरें",
        "min_price": "न्यूनतम दाम",
        "max_price": "अधिकतम दाम",
        "avg_price": "औसत दाम",
        "no_specific_rates": "ई फसल खातिर कोनो खास दर ना मिलल, जिला खातिर उपलब्ध दरें देखावल जात बा।",
        "mandi_general_error": "मंडी दरें ले आवत घरी एगो गलती भइल।",
        "fetching_schemes": "योजनाएं ले आवल जात बा...",
        "schemes_found_title": "मिलल योजनाएं",
        "category": "श्रेणी",
        "eligibility": "पात्रता",
        "schemes_general_error": "योजनाएं ले आवत घरी एगो गलती भइल।",
        "weather_ask": "हम मौसम के अपडेट दे सकत बानी। रउआं के कवन शहर में रुचि बा?",
        "crop_ask": "हम फसल के जानकारी में मदद कर सकत बानी। रउआं के कवनो खास फसल भा समस्या के बारे में जानल बा?",
        "schemes_ask": "हमरा लगे सरकारी योजना के जानकारी बा। रउआं कवन तरह के योजना खोजत बानी?",
        "default_bot_response": "हम किसान साथी बानी। हम रउआं के खेती से संबंधित सवालन में कइसे मदद कर सकत बानी?",
        "state_name_up": "उत्तर प्रदेश",
        "state_name_br": "बिहार",
        "dist_name_vns": "वाराणसी",
        "dist_name_pna": "पटना",
        "dist_name_fzd": "फिरोजाबाद",
        "crop_name_wheat": "गेहूँ",
        "crop_name_rice": "चाउर",
        "crop_name_potato": "आलू",
        "crop_name_mustard": "सरसों",
        "crop_name_maize": "मक्का",
        "scheme_cat_insurance": "बीमा",
        "scheme_cat_credit": "ऋण",
        "scheme_cat_organic_farming": "जैविक खेती",
        "scheme_cat_soil_health": "माटी के सेहत",
        "scheme_cat_irrigation": "सिंचाई",
        "unit_quintal": "क्विंटल"
    }
}

# --- Global Context Processor ---
@app.before_request
def set_language_and_text():
    # If a lang parameter is in the URL, set session language
    lang = request.args.get('lang')
    # Use 'bho' as the key for Bhojpuri
    if lang == 'bhojpuri': # If frontend sends 'bhojpuri'
        session['lang'] = 'bho'
    elif lang in lang_data:
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
    # Get the language from the request, fallback to current_lang from g
    lang_code = request.json.get('lang', g.current_lang)

    # Mock AI response based on keywords (replace with your actual LLM integration)
    if "hello" in user_message.lower() or "hi" in user_message.lower():
        bot_response = lang_data.get(lang_code, lang_data['en']).get('chatbot_welcome', "Hello! How can I help you today?")
    elif "weather" in user_message.lower():
        bot_response = lang_data.get(lang_code, lang_data['en']).get('weather_ask', "I can provide weather updates. What city are you interested in?")
    elif "crop" in user_message.lower():
        bot_response = lang_data.get(lang_code, lang_data['en']).get('crop_ask', "I can help with crop information. What specific crop or issue are you curious about?")
    elif "schemes" in user_message.lower() or "yojana" in user_message.lower():
        bot_response = lang_data.get(lang_code, lang_data['en']).get('schemes_ask', "I have information on government schemes. What kind of scheme are you looking for?")
    else:
        bot_response = lang_data.get(lang_code, lang_data['en']).get('default_bot_response', "I am Kisaan Saathi. How can I assist you with farming-related queries?")

    if response_type == 'audio':
        try:
            # Use the determined language for gTTS
            tts = gTTS(text=bot_response, lang=lang_code)
            audio_filename = f"response_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            audio_filepath = os.path.join(app.static_folder, 'audio', audio_filename)
            os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)
            tts.save(audio_filepath)
            audio_url = url_for('static', filename=f'audio/{audio_filename}')
            return jsonify({'response': bot_response, 'audio_url': audio_url})
        except Exception as e:
            print(f"Error generating audio: {e}")
            return jsonify({'response': bot_response, 'audio_url': None, 'error': lang_data.get(lang_code, lang_data['en']).get('audio_error', 'Could not generate audio.')})
    else:
        return jsonify({'response': bot_response})

# --- Weather API (Requires API Key) ---
# Replace 'YOUR_OPENWEATHERMAP_API_KEY' with your actual key
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "592a88aefc717397705d60f599ad55da") # Use env var, fallback to default for development

# --- Weather Route ---
@app.route('/get_weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    lang_code = request.args.get('lang', g.current_lang) # Get language for error messages

    if not city:
        return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('weather_no_city', 'City name is required.')}), 400

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", lang_data.get(lang_code, lang_data['en']).get('weather_city_not_found', 'City not found or API error.'))
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
        return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('weather_api_error', 'Could not connect to weather service.')}), 500
    except Exception as e:
        print(f"Error processing weather data: {e}")
        return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('weather_general_error', 'An unexpected error occurred.')}), 500


# --- Mandi Rates Route (Simulated Data) ---
@app.route('/get_mandi_rates', methods=['GET'])
def get_mandi_rates():
    state = request.args.get('state', 'Uttar Pradesh')
    district = request.args.get('district', 'Varanasi')
    crop = request.args.get('crop', 'Wheat')
    lang_code = request.args.get('lang', g.current_lang)

    simulated_rates_raw = { # Store raw data, then localize on retrieval
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
                'Maize': {'min': 1800, 'max': 2000, 'avg': 1900, 'unit': 'quintal'}
            }
        }
    }

    # Helper to localize string from raw data
    def _(key, lang=lang_code):
        # This will attempt to find a direct match in lang_data (e.g., 'Wheat' -> 'गेहूं')
        # If not found, it returns the original key.
        return lang_data.get(lang, lang_data['en']).get(key, key)

    district_data_raw = simulated_rates_raw.get(state, {}).get(district, {})
    crop_data_raw = district_data_raw.get(crop)

    if crop_data_raw:
        # Localize the unit
        localized_crop_data = crop_data_raw.copy()
        localized_crop_data['unit'] = _(localized_crop_data['unit'])
        return jsonify({
            'success': True,
            'state': _(state),
            'district': _(district),
            'crop': _(crop),
            'rates': localized_crop_data
        })
    elif district_data_raw:
        # If no specific crop rates found, return all rates for the district
        # Localize all crop names within the district data
        localized_district_rates = {}
        for c, rates in district_data_raw.items():
            localized_rates = rates.copy()
            localized_rates['unit'] = _(localized_rates['unit'])
            localized_district_rates[_(c)] = localized_rates # Localize crop name as key

        return jsonify({
            'success': True,
            'state': _(state),
            'district': _(district),
            'crop': None, # Indicate no specific crop rates
            'message': g.text.get('no_specific_rates', 'No specific rates found for this crop, displaying available rates for the district.'),
            'rates': localized_district_rates
        })
    else:
        return jsonify({
            'success': False,
            'error': g.text.get('mandi_general_error', 'An error occurred fetching mandi rates.'),
            'details': 'State or district data not found.'
        }), 404

# --- Crop Prediction Route (Simulated Data) ---
@app.route('/upload_crop_image', methods=['POST'])
def upload_crop_image():
    lang_code = request.form.get('lang', g.current_lang) # Get language from form data

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('prediction_no_file_uploaded', 'No file part')}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('prediction_no_selected_file', 'No selected file')}), 400
    if file:
        # In a real application, you would save the file, process it with a ML model,
        # and return a real prediction.
        # For simulation, let's just pretend to process it and return a generic localized prediction.

        # Example: Save the file to a static directory to make it accessible
        # This is a basic example; consider security for file uploads in production.
        upload_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"crop_image_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Simulate prediction result and localize it
        simulated_prediction = "This crop appears to be healthy with no major diseases detected."
        if "leaf_spot" in file.filename.lower(): # Just a silly example condition
            simulated_prediction = "Signs of Leaf Spot disease detected. Consider applying a fungicide."

        # You would integrate your actual ML model here to get a real prediction.
        # Once you have the real prediction, you might have pre-defined localized messages for different diseases.
        # For now, we'll just use a placeholder and localize it if possible or use the original.
        localized_prediction_messages = {
            'en': {
                "healthy_crop": "This crop appears to be healthy with no major diseases detected.",
                "leaf_spot": "Signs of Leaf Spot disease detected. Consider applying a fungicide.",
                "rust": "Rust disease identified. Consult an agricultural expert for treatment."
            },
            'hi': {
                "healthy_crop": "यह फसल स्वस्थ दिख रही है, कोई बड़ी बीमारी नहीं पाई गई।",
                "leaf_spot": "पत्ती धब्बे रोग के लक्षण पाए गए। फफूंदनाशक का प्रयोग करने पर विचार करें।",
                "rust": "रस्ट रोग की पहचान हुई। उपचार के लिए कृषि विशेषज्ञ से सलाह लें।"
            },
            'bho': {
                "healthy_crop": "ई फसल ठीक बा, कवनो बड़हन बीमारी नइखे मिलल।",
                "leaf_spot": "पत्ता पर धब्बा रोग के लक्षण मिलल। फंगसनाशक के उपयोग पर विचार करीं।",
                "rust": "रस्ट रोग के पहचान भइल। इलाज खातिर कृषि विशेषज्ञ से सलाह लीं।"
            }
        }

        # Select the appropriate localized message based on the simulated outcome
        final_prediction_message = ""
        if "healthy" in simulated_prediction.lower():
            final_prediction_message = localized_prediction_messages.get(lang_code, localized_prediction_messages['en']).get('healthy_crop')
        elif "leaf spot" in simulated_prediction.lower():
            final_prediction_message = localized_prediction_messages.get(lang_code, localized_prediction_messages['en']).get('leaf_spot')
        else: # Fallback
            final_prediction_message = simulated_prediction # Use the original if no specific localization

        return jsonify({
            'success': True,
            'prediction': final_prediction_message,
            'image_url': url_for('static', filename=f'uploads/{filename}')
        })
    return jsonify({'success': False, 'error': lang_data.get(lang_code, lang_data['en']).get('prediction_unknown_error', 'An unknown error occurred during upload.')}), 500

# --- Schemes Route (Simulated Data) ---
@app.route('/get_schemes', methods=['GET'])
def get_schemes():
    category_filter = request.args.get('category')
    eligibility_filter = request.args.get('eligibility')
    lang_code = request.args.get('lang', g.current_lang)

    simulated_schemes_raw = [ # Store raw data
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Provides crop insurance against non-preventable natural risks.",
            "category": "Insurance",
            "eligibility": "Farmers growing notified crops in notified areas."
        },
        {
            "name": "Kisan Credit Card (KCC)",
            "description": "Provides timely and adequate credit support to farmers for their agricultural operations.",
            "category": "Credit",
            "eligibility": "Farmers, individual/joint cultivators, tenant farmers, share croppers, SHGs/JLGs of farmers."
        },
        {
            "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "description": "Promotes organic farming through cluster approach.",
            "category": "Organic Farming",
            "eligibility": "Farmers willing to undertake organic farming as per NPOP standards."
        },
        {
            "name": "Soil Health Card Scheme",
            "description": "Provides information to farmers on nutrient status of their soil and recommendations on dosage of nutrients.",
            "category": "Soil Health",
            "eligibility": "All farmers."
        },
        {
            "name": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)",
            "description": "Aims to expand cultivable area under assured irrigation, improve water use efficiency.",
            "category": "Irrigation",
            "eligibility": "Farmers requiring irrigation facilities."
        }
    ]

    # Helper to localize scheme specific strings
    def _scheme_prop(key, prop_name, lang=lang_code):
        # This function should map generic property names like "Insurance" to their localized keys
        # For example, "Insurance" -> "scheme_cat_insurance" and then look that up
        mapping = {
            "Insurance": "scheme_cat_insurance",
            "Credit": "scheme_cat_credit",
            "Organic Farming": "scheme_cat_organic_farming",
            "Soil Health": "scheme_cat_soil_health",
            "Irrigation": "scheme_cat_irrigation",
            # Add more as needed for descriptions and eligibilities if they are standardized
        }
        localized_key = mapping.get(key, key) # Get mapped key or use original
        return lang_data.get(lang, lang_data['en']).get(localized_key, key)


    filtered_schemes = []
    for scheme in simulated_schemes_raw:
        match = True
        # Filter based on raw data for consistency in filtering logic
        if category_filter and category_filter.lower() not in scheme['category'].lower():
            match = False
        if eligibility_filter and eligibility_filter.lower() not in scheme['eligibility'].lower():
            match = False

        if match:
            # Localize the scheme properties before adding to filtered_schemes
            localized_scheme = {
                "name": scheme["name"], # Scheme names might not always be localized directly
                "description": _scheme_prop(scheme["description"], "description"), # You might need a more sophisticated lookup here
                "category": _scheme_prop(scheme["category"], "category"),
                "eligibility": _scheme_prop(scheme["eligibility"], "eligibility") # Similar for eligibility
            }
            # For demonstration, I'm using _scheme_prop, but for free-form text like description
            # and eligibility, you might need a more advanced translation method (e.g., an LLM translating it).
            # For now, if the string isn't in lang_data, it returns the original English.
            # You'll likely need to expand `lang_data` with translations for actual descriptions and eligibilities.
            filtered_schemes.append(localized_scheme)

    if filtered_schemes:
        return jsonify({
            'success': True,
            'schemes': filtered_schemes,
            'message': lang_data.get(lang_code, lang_data['en']).get('schemes_found_title', 'Found Schemes')
        })
    else:
        return jsonify({
            'success': False,
            'message': lang_data.get(lang_code, lang_data['en']).get('schemes_general_error', 'An error occurred fetching schemes.'),
            'details': 'No schemes found matching criteria.'
        }), 404


if __name__ == '__main__':
    # Initialize the database if it doesn't exist
    with app.app_context():
        db.create_all()
    # It's good practice to create the static/audio directory if it doesn't exist
    os.makedirs(os.path.join(app.static_folder, 'audio'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    app.run(debug=True)