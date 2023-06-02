import pandas as pd

def duplicates(main_tracklist, sample_tracklist):

    sample_duplicates = sample_tracklist.duplicated(subset = ['Track Name', 'Artist Name']).sum()

    if sample_duplicates >= 0:
        ###########################################################################
        #Cleaning from duplicates - within sample_tracklist
        ###########################################################################
        sample_tracklist = sample_tracklist.loc[~sample_tracklist[['Track Name', 'Artist Name']].duplicated()]
        ###########################################################################
        #Removing song from sample_playlist_df which are in main_playlist_df too
        ###########################################################################
        both_duplicates =  main_tracklist[['Artist Name', 'Track Name']].merge(sample_tracklist[['Artist Name', 'Track Name']], how = 'inner')     
        sample_tracklist_conc = pd.concat([sample_tracklist, both_duplicates])
        sample_tracklist = sample_tracklist_conc.drop_duplicates(subset=['Artist Name', 'Track Name'], keep = False)
        ###########################################################################
        #Summary
        ###########################################################################
        print('Summary:')
        print('(1)Number of duplicates within sample playlist:', sample_duplicates)
        print('(2)Number of duplicates between playlists:', len(both_duplicates))
        print('Preprocessor state: Finish')
        
        return sample_tracklist