"""
import pandas as pd
from sklearn.cluster import KMeans

def generate_recommendations(sp, k=3, seed_limit=2, rec_limit=5, max_pop=35):
    top = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    track_ids = [t['id'] for t in top['items']]

    features = sp.audio_features(track_ids)
    df_feats = pd.DataFrame(features).set_index('id')
    X = df_feats[['danceability','energy','acousticness','valence']]

    km = KMeans(n_clusters=k, random_state=42).fit(X)
    df_feats['cluster'] = km.labels_

    niche_suggestions = {}
    for c in range(k):
        seeds = df_feats[df_feats['cluster']==c].sample(seed_limit).index.tolist()
        raw_recs = sp.recommendations(seed_tracks=seeds, limit=rec_limit*2)['tracks']
        filtered_recs = [r for r in raw_recs if r['popularity'] <= max_pop][:rec_limit]
        niche_suggestions[c] = [(r['name'], r['artists'][0]['name'], r['popularity']) for r in filtered_recs]

    return niche_suggestions
----
import pandas as pd
from sklearn.cluster import KMeans

def generate_recommendations(sp, k=3, seed_limit=2, rec_limit=5, max_pop=35):
    valid_track_ids = [track['id'] for track in top['items'] if track and track['id']]
    top = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    
    # Gather basic metadata
    tracks = []
    for t in top['items']:
        tracks.append({
            'id': t['id'],
            'name': t['name'],
            'popularity': t['popularity'],
            'artist': t['artists'][0]['name'],
            'artist_id': t['artists'][0]['id'],
        })
    df = pd.DataFrame(tracks).set_index('id')

    # Use normalized popularity as a simple feature
    df['popularity_norm'] = df['popularity'] / 100.0

    # Perform basic clustering on popularity (or enhance with artist genre later)
    X = df[['popularity_norm']]
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    df['cluster'] = km.labels_

    niche_suggestions = {}
    for c in range(k):
        seeds = df[df['cluster'] == c].sample(min(seed_limit, len(df[df['cluster'] == c]))).index.tolist()
        raw_recs = sp.recommendations(seed_tracks=seeds, limit=rec_limit * 2)['tracks']
        filtered_recs = [r for r in raw_recs if r['popularity'] <= max_pop][:rec_limit]
        niche_suggestions[c] = [(r['name'], r['artists'][0]['name'], r['popularity']) for r in filtered_recs]

    return niche_suggestions
"""
import pandas as pd
from sklearn.cluster import KMeans
import random

def generate_recommendations(sp, k=3, seed_limit=2, rec_limit=5, max_pop=35):
    try:
        top = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    except Exception as e:
        print(f"Error fetching top tracks: {e}")
        return {}

    valid_tracks = [t for t in top['items'] if t and t.get('id')]

    tracks = []
    for t in valid_tracks:
        tracks.append({
            'id': t['id'],
            'name': t['name'],
            'popularity': t['popularity'],
            'artist': t['artists'][0]['name'],
            'artist_id': t['artists'][0]['id'],
        })
    df = pd.DataFrame(tracks).set_index('id')

    if df.empty:
        print("No valid tracks to process.")
        return {}

    df['popularity_norm'] = df['popularity'] / 100.0
    X = df[['popularity_norm']]
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    df['cluster'] = km.labels_

    niche_suggestions = {}
    for c in range(k):
        cluster_df = df[df['cluster'] == c]
        if cluster_df.empty:
            continue

        seed_tracks = cluster_df.sample(min(seed_limit, len(cluster_df))).index.tolist()
        valid_seed_tracks = []

        # Validate seed tracks
        for tid in seed_tracks:
            try:
                sp.track(tid)  # will throw error if invalid or unplayable
                valid_seed_tracks.append(tid)
            except:
                print(f"Invalid seed track skipped: {tid}")
                continue

        # 1. Try with valid track seeds
        try:
            if valid_seed_tracks:
                raw_recs = sp.recommendations(seed_tracks=valid_seed_tracks, limit=rec_limit * 2)['tracks']
                filtered = [r for r in raw_recs if r['popularity'] <= max_pop][:rec_limit]
                if filtered:
                    niche_suggestions[c] = [(r['name'], r['artists'][0]['name'], r['popularity']) for r in filtered]
                    continue
        except Exception as e:
            print(f"Track seed failed for cluster {c}: {e}")

        # 2. Fallback: use artist seeds
        try:
            artist_ids = list(cluster_df['artist_id'].dropna().unique())
            if artist_ids:
                sampled_artists = random.sample(artist_ids, min(seed_limit, len(artist_ids)))
                raw_recs = sp.recommendations(seed_artists=sampled_artists, limit=rec_limit * 2)['tracks']
                filtered = [r for r in raw_recs if r['popularity'] <= max_pop][:rec_limit]
                if filtered:
                    niche_suggestions[c] = [(r['name'], r['artists'][0]['name'], r['popularity']) for r in filtered]
                    continue
        except Exception as e:
            print(f"Artist seed failed for cluster {c}: {e}")

        # 3. Fallback: empty result
        niche_suggestions[c] = []

    return niche_suggestions

