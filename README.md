# 📜 திருக்குறள் பழகு (Thirukkural Pazhagu)
### *An AI-Powered Interactive Gamified Learning & Speech Evaluation Platform for Thirukkural*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?style=for-the-badge&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-4EA94B?style=for-the-badge&logo=mongodb)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

---

## 🌟 Overview

**திருக்குறள் பழகு (Thirukkural Pazhagu)** is an innovative web-based educational platform designed to make learning classical Tamil literature (**Thirukkural**) engaging, gamified, and accessible. 

By combining **AI Speech Recognition**, **N-gram Statistical Prediction Engine**, and a **Gamified Progression Economy**, users can read, memorize, pronounce, and master all 1,330 Thirukkural couplets through interactive challenges.

---

## 🚀 Key Features

### 1. 🎯 3-Round Interactive Kural Mastery Engine
Every Thirukkural is structured into a progressive 3-round learning journey:
- **Round 1: Choose Missing Word (சொல்லைத் தேர்ந்தெடு)**  
  Test vocabulary by selecting the correct missing word from multiple choices. *(1 Pulli)*
- **Round 2: Arrange Words (சொற்களை வரிசைப்படுத்து)**  
  Drag-and-drop or tap to arrange the 7 Tamil words of the couplet in precise sequential order. *(Up to 7 Pulligal — 1 per correct word)*
- **Round 3: AI Voice Pronunciation Challenge (குரல் உச்சரிப்பு சவால்)**  
  Recite the Kural into your microphone. Integrated AI Speech-to-Text evaluates Tamil pronunciation accuracy word-by-word in real-time. *(Up to 7 Pulligal — 1 per correct spoken word)*

---

### 2. 🤖 AI N-gram Prediction Challenge (குறள் யுத்தம்)
A human-versus-machine word prediction game powered by a custom **Bigram / Trigram Statistical Language Model** built on the complete corpus of Thirukkural. Compete against AI predictions to test your deep knowledge of classical Tamil syntax!

---

### 3. 🏆 Gamification & Reward Economy

The platform features a balanced dual-currency and XP system:

* **⭐ புள்ளிகள் (Pulligal / XP)**: Earned strictly through learning and solving Kurals. Max **15 Pulligal** per solved Kural ($1 + 7 + 7 = 15$).
* **🪙 நாணயங்கள் (Nanayangal / Coins)**: Earned 1:1 with Pulligal in rounds, as well as via Daily Login Bonuses.
* **💎 வைரங்கள் (Vairangal / Diamonds)**: Rare currency awarded for Voice Pronunciation challenges and Kural Master achievements.
* **⚡ நிலைகள் (Level Progression)**: Automatic level progression for every 100 Pulligal earned:
  $$\text{Level} = 1 + \left(\frac{\text{Pulligal (XP)}}{100}\right)$$
* **📅 7-Day Daily Login Streak (தினசரி லாகின் போனஸ்)**: Log in daily to maintain active streaks and claim scaled rewards of Coins 🪙 and Diamonds 💎.
* **🥇 Leaderboards & Badges**: Real-time global ranking system based on XP, completion percentage, and earned badges such as **"Kural Master"**.

---

### 4. 👤 Complete User & Profile Management
- Secure user registration and login powered by **PBKDF2 SHA-256** password hashing.
- Comprehensive User Profile Dashboard tracking completion rate out of 1,330 Kurals, accuracy %, current & longest streaks, and earned badges.
- Self-service **Account Deletion** with complete data cleanup.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.10+, Flask (REST APIs, Session Management, Blueprint Architecture)
- **Database**: MongoDB Atlas (Cloud NoSQL storing `user_details`, `kural_data`, `adhigaram_data`, `ngram_game_scores`)
- **AI & Speech Evaluation**:
  - `SpeechRecognition` library for audio-to-text pronunciation matching.
  - Custom `N-gram` Bigram/Trigram statistical model (`ngram_model.py`).
  - Google Text-to-Speech (`gTTS`) & custom native Tamil pause formatter (`tts.py`).
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism, Micro-animations, Gamified UI), JavaScript (ES6+), jQuery.

---

## 📂 Directory Structure

```dir
thirukural1-main/
├── app.py                   # Main Flask application entry point & dashboard APIs
├── n-gram_model.py          # N-gram statistical language model for AI prediction
├── tts.py                   # Text-to-Speech & Tamil breath-pause formatter
├── requirements.txt         # Python dependency manifest
├── Procfile                 # Deployment configuration (Gunicorn / Heroku)
├── .env                     # Environment variables (MongoDB connection string)
├── adhigaram_data.json      # Structured Adhigaram database export
├── Thirukural.txt           # Raw Thirukkural corpus text
│
├── user/                    # User Module & Core Game Logic
│   ├── models.py            # User schema, normalization & authentication logic
│   ├── routes.py            # Flask API routes for user actions & game rounds
│   ├── kural.py             # Kural game engine evaluation logic
│   └── audioProcessing.py   # Speech recognition & pronunciation analysis engine
│
├── templates/               # Jinja2 HTML Templates
│   ├── index.html           # Main Dashboard & Leaderboard
│   ├── profile.html         # User Profile & Account Settings
│   ├── play_kural.html      # 3-Round Interactive Kural Game UI
│   ├── ngram_game.html      # AI N-gram Challenge UI
│   ├── login.html           # Authentication Login page
│   └── register.html        # New User Registration page
│
└── static/                  # Static Web Assets
    ├── css/                 # Custom CSS stylesheets (dashboard, basicStyle, etc.)
    ├── js/                  # Client-side JavaScript & Audio Recorders
    └── images/              # Media assets, icons, badges & logos
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
Ensure you have the following installed on your system:
- **Python 3.10** or higher
- **pip** (Python package installer)
- **Git**

---

### 2. Clone the Repository
```bash
git clone https://github.com/mohanshanmugavel/Thirukkural.git
cd Thirukkural
```

---

### 3. Create a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 5. Environment Configuration
Create a `.env` file in the root directory and add your MongoDB Atlas URI:

```env
STRING="mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority"
```

---

### 6. Run the Application
Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```url
http://127.0.0.1:5000/
```

---

## 📊 Summary of Kural Rewards

| Game Round | Objective | Max Pulligal (XP ⭐) | Max Nanayangal (Coins 🪙) | Vairangal (Diamonds 💎) |
| :--- | :--- | :---: | :---: | :---: |
| **Round 1** | Choose correct missing word | **1** | **1** | 0 |
| **Round 2** | Arrange 7 words in order | **7** *(1 / word)* | **7** *(1 / word)* | 0 |
| **Round 3** | Recite Kural with speech AI | **7** *(1 / word)* | **7** *(1 / word)* | 1 |
| **Completion** | All 3 Rounds Complete | **Bonus Badge** | **Bonus Badge** | 1 |
| **Total** | **1 Complete Solved Kural** | **15 Pulligal** | **15 Coins** | **2 Diamonds** |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](https://github.com/mohanshanmugavel/Thirukkural/issues).

---

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p center>
  Made with ❤️ for Tamil Literature & Modern AI Education
</p>
