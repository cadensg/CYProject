from flask import Flask, request, redirect, session, url_for, render_template
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from recommender import generate_recommendations

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "gosteelers")

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-top-read"
)

@app.route("/")
def login():
    if 'token_info' in session:
        return redirect('/callback')  # or home/dashboard
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    try:
        code = request.args.get('code')
        if code is None:
            return "Authorization code not found", 400

        token_info = sp_oauth.get_cached_token()
        session['token_info'] = token_info
        sp = get_spotify_client()
        recommendations = generate_recommendations(sp)
        return render_template('results.html', recs=recommendations)
       
    except spotipy.exceptions.SpotifyException as e:
        print("Spotify API error:", e)
        return "Spotify authorization failed", 403
    except Exception as e:
        print("General error:", e)
        return "An error occurred", 500

def get_spotify_client():
    token_info = session.get('token_info', None)

    if not token_info:
        raise Exception("No token info in session")

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info  # update with new token

    return spotipy.Spotify(auth=token_info['access_token'])

"""
    html_output = ""
    for cluster, songs in recommendations.items():
        html_output += f"<h3>Cluster {cluster}</h3><ul>"
        for name, artist, pop in songs:
            html_output += f"<li>{name} — {artist} (popularity: {pop})</li>"
        html_output += "</ul>"

    return html_output
"""
if __name__ == "__main__":
    app.run(debug=True)
