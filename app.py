from flask import Flask, request, redirect
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from recommender import generate_recommendations

app = Flask(__name__)

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
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

    recommendations = generate_recommendations(sp)

    html_output = ""
    for cluster, songs in recommendations.items():
        html_output += f"<h3>Cluster {cluster}</h3><ul>"
        for name, artist, pop in songs:
            html_output += f"<li>{name} — {artist} (popularity: {pop})</li>"
        html_output += "</ul>"

    return html_output

if __name__ == "__main__":
    app.run(debug=True)
