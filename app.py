
# 🎵 MoodTracks — FINAL VERSION

import streamlit as st
import pandas as pd
import joblib
import pyrebase
import firebase_admin
import unicodedata

from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

# PAGE CONFIG


st.set_page_config(
    page_title="MoodTracks",
    page_icon="🎵",
    layout="wide"
)


# FIREBASE CONFIG


firebase_config = dict(
    st.secrets["firebase"]
)


# SESSION


if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = "user"

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "recommended" not in st.session_state:
    st.session_state.recommended = None


# CUSTOM CSS


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


# LIGHT THEME


if st.session_state.theme == "Light":

    st.markdown("""
    <style>

    .stApp {
        background-color: white;
        color: black;
    }

    .song-card {
        background-color: #F3F3F3 !important;
        border: 1px solid #DDD !important;
    }

    .song-info {
        color: black !important;
    }

    </style>
    """, unsafe_allow_html=True)

# TEXT NORMALIZATION


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


# FIREBASE

firebase = pyrebase.initialize_app(
    firebase_config
)

auth = firebase.auth()


# FIRESTORE


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


# LOAD DATA

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


# LOAD MODEL


model = joblib.load(
    "moodtracks_model.pkl"
)


# HEADER

st.title("🎵 MoodTracks")

st.subheader(
    "AI-powered music recommendations based on your mood"
)

# AUTH MENU


menu = ["Login", "Register"]

choice = st.sidebar.selectbox(
    "Account",
    menu
)


# LOGIN


if choice == "Login":

    st.sidebar.subheader("🔑 Login")

    email = st.sidebar.text_input(
        "Email"
    )

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

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

                theme = user_data.get(
                    "theme",
                    "Dark"
                )

                st.session_state.theme = theme

            st.session_state.role = role

            st.sidebar.success(
                "Login successful"
            )

            st.rerun()

        except Exception as e:

            st.sidebar.error(
                f"Login failed: {e}"
            )


# REGISTER


if choice == "Register":

    st.sidebar.subheader("📝 Register")

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
                "role": role,
                "theme": "Dark"

            })

            st.sidebar.success(
                "Verification email sent!"
            )

        except Exception as e:

            st.sidebar.error(
                f"Registration failed: {e}"
            )


# LOGIN REQUIRED


if not st.session_state.user:

    st.warning(
        "Please login to continue"
    )

    st.stop()


# USER INFO


uid = st.session_state.user["localId"]

st.sidebar.success(
    f'Logged in as:\n{st.session_state.user["email"]}'
)

if st.session_state.role == "admin":

    st.sidebar.success(
        "👑 Admin"
    )


# THEME


theme = st.sidebar.selectbox(
    "🌙 Theme",
    ["Dark", "Light"],
    index=0 if st.session_state.theme == "Dark" else 1
)

if theme != st.session_state.theme:

    st.session_state.theme = theme

    db.collection(
        "users"
    ).document(uid).update({

        "theme": theme

    })

    st.rerun()
 
 # =========================================================
# ADMIN PANEL
# =========================================================

if st.session_state.role == "admin":

    with st.expander(
        "👑 Admin Panel"
    ):

        # =========================================================
        # ADD SONG
        # =========================================================

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

            else:

                new_row = {

                    "track_name": new_track,
                    "artists": new_artist,
                    "track_genre": new_genre,
                    "mood": new_mood,
                    "popularity": new_popularity,
                    "energy": new_energy,
                    "valence": new_valence

                }

                try:

                    admin_df = pd.read_csv(
                        "admin_songs.csv"
                    )

                except:

                    admin_df = pd.DataFrame()

                admin_df = pd.concat(
                    [
                        admin_df,
                        pd.DataFrame([new_row])
                    ],
                    ignore_index=True
                )

                admin_df.to_csv(
                    "admin_songs.csv",
                    index=False
                )

                st.success(
                    "Song added successfully!"
                )

                st.cache_data.clear()

                st.rerun()

        st.markdown("---")

        # =========================================================
        # MANAGE SONGS
        # =========================================================

        st.subheader(
            "🎵 Manage Added Songs"
        )

        try:

            admin_df = pd.read_csv(
                "admin_songs.csv"
            )

        except:

            admin_df = pd.DataFrame()

        if not admin_df.empty:

            selected_song = st.selectbox(

                "Select Song",

                admin_df.apply(
                    lambda x:
                    f'{x["track_name"]} — {x["artists"]}',
                    axis=1
                ).tolist()
            )

            selected_index = admin_df.apply(
                lambda x:
                f'{x["track_name"]} — {x["artists"]}',
                axis=1
            ).tolist().index(selected_song)

            row = admin_df.iloc[selected_index]

            edit_track = st.text_input(
                "Edit Song Name",
                value=row["track_name"]
            )

            edit_artist = st.text_input(
                "Edit Artist",
                value=row["artists"]
            )

            edit_genre = st.text_input(
                "Edit Genre",
                value=row["track_genre"]
            )

            edit_mood = st.selectbox(
                "Edit Mood",
                [
                    "happy",
                    "sad",
                    "angry",
                    "calm"
                ],
                index=[
                    "happy",
                    "sad",
                    "angry",
                    "calm"
                ].index(row["mood"])
            )

            edit_popularity = st.slider(
                "Edit Popularity",
                0,
                100,
                int(row["popularity"])
            )

            edit_energy = st.slider(
                "Edit Energy",
                0.0,
                1.0,
                float(row["energy"])
            )

            edit_valence = st.slider(
                "Edit Valence",
                0.0,
                1.0,
                float(row["valence"])
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "💾 Save Changes"
                ):

                    admin_df.loc[selected_index] = {

                        "track_name": edit_track,
                        "artists": edit_artist,
                        "track_genre": edit_genre,
                        "mood": edit_mood,
                        "popularity": edit_popularity,
                        "energy": edit_energy,
                        "valence": edit_valence

                    }

                    admin_df.to_csv(
                        "admin_songs.csv",
                        index=False
                    )

                    st.success(
                        "Song updated successfully!"
                    )

                    st.cache_data.clear()

                    st.rerun()

            with col2:

                if st.button(
                    "🗑 Delete Song"
                ):

                    admin_df = admin_df.drop(
                        selected_index
                    )

                    admin_df.to_csv(
                        "admin_songs.csv",
                        index=False
                    )

                    st.success(
                        "Song deleted successfully!"
                    )

                    st.cache_data.clear()

                    st.rerun()

        else:

            st.info(
                "No admin-added songs yet."
            )

