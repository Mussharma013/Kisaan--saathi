# 🌾 Kisaan Saathi – Voice & AI Assistant for Indian Farmers

**Kisaan Saathi** is a multilingual AI-powered assistant web application designed for Indian farmers. It bridges the digital divide by providing localized voice/chat interaction in rural languages like **Hindi**, **Bhojpuri**, **Gujarati**, and others.

The platform offers real-time information on **crop diseases**, **mandi prices**, **government schemes**, and **weather updates** — all in a simple, mobile-first UI with voice support.

---

## 📌 Key Features

### 🧠 AI Voice Assistant
- Natural interaction using speech/text in regional languages
- Powered by **GPT-4 via LangChain**
- Voice-to-text (Whisper/Vosk) and text-to-speech (gTTS/Coqui)

### 🌾 Crop Disease Detection
- Upload crop images and receive disease predictions
- ML model trained on plant disease dataset
- Local language explanation of results

### 🛒 Mandi Rate Finder
- Real-time **market prices (mandi rates)** of crops
- Based on user’s selected location or state
- Uses **AgmarkNet API**

### 🏛️ Government Scheme Info
- Smart assistant to help farmers navigate schemes like **PM-Kisan**, **PMFBY**, etc.
- Answers eligibility and benefit queries via GPT-4 + API/manual database

### 🌤️ Live Weather Forecast
- Daily temperature, rainfall, humidity, wind
- Powered by **OpenWeatherMap** and IMD data
- Delivered in user's language

### 🌐 Language Switcher
- Dynamically switch entire website between **Hindi**, **Bhojpuri**, **Gujarati**, etc.
- All UI elements update instantly
- Auto-detection from voice input (in progress)

---

## 🧠 AI/ML Backend

### 🔍 Image Classification Model for Crop Diseases
- Dataset: PlantVillage or custom-curated
- Model: Trained using CNN (Keras/TensorFlow)
- Output: Disease name + remedy in local language

➡️ Training pipeline is modularized in `utils/train_model.py`  
➡️ Dataset organized in `data/plant_disease/`  
➡️ Trained model saved as `crop_model.pkl`

---

## 🧰 Project Structure


kisaan-saathi/
├── app.py # Flask backend
├── utils/
│ ├── train_model.py # Script to train crop disease model
│ └── translator.py # Util for translating text to local languages
├── templates/
│ ├── base.html
│ ├── home.html
│ ├── login.html
│ ├── signup.html
│ ├── chatbot.html
│ ├── weather.html
│ ├── mandi.html
│ ├── scheme.html
│ └── crop.html
├── static/
│ ├── style.css
│ └── script.js
├── data/
│ └── plant_disease/ # Folder with training images (by class)
├── models/
│ └── crop_model.pkl # Trained model file
├── firebase_config.json # Firebase Auth config
├── requirements.txt
├── .gitignore
└── README.md
