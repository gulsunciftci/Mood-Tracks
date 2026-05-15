# 🎵 MoodTracks

> AI-powered music recommendation system based on your mood

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?logo=scikit-learn)
![Firebase](https://img.shields.io/badge/Firebase-Auth%20%26%20Firestore-yellow?logo=firebase)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 About

MoodTracks is a data science project that recommends music based on the user's current mood. It uses a **Random Forest** machine learning model trained on 114,000+ Spotify tracks to classify songs into four mood categories: Happy, Sad, Angry, and Calm.

---


## 🌐 Live Demo

🔗 [Open MoodTracks](https://mood-tracks.streamlit.app/)

## ✨ Features

- 🎭 **Mood-based recommendations** — Select your mood and get personalized song suggestions
- 🎸 **Genre filter** — Filter recommendations by music genre (114 genres available)
- 🔍 **Search** — Search by song name or artist with Turkish character support
- 🎧 **Direct links** — Open songs instantly on Spotify or YouTube
- 👑 **Admin panel** — Admins can add new songs and retrain the model
- 🔐 **Firebase authentication** — Secure login and registration system
- 📊 **Recommendation stats** — Average popularity, energy, and positivity scores

---

## 🧠 How It Works

Songs are classified into moods using two audio features from Spotify:

| Mood | Valence | Energy |
|------|---------|--------|
| 😊 Happy | ≥ 0.6 | ≥ 0.6 |
| 😌 Calm | ≥ 0.6 | < 0.6 |
| 😡 Angry | < 0.4 | ≥ 0.6 |
| 😢 Sad | < 0.4 | < 0.6 |

A **Random Forest Classifier** (100 estimators) is trained on these features to predict mood and power the recommendation engine.

---

## 🗂️ Dataset

- **Source:** [Spotify Tracks Dataset — Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)
- **Size:** 114,000+ songs
- **Features:** valence, energy, danceability, tempo, acousticness, speechiness, loudness, instrumentalness, popularity
- **Genres:** 114 different genres

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Web application |
| Pandas & NumPy | Data processing |
| Scikit-learn | Machine learning (Random Forest) |
| Matplotlib & Seaborn | Data visualization |
| Firebase (Pyrebase + Admin SDK) | Authentication & database |
| Joblib | Model serialization |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/gulsunciftci/Mood-Tracks.git
cd Mood-Tracks
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up secrets

Create `.streamlit/secrets.toml` file:

```toml
[firebase]
apiKey = "..."
authDomain = "..."
databaseURL = "..."
projectId = "..."
storageBucket = "..."
messagingSenderId = "..."
appId = "..."

[firebase_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

### 4. Add dataset and model

Place these files in the project root:
- `data_cleaned.csv` — cleaned Spotify dataset
- `moodtracks_model.pkl` — trained Random Forest model

### 5. Run the app

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
MoodTracks/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── data_cleaned.csv        # Cleaned dataset (not in repo)
├── moodtracks_model.pkl    # Trained ML model (not in repo)
├── admin_songs.csv         # Admin-added songs (not in repo)
├── .streamlit/
│   └── secrets.toml        # Firebase secrets (not in repo)
└── README.md
```

---

## 📊 Project Phases

- [x] Data collection (Kaggle Spotify dataset)
- [x] Data cleaning & mood labeling
- [x] Exploratory data analysis (EDA)
- [x] Machine learning model (Random Forest)
- [x] Feature importance analysis
- [x] Streamlit web application
- [x] Firebase authentication
- [x] Admin panel
- [x] Cloud deployment

---

## 🙋 Author

**Gulsun Ciftci**
- GitHub: [@gulsunciftci](https://github.com/gulsunciftci)

---

## 📄 License

This project is licensed under the MIT License.