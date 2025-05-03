def search_track(sp, query):
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
