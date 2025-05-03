def search_track(sp, query):
    try:
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
    except Exception as e:
        print(f"Error searching for track '{query}': {e}")
        return None
