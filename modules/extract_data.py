from modules.authenticator import authenticator
import pandas as pd
import time
import sys
import streamlit as st

def extract_data(sp, info_dict, url_types):
    #Initialize Spotify user credentials
    sp = authenticator()

    api_calls = 0

    track_uris = []
    track_names = []
    albums = []
    track_popularities = []
    track_popularity = []
    artist_names = []  
    artist_popularities = []  
    artist_genres = [] 
    release_dates = []

    for i in range(len(info_dict)):

        # Record the start time
        start_time = time.time()

        url_type = url_types[i]
        item = info_dict[i]

        # Extract track URI
        if url_type in ['playlist', 'track']:
            track_uri = item['track']['uri']
        elif url_type in 'album':
            track_uri = item['uri']
        elif url_type == 'artist':
            track_uri = item['track']['uri']
        else:
            track_uri = None

        # Extract track name
        if url_type in ['playlist', 'track']:
            track_name = item['track']['name'] if 'name' in item['track'] else None
        elif url_type in 'album':
            track_name = item['name'] if 'name' in item else None
        elif url_type == 'artist':
            track_name = item['track']['name'] if 'name' in item['track'] else None
        else:
            track_uri = None

        # Extract album name
        if url_type in ['playlist', 'track']:
            album = item['track']['album']['name'] if 'album' in item['track'] else None
        elif url_type in 'album':
            uri = item['id']
            url = sp.track(uri)
            api_calls = api_calls + 1
            album = url['album']['name'] if 'name' in url['album'] else None
        elif url_type == 'artist':
            if 'album' in item['track']:
                album = item['track']['album']['name']
            else:
                album = None

        # Extract track popularity
        if url_type in ['playlist', 'track']:
            track_popularity = item['track']['popularity'] if 'popularity' in item['track'] else None
        elif url_type in 'album':
            uri = item['id']
            url = sp.track(uri)
            track_popularity = url['popularity'] if 'popularity' in url else None
            api_calls = api_calls + 1
        elif url_type == 'artist':
            track_popularity = item['track']['popularity'] if 'popularity' in item['track'] else None

        # Extract artist name
        if url_type in ['playlist', 'track']:
            artist = item['track']['artists'][0]['name'] if 'artists' in item['track'] else None
        elif url_type in 'album':
            artist = item['artists'][0]['name'] if 'name' in item['artists'][0] else None
        elif url_type == 'artist':
            artist = item['track']['artists'][0]['name'] if 'name' in item['track']['artists'][0] else None

        # Extract artist popularity
        if url_type in ['playlist', 'track']:
            artist_popularity = sp.artist(item['track']['artists'][0]['id'])['popularity'] if 'artists' in item['track'] else None
            api_calls = api_calls + 1
        elif url_type in 'album':
            uri = item['artists'][0]['external_urls']
            uri = uri['spotify']
            url = sp.artists([uri])
            artist_popularity = url['artists'][0]['popularity'] if 'popularity' in url['artists'][0] else None
            api_calls = api_calls + 1
        elif url_type == 'artist':
            artist_popularity = sp.artist(item['track']['artists'][0]['id'])['popularity'] if 'artists' in item['track'] else None
            api_calls = api_calls + 1

        # Extract artist genres
        if url_type in ['playlist', 'track']:
            artist_info = sp.artist(item['track']['artists'][0]['id']) if 'artists' in item['track'] else None
            #genres = artist_info['genres'] if artist_info is not None else None - all genres
            genres = artist_info['genres'][0] if artist_info and artist_info['genres'] else 'None'
            api_calls = api_calls + 1
        elif url_type in 'album':
            uri = item['artists'][0]['external_urls']
            uri = uri['spotify']
            url = sp.artists([uri])
            #genres = url['artists'][0]['genres'] if 'genres' in url['artists'][0] else None - all genres
            genres = url['artists'][0]['genres'] if 'genres' in url['artists'][0] else 'None'
            api_calls = api_calls + 1
        elif url_type in 'artist':
            artist_info = sp.artist(item['track']['artists'][0]['id']) if 'artists' in item['track'] else None
            #genres = artist_info['genres'] if artist_info is not None else None - all genres
            genres = artist_info['genres'] if artist_info and 'genres' in artist_info else None
            api_calls = api_calls + 1
        
        #Extract release date
        if url_type in ['playlist', 'track']:
            release_date = item['track']['album']['release_date'] if 'album' in item['track'] else None
        elif url_type in 'album':
            uri = item['id']
            url = sp.track(uri)
            release_date = url['album']['release_date'] if 'release_date' in url['album'] else None
            api_calls = api_calls + 1
        elif url_type == 'artist':
            release_date = item['track']['album']['release_date'] if 'album' in item['track'] else None

        #Record the end time
        end_time = time.time()
        #Calculate the execution time in seconds
        execution_time = end_time - start_time
        #For terminal  
        print(i + 1, '/', len(info_dict), 'tracks extracted.', f'Execution time: {execution_time:3f} seconds')
        sys.stdout.write('\033[F')
        #For streamlit
        #st.write(i + 1, '/', len(info_dict), 'tracks extracted.', f'Execution time: {execution_time:.3f} seconds')


        track_uris.append(track_uri)
        track_names.append(track_name)
        albums.append(album)
        track_popularities.append(track_popularity)
        artist_names.append(artist)
        artist_popularities.append(artist_popularity)
        artist_genres.append(genres)
        release_dates.append(release_date)
    
    st.write('Data has been extracted')

    audio_features = [list(sp.audio_features(uri)[0].values()) for uri in track_uris]

    feature_keys = list(sp.audio_features(track_uris[0])[0].keys())

    data_features_df = pd.DataFrame({'Track URI': track_uris,
                                     'Track Name': track_names,
                                     'Artist Name': artist_names,
                                     'Album': albums,
                                     'Release Year': release_dates,
                                     'Artist Genres': artist_genres,
                                     'Track Popularity': track_popularities,
                                     'Artist Popularity': artist_popularities})

    audio_features_df = pd.DataFrame(audio_features, columns=feature_keys).drop(
        ['type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature'], axis=1)

    playlist_df = pd.concat([data_features_df, audio_features_df], axis=1, join='inner') \
        #.set_index('Track URI')

    playlist_df['Release Year'] = pd.to_datetime(playlist_df['Release Year'])

    print('api_calls = ', api_calls)
    
    return playlist_df