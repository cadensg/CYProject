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
        session.clear()
        code = request.args.get('code')
        if code is None:
            return "Authorization code not found", 400

        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        sp = spotipy.Spotify(auth=token_info['access_token'])
        recommendations = generate_recommendations(sp)
        return render_template('results.html', recs=recommendations)
        """
    except spotipy.exceptions.SpotifyException as e:
        print("Spotify API error:", e)
        return "Spotify authorization failed", 403
    except Exception as e:
        print("General error:", e)
        return "An error occurred", 500


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
