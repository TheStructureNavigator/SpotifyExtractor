import pandas as pd

def one_hot(tracklist, column, new_name):
    ###########################################################################
    #One hot encoding
    ###########################################################################
    enc_column = pd.get_dummies(tracklist[column])
    features = enc_column.columns
    enc_column.columns = [new_name + '|' + str(int(i)) for i in features]
    
    return enc_column