# LOGOUT


if st.sidebar.button("Logout"):

    st.session_state.user = None
    st.session_state.role = "user"
    st.session_state.recommended = None

    st.rerun()


# FILTERS


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


# SEARCH


search = st.text_input(
    "🔍 Search song or artist"
)


# GET RECOMMENDATIONS


if st.button(
    "🎵 Get Recommendations",
    use_container_width=True
):

    db.collection(
        "mood_history"
    ).add({

        "uid": uid,
        "mood": mood,
        "timestamp": datetime.utcnow()

    })

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

        st.session_state.recommended = None

    else:

        st.session_state.recommended = filtered.sort_values(
            "popularity",
            ascending=False
        ).head(n)

# SHOW RECOMMENDATIONS


if st.session_state.recommended is not None:

    recommended = st.session_state.recommended

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

        if st.button(
            "❤️ Favorite",
            key=f"fav_{i}"
        ):

            favorite_exists = list(
                db.collection("favorites")
                .where("uid", "==", uid)
                .where("track_name", "==", row["track_name"])
                .where("artist", "==", row["artists"])
                .stream()
            )

            if favorite_exists:

                st.warning(
                    "Already in favorites."
                )

            else:

                db.collection(
                    "favorites"
                ).add({

                    "uid": uid,
                    "track_name": row["track_name"],
                    "artist": row["artists"]

                })

                st.success(
                    "Added to favorites!"
                )

                st.rerun()


# MOOD HISTORY


st.markdown("## 🧠 Your Mood History")

history_docs = db.collection(
    "mood_history"
).where(
    "uid",
    "==",
    uid
).stream()

history = []

for doc in history_docs:

    data = doc.to_dict()

    history.append(
        data["mood"]
    )

if history:

    history_df = pd.DataFrame(
        history,
        columns=["mood"]
    )

    mood_counts = history_df[
        "mood"
    ].value_counts()

    top_count = mood_counts.max()

    top_moods = mood_counts[
        mood_counts == top_count
    ].index.tolist()

    if len(top_moods) == 1:

        top_mood_text = top_moods[0]

    else:

        top_mood_text = ", ".join(top_moods)

    total = len(history)

    st.info(
        f"Most selected mood: {top_mood_text}"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Total Mood Selections",
        total
    )

    c2.metric(
        "Most Selected Mood",
        top_mood_text
    )

else:

    st.warning(
        "No mood history yet."
    )


# =========================================================
# FAVORITE SONGS
# =========================================================

with st.expander(
    "❤️ Your Favorite Songs",
    expanded=True
):

    favorite_search = st.text_input(
        "🔍 Search favorite song"
    )

    favorite_docs = db.collection(
        "favorites"
    ).where(
        "uid",
        "==",
        uid
    ).stream()

    favorites = []

    for doc in favorite_docs:

        data = doc.to_dict()

        data["doc_id"] = doc.id

        favorites.append(data)

    if favorite_search:

        normalized_search = normalize_text(
            favorite_search
        )

        favorites = [

            fav for fav in favorites

            if
            normalized_search
            in
            normalize_text(
                fav["track_name"]
            )

            or

            normalized_search
            in
            normalize_text(
                fav["artist"]
            )
        ]

    if favorites:

        for i, fav in enumerate(favorites, 1):

            with st.container():

                st.markdown(
                    f"""
                    <div class="song-card">
                    <div class="song-title">
                    🎵 {fav["track_name"]}
                    </div>
                    <div class="song-info">
                    🎤 {fav["artist"]}
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                query = (
                    f'{fav["track_name"]} '
                    f'{fav["artist"]}'
                )

                youtube_url = (
                    "https://www.youtube.com/results?"
                    "search_query="
                    +
                    query.replace(" ", "+")
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.link_button(
                        "▶ YouTube",
                        youtube_url,
                        use_container_width=True,
                        key=f'youtube_{fav["doc_id"]}'
                    )

                with col2:

                    if st.button(
                        "🗑 Remove",
                        use_container_width=True,
                        key=f'remove_{fav["doc_id"]}'
                    ):

                        db.collection(
                            "favorites"
                        ).document(
                            fav["doc_id"]
                        ).delete()

                        st.success(
                            "Removed from favorites!"
                        )

                        st.rerun()

    else:

        st.info(
            "No favorite songs found."
        )

# FOOTER


st.caption(
    "🎵 MoodTracks — AI Music Recommendation System"
)