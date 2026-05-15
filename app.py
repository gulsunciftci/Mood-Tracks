# =========================================================
# 🎵 MoodTracks — FINAL VERSION
# =========================================================

import streamlit as st
import pandas as pd
import joblib
import pyrebase
import firebase_admin
import unicodedata

from firebase_admin import credentials
from firebase_admin import firestore
from sklearn.ensemble import RandomForestClassifier

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MoodTracks",
    page_icon="🎵",
    layout="wide"
)

# =========================================================
# FIREBASE CONFIG
# =========================================================

firebase_config = dict(
    st.secrets["firebase"]
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.stButton>button {
    border-radius: 12px;
    height: 3em;
    font-size: 15px;
    font-weight: 600;
}

.song-card {
    padding: 20px;
    border-radius: 14px;
    background-color: #1E1E1E;
    margin-bottom: 18px;
    border: 1px solid #333;
}

.song-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}

.song-info {
    color: #CCCCCC;
    font-size: 15px;
    line-height: 1.7;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):

    text = str(text).lower()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    replacements = {
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ş": "s",
        "ö": "o",
        "ç": "c"
    }

    for tr, en in replacements.items():

        text = text.replace(tr, en)

    return text

# =========================================================
# FIREBASE
# =========================================================

firebase = pyrebase.initialize_app(
    firebase_config
)

auth = firebase.auth()

# =========================================================
# FIRESTORE
# =========================================================

if not firebase_admin._apps:

    cred = credentials.Certificate(
        dict(
            st.secrets["firebase_service_account"]
        )
    )

    firebase_admin.initialize_app(
        cred
    )

db = firestore.client()

# =========================================================
# SESSION
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = "user"

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    main_df = pd.read_csv(
        "data_cleaned.csv"
    )

    try:

        admin_df = pd.read_csv(
            "admin_songs.csv"
        )

    except:

        admin_df = pd.DataFrame()

    df = pd.concat(
        [main_df, admin_df],
        ignore_index=True
    )

    df = df.drop_duplicates(
        subset=["track_name", "artists"]
    )

    return df

df = load_data()

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(
    "moodtracks_model.pkl"
)

# =========================================================
# HEADER
# =========================================================

st.title("🎵 MoodTracks")

st.subheader(
    "AI-powered music recommendations based on your mood"
)

# =========================================================
# AUTH MENU
# =========================================================

menu = ["Login", "Register"]

choice = st.sidebar.selectbox(
    "Account",
    menu
)

# =========================================================
# LOGIN
# =========================================================

if choice == "Login":

    st.sidebar.subheader(
        "🔑 Login"
    )

    email = st.sidebar.text_input(
        "Email"
    )

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button(
        "Login"
    ):

        try:

            user = auth.sign_in_with_email_and_password(
                email,
                password
            )

            st.session_state.user = user

            uid = user["localId"]

            role = "user"

            user_doc = db.collection(
                "users"
            ).document(uid).get()

            if user_doc.exists:

                user_data = user_doc.to_dict()

                role = user_data.get(
                    "role",
                    "user"
                )

            st.session_state.role = role

            st.sidebar.success(
                "Login successful"
            )

            st.rerun()

        except Exception as e:

            st.sidebar.error(
                f"Login failed: {e}"
            )

# =========================================================
# REGISTER
# =========================================================

if choice == "Register":

    st.sidebar.subheader(
        "📝 Register"
    )

    new_email = st.sidebar.text_input(
        "Email"
    )

    new_password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button(
        "Create Account"
    ):

        try:

            user = auth.create_user_with_email_and_password(
                new_email,
                new_password
            )

            auth.send_email_verification(
                user["idToken"]
            )

            uid = user["localId"]

            role = "user"

            if new_email == "gulsunnciftci@gmail.com":

                role = "admin"

            db.collection(
                "users"
            ).document(uid).set({

                "email": new_email,
                "role": role

            })

            st.sidebar.success(
                "Verification email sent!"
            )

        except Exception as e:

            st.sidebar.error(
                f"Registration failed: {e}"
            )

# =========================================================
# LOGIN REQUIRED
# =========================================================

if not st.session_state.user:

    st.warning(
        "Please login to continue"
    )

    st.stop()

# =========================================================
# USER INFO
# =========================================================

st.sidebar.success(
    f'Logged in as:\n{st.session_state.user["email"]}'
)

if st.session_state.role == "admin":

    st.sidebar.success(
        "👑 Admin"
    )

# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button(
    "Logout"
):

    st.session_state.user = None
    st.session_state.role = "user"

    st.rerun()

# =========================================================
# ADMIN PANEL
# =========================================================

