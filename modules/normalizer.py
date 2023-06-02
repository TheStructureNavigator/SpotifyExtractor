import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def normalizer(main_tracklist):

    #Normalization as a function - works only for one column
    def normalize(main_playlist_df, column):
        col_to_normalize = main_playlist_df[column].reset_index(drop = True)
        scaler = MinMaxScaler()
        col_scaled = pd.DataFrame(scaler.fit_transform(col_to_normalize.array.reshape(-1, 1)), columns = [column])

        return col_scaled
    
    #main_tracklist
    artist_pop_scaled = normalize(main_tracklist, 'Artist Popularity')
    track_pop_scaled = normalize(main_tracklist, 'Track Popularity')

    #Normalization - float values
    #Main
    floats = main_tracklist[['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']].reset_index(drop = True)
    scaler = MinMaxScaler()
    floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns = floats.columns)
    
    return artist_pop_scaled, track_pop_scaled, floats_scaled
