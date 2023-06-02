from modules.authenticator import authenticator
from modules.duplicates import duplicates
from modules.one_hot import one_hot
from modules.vectorizer import vectorizer
from modules.normalizer import normalizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import streamlit as st

def recommender(main_tracklist, sample_tracklist):

    #Removing duplicates from sample_tracklist and in between tracklists
    sample_tracklist = duplicates(main_tracklist, sample_tracklist)

    #One hot encoder
    #main_tracklist
    m_enc_key = one_hot(main_tracklist, 'key', 'key').reset_index(drop = True)
    m_enc_mode = one_hot(main_tracklist, 'mode', 'mode').reset_index(drop = True)
    #sample_tracklist
    s_enc_key = one_hot(sample_tracklist, 'key', 'key').reset_index(drop = True)
    s_enc_mode = one_hot(sample_tracklist, 'mode', 'mode').reset_index(drop = True)

    #TF-IDF vectorizer
    m_vect_genres = vectorizer(main_tracklist, 'Artist Genres')
    s_vect_genres = vectorizer(sample_tracklist, 'Artist Genres')

    #Normalizer
    m_artist_pop_scaled, m_track_pop_scaled, m_floats_scaled = normalizer(main_tracklist)
    s_artist_pop_scaled, s_track_pop_scaled, s_floats_scaled = normalizer(sample_tracklist)

    #Creating dataframe of all neccesary values
    #main_tracklist
    normalize_m_tracklist = pd.concat([m_artist_pop_scaled, m_track_pop_scaled, m_vect_genres, m_enc_key, m_enc_mode, m_floats_scaled], axis = 1)
    #normalize_playlist_df['Track URI'] = main_playlist_df.index.values
    #normalize_playlist_df = normalize_playlist_df.set_index('Track URI') we dont need index but if we want, this line adds an indexing
    #sample_tracklist
    normalize_s_tracklist = pd.concat([s_artist_pop_scaled, s_track_pop_scaled, s_vect_genres, s_enc_key, s_enc_mode, s_floats_scaled], axis = 1)

    #Playlist summarizer - sum
    playlist_vector = normalize_m_tracklist.sum(axis = 0)
    #Playlist summarzer - mean
    #playlist_vector = normalize_m_tracklist.mean(axis = 0)

    #Playlist structures compability
    #Dropping genres from sample which are not in main
    for s_genre in normalize_s_tracklist.columns:
        for genre in normalize_m_tracklist.columns:
            flag = 0
            if s_genre == genre:
                flag =  1
                break

        if flag == 0:
            normalize_s_tracklist = normalize_s_tracklist.drop(columns = [s_genre])

    #Adding genres to sample which are in main
    for genre in normalize_m_tracklist.columns:
        for s_genre in normalize_s_tracklist.columns:
            flag = 0
            if genre == s_genre:
                flag = 1
                break
        if flag == 0:
            normalize_s_tracklist[genre] = 0

    #Compatibility of columns in sample playlist and playlist vector
    normalize_s_tracklist = normalize_s_tracklist[normalize_m_tracklist.columns]

    #Cosine similarity
    #Summarize playlist to a dataframe
    playlist_vector = pd.DataFrame(playlist_vector)
    playlist_vector = playlist_vector.transpose()
    #Calculating predictions
    predictions = cosine_similarity(normalize_s_tracklist, playlist_vector)
    #Predictions to a dataframe with tracks uris
    recommendations = pd.DataFrame(index = sample_tracklist.index)
    recommendations[['Track Name', 'Artist Name']] = sample_tracklist[['Track Name', 'Artist Name']]
    recommendations['Recommendations'] = predictions
    #Sorting recommendations
    recommendations = recommendations.sort_values(by = ['Recommendations'], ascending = False)

    print(recommendations.head(20))

    return recommendations