if st.session_state.role == "admin":

    with st.expander(
        "👑 Admin Panel"
    ):

        st.subheader(
            "➕ Add New Song"
        )

        new_track = st.text_input(
            "Song Name"
        )

        new_artist = st.text_input(
            "Artist"
        )

        new_genre = st.text_input(
            "Genre"
        )

        new_mood = st.selectbox(
            "Mood",
            [
                "happy",
                "sad",
                "angry",
                "calm"
            ]
        )

        new_popularity = st.slider(
            "Popularity",
            0,
            100,
            50
        )

        new_energy = st.slider(
            "Energy",
            0.0,
            1.0,
            0.5
        )

        new_valence = st.slider(
            "Valence",
            0.0,
            1.0,
            0.5
        )

        if st.button(
            "➕ Add Song"
        ):

            if (
                not new_track
                or
                not new_artist
                or
                not new_genre
            ):

                st.error(
                    "Please fill all fields."
                )

                st.stop()

            normalized_track = normalize_text(
                new_track
            )

            normalized_artist = normalize_text(
                new_artist
            )

            song_exists = df[
                df["track_name"]
                .fillna("")
                .apply(normalize_text)
                ==
                normalized_track
            ]

            song_exists = song_exists[
                song_exists["artists"]
                .fillna("")
                .apply(normalize_text)
                ==
                normalized_artist
            ]

            if not song_exists.empty:

                st.error(
                    "This song already exists!"
                )

                st.stop()

            new_row = {

                "track_name": new_track,
                "artists": new_artist,
                "track_genre": new_genre,
                "mood": new_mood,
                "popularity": new_popularity,
                "energy": new_energy,
                "valence": new_valence

            }

            new_df = pd.DataFrame(
                [new_row]
            )

            try:

                admin_df = pd.read_csv(
                    "admin_songs.csv"
                )

            except:

                admin_df = pd.DataFrame()

            admin_df = pd.concat(
                [admin_df, new_df],
                ignore_index=True
            )

            admin_df.to_csv(
                "admin_songs.csv",
                index=False
            )

            full_df = pd.concat(
                [df, new_df],
                ignore_index=True
            )

            X = full_df[
                [
                    "valence",
                    "energy",
                    "popularity"
                ]
            ]

            y = full_df["mood"]

            new_model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )

            new_model.fit(X, y)

            joblib.dump(
                new_model,
                "moodtracks_model.pkl"
            )

            st.success(
                "Song added & model retrained!"
            )

            st.cache_data.clear()

            st.rerun()

# =========================================================
# FILTERS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    mood = st.selectbox(
        "🎭 Mood",
        [
            "happy",
            "sad",
            "angry",
            "calm"
        ],
        format_func=lambda x: {
            "happy": "😊 Happy",
            "sad": "😢 Sad",
            "angry": "😡 Angry",
            "calm": "😌 Calm"
        }[x]
    )

with col2:

    genres = ["All"] + sorted(
        df["track_genre"]
        .dropna()
        .unique()
        .tolist()
    )

    genre = st.selectbox(
        "🎸 Genre",
        genres
    )

with col3:

    n = st.slider(
        "🎯 Recommendations",
        5,
        20,
        10
    )

# =========================================================
# SEARCH
# =========================================================

search = st.text_input(
    "🔍 Search song or artist"
)

# =========================================================
# GET RECOMMENDATIONS
# =========================================================

if st.button(
    "🎵 Get Recommendations",
    use_container_width=True
):

    filtered = df[
        df["mood"] == mood
    ]

    if genre != "All":

        filtered = filtered[
            filtered["track_genre"] == genre
        ]

    if search:

        normalized_search = normalize_text(
            search
        )

        filtered = filtered[

            filtered["track_name"]
            .fillna("")
            .apply(
                lambda x:
                normalized_search
                in
                normalize_text(x)
            )

            |

            filtered["artists"]
            .fillna("")
            .apply(
                lambda x:
                normalized_search
                in
                normalize_text(x)
            )
        ]

    if filtered.empty:

        st.warning(
            "No songs found."
        )

    else:

        recommended = filtered.sort_values(
            "popularity",
            ascending=False
        ).head(n)

        st.success(
            f'{len(recommended)} songs found'
        )

        for i, (_, row) in enumerate(
            recommended.iterrows(),
            1
        ):

            st.markdown(
                f"""
                <div class="song-card">
                <div class="song-title">
                {i}. {row["track_name"]}
                </div>
                <div class="song-info">
                🎤 Artist: {row["artists"]}
                <br>
                🎸 Genre: {row["track_genre"]}
                <br>
                ⭐ Popularity: {row["popularity"]:.0f}
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            query = (
                f'{row["track_name"]} '
                f'{row["artists"]}'
            )

            youtube_url = (
                "https://www.youtube.com/results?"
                "search_query="
                +
                query.replace(" ", "+")
            )

            st.link_button(
                "▶ YouTube",
                youtube_url,
                use_container_width=True
            )

        st.markdown(
            "## 📊 Recommendation Statistics"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Avg Popularity",
            f'{recommended["popularity"].mean():.0f}'
        )

        c2.metric(
            "Avg Energy",
            f'{recommended["energy"].mean():.2f}'
        )

        c3.metric(
            "Avg Positivity",
            f'{recommended["valence"].mean():.2f}'
        )

# =========================================================
# FOOTER
# =========================================================

st.caption(
    "🎵 MoodTracks — AI Music Recommendation System"
)