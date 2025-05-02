#pip install flask spotipy
#pip freeze > requirements.txt
# app.py
from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

sp_oauth = SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="https://yourapp.onrender.com/callback",
    scope="user-top-read"
)

@app.route("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    top_tracks = sp.current_user_top_tracks(limit=10)
    return "<br>".join([f"{t['name']} - {t['artists'][0]['name']}" for t in top_tracks['items']])

if __name__ == "__main__":
    app.run()

from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# 1) Authenticate and get token
scope = "user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# 2) Fetch your top tracks (last 6 months)
top = sp.current_user_top_tracks(limit=50, time_range='medium_term')
track_ids = [t['id'] for t in top['items']]

# 3) Get audio features
features = sp.audio_features(track_ids)
df_feats = pd.DataFrame(features).set_index('id')

from sklearn.cluster import KMeans

# Select numeric features for clustering
X = df_feats[['danceability','energy','acousticness','valence']]

# KMeans: choose k based on elbow method or domain knowledge
k = 3
km = KMeans(n_clusters=k, random_state=42).fit(X)
df_feats['cluster'] = km.labels_
centroids = km.cluster_centers_

def niche_recs(seed_tracks, max_pop=40, limit=10):
    recs = sp.recommendations(
        seed_tracks=seed_tracks, 
        limit=limit,
        max_popularity=max_pop
    )['tracks']
    return [(r['name'], r['artists'][0]['name'], r['popularity']) for r in recs]

# For each cluster, pick 2 seeds and get 5 niche tracks
niche_suggestions = {}
for c in range(k):
    seeds = df_feats[df_feats['cluster']==c].sample(2).index.tolist()
    niche_suggestions[c] = niche_recs(seeds, max_pop=35, limit=5)

# Print results
for cluster, songs in niche_suggestions.items():
    print(f"\nCluster {cluster}:")
    for name, artist, pop in songs:
        print(f"  • {name} — {artist} (pop. {pop})")

# Assuming you have a valid Spotify client object `sp`
def search_track(query):
    result = sp.search(q=query, type='track', limit=1)
    tracks = result.get('tracks', {}).get('items', [])
    if tracks:
        return {
            'uri': tracks[0]['uri'],
            'name': tracks[0]['name'],
            'artist': tracks[0]['artists'][0]['name'],
            'popularity': tracks[0]['popularity']
        }
    return None

# Map metadata strings to track URIs
mapped_tracks = []
for entry in song_metadata:
    match = search_track(entry)
    if match:
        mapped_tracks.append(match)

# Output example
for track in mapped_tracks:
    print(f"{track['name']} — {track['artist']} ({track['popularity']}) → {track['uri']}")
