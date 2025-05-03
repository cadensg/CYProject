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
