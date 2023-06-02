import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

def vectorizer(main_tracklist, column):
    ###########################################################################
    #Genre vectorizer
    ###########################################################################
    vectorizer = TfidfVectorizer()
    vectorizer_matrix = vectorizer.fit_transform(main_tracklist[column])
    vect_genres = pd.DataFrame(vectorizer_matrix.toarray())
    vect_genres.columns = ['Genre' + '|' + i for i in vectorizer.get_feature_names_out()]
    
    return vect_genres