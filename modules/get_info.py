from modules.authenticator import authenticator

def get_info(sp, playlist_urls, category = 'top'):
    
    info_dict = [] #Variable to store playlist track information
    url_types = [] #Variable to store the types of URLs
    
    for url in playlist_urls:
        
        api_calls = 0

        #Extract URI from the URL
        uri = url.split('/')[-1].split('?')[0]
        
        #Get dictionary
        if 'playlist' in url:
            url_type = 'playlist'
            items = sp.playlist_items(uri)['items']
            api_calls = api_calls + 1
        elif 'album' in url:
            url_type = 'album'
            items = sp.album_tracks(uri)['items']
            api_calls = api_calls + 1
        elif 'track' in url:
            url_type = 'track'
            track_info = sp.track(uri)
            items = [{'track': track_info}]
            api_calls = api_calls + 1
        elif 'artist' in url:
            url_type = 'artist'
            if category == 'top':
                top_tracks = sp.artist_top_tracks(uri)['tracks']
                items = [{'track': track} for track in top_tracks]
                api_calls = api_calls + 1
            # elif category == 'all':
            #     albums = sp.artist_albums(uri)['items']
            #     items = []
            #     for album in albums:
            #         album_tracks = sp.album_tracks(album['uri'])['items']
            #         items += [{'track': track} for track in album_tracks]
            #     api_calls = api_calls + 1
            else:
                print("Invalid category. Choose between 'top' and 'all'.")
                continue
        else:
            print("Invalid type. Choose between playlist, album, track, and artist.")
            continue
        
        info_dict += items
        url_types += [url_type] * len(items)  #Append url_type for each item

    print('api_calls = ', api_calls)
    
    return info_dict, url_types 
