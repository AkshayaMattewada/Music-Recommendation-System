import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotify client
CLIENT_ID = "2efeb510414b4e1bb9be38190ea58981"
CLIENT_SECRET = "89c8d0e72d4f4b86b07c1797bee275df"
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load preprocessed data and similarity matrix
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to get song album cover URL
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        song_link = track["external_urls"]["spotify"]
        return album_cover_url, song_link
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", None

# Function to recommend songs
def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    recommended_music_links = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        album_cover_url, song_link = get_song_album_cover_url(song_name, artist)
        recommended_music_posters.append(album_cover_url)
        recommended_music_names.append(song_name)
        recommended_music_links.append(song_link)
    return recommended_music_names, recommended_music_posters, recommended_music_links

# Function to get default popular songs (first 20 songs from the dataset)
def get_default_popular_songs():
    popular_music_names = music['song'][:20].tolist()
    popular_music_posters = []
    popular_music_links = []
    for song_name in popular_music_names:
        artist = music[music['song'] == song_name]['artist'].values[0]
        album_cover_url, song_link = get_song_album_cover_url(song_name, artist)
        popular_music_posters.append(album_cover_url)
        popular_music_links.append(song_link)
    return popular_music_names, popular_music_posters, popular_music_links

# Streamlit UI
st.markdown("""
    <style>
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0');
            background-size: cover;
            background-position: center;
            color: white;
        }
        .main-title {
            font-family: 'Pacifico', cursive;
            font-size: 3rem;
            text-align: center;
            margin-bottom: 20px;
            color: #000000;
        }
        .sub-title {
            font-size: 1.5rem;
            text-align: center;
            margin-top: 20px;
            color: #ffffff;
        }
        .song-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #ffffff;
            margin-top: 10px;
        }
        .album-cover {
            border-radius: 10px;
            transition: transform 0.2s;
            margin-bottom: 20px;
        }
        .album-cover:hover {
            transform: scale(1.05);
        }
        .recommendation-section {
            background: rgba(75, 0, 130, 0.8);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #4b0082;
            color: white;
            border-radius: 12px;
            font-size: 16px;
            padding: 10px 20px;
            margin: 20px auto;
            display: block;
        }
        .stSelectbox>div {
            background-color: #4b0082;
            color: white;
            border-radius: 12px;
            font-size: 16px;
            padding: 10px 20px;
            margin: 20px auto;
            display: block;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>🎵 Music Recommender System</div>", unsafe_allow_html=True)

music_list = music['song'].values
selected_song = st.selectbox("Type or select a song from the dropdown", music_list)

if st.button('Show Recommendation'):
    st.markdown("<div class='sub-title'>Recommended Songs</div>", unsafe_allow_html=True)
    recommended_music_names, recommended_music_posters, recommended_music_links = recommend(selected_song)
    st.markdown("<div class='recommendation-section'>", unsafe_allow_html=True)
    cols = st.columns(len(recommended_music_names))
    for i, col in enumerate(cols):
        col.markdown(f"""
            <div style="text-align: center;">
                <a href="{recommended_music_links[i]}" target="_blank">
                    <img src="{recommended_music_posters[i]}" class="album-cover" style="max-width: 200px; height: auto;">
                </a>
                <div class="song-title">{recommended_music_names[i]}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='sub-title'>Popular Songs</div>", unsafe_allow_html=True)
popular_music_names, popular_music_posters, popular_music_links = get_default_popular_songs()
st.markdown("<div class='recommendation-section'>", unsafe_allow_html=True)

num_songs = len(popular_music_names)
num_cols = 5  # Adjust number of columns to display songs in rows
num_rows = (num_songs // num_cols) + (num_songs % num_cols > 0)

for row in range(num_rows):
    cols = st.columns(num_cols)
    for col_index in range(num_cols):
        song_index = row * num_cols + col_index
        if song_index < num_songs:
            with cols[col_index]:
                st.markdown(f"""
                    <div style="text-align: center;">
                        <a href="{popular_music_links[song_index]}" target="_blank">
                            <img src="{popular_music_posters[song_index]}" class="album-cover" style="max-width: 200px; height: auto;">
                        </a>
                        <div class="song-title">{popular_music_names[song_index]}</div>
                    </div>
                """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
