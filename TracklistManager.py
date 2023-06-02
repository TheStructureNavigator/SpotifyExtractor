#Dependencies#
from modules.authenticator import authenticator
from modules.get_info import get_info
from modules.extract_data import extract_data
from modules.recommender import recommender
from modules.duplicates import duplicates
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import os
import seaborn as sns
import numpy as np
from tkinter import Tk, filedialog

#Initialize Spotify User Credentials#
sp = authenticator()

#Function to load CSV file and return dataframe
def load_data(file):
    df = pd.read_csv(file)
    return df

#Function to save dataframe to CSV file
def save_data(df, file):

    root = Tk()
    root.withdraw()

    folder_path = "dataframes"
    file_path = os.path.join(folder_path, file)
    df.to_csv(file_path, index=False)

#Title
st.title("TRACKLIST MANAGER")
st.divider()

################################################################
#Extractor
#################################################################

#Description
st.header('Data Extractor')
st.markdown(
    """
    __The Data Extractor module enables users 
    to directly extract data from the Spotify 
    Database. To extract specific information, 
    users need to provide a list of URLs for 
    the desired tracks, playlists, albums, or 
    artists (only top songs). The module allows users to create 
    a dataframe of tracks, including additional 
    information about each track, which can be 
    used for further analysis.__ \n
    __There are two methods to provide Uniform 
    Resource Locators (URLs):__ \n
    1. By manually entering a list of 
    comma-separated URLs.
    2. By uploading a text file that contains 
    a comma-separated list of URLs.
    """)
#-------------------------------------------------------------

#Checkbox to hide/unhide the "Data Extractor" section
show_data_extractor = st.expander("__Show Data Extractor__")
#-------------------------------------------------------------

with show_data_extractor:

    extraction_option = st.radio(
        '__Select extraction option:__', ('Enter URLs', 'Upload URLs file'))

    if extraction_option == 'Enter URLs':
        user_input = st.text_input("Enter URLs (comma-separated):")
        urls = user_input.split(',')

        if user_input is not None:
            start_extracting = st.button('Start Extracting')

            if start_extracting:

                st.write('Extraction in progress...')
                info_dict, url_types = get_info(sp, urls)
                extracted_df = extract_data(sp, info_dict, url_types)
                st.write('Extraction completed')

                if 'extracted_tracklist' not in st.session_state:
                    st.session_state['extracted_tracklist'] = pd.DataFrame()

                st.session_state['extracted_tracklist'] = extracted_df

    elif extraction_option == 'Upload URLs file':
        load_input = st.file_uploader(
            "Upload a file that contains a list of comma-separated URLs:", type=["txt"])

        if load_input is not None:
            start_extracting = st.button('Start Extracting')
            urls_file_content = load_input.read().decode("utf-8")
            urls = urls_file_content.split(',')

            if start_extracting:
                if load_input is not None:

                    st.write("Extracted URLs:")
                    st.write(", ".join(urls))
                    st.write('Extraction in progress...')

                    info_dict, url_types = get_info(sp, urls)
                    extracted_df = extract_data(sp, info_dict, url_types)

                    st.write('Extraction completed')

                    if 'extracted_tracklist' not in st.session_state:
                        st.session_state['extracted_tracklist'] = pd.DataFrame()

                    st.session_state['extracted_tracklist'] = extracted_df

    if 'extracted_tracklist' in st.session_state:

        if st.checkbox('Show extracted dataframe'):

            st.write("Extracted Dataframe:")
            st.dataframe(st.session_state['extracted_tracklist'])

            save_extracted_dataframe = st.button('Save Extracted Dataframe')

            if save_extracted_dataframe:
                save_data(
                    st.session_state['extracted_tracklist'], "extracted_dataframe.csv")
                st.write("Extracted Dataframe has been saved.")
                st.write("File saved as 'extracted_dataframe.csv'.")

    else:

        st.write('Extract data to display')

st.divider()

################################################################
#Loader
#################################################################
st.header('Data Loader')
st.markdown(
    """
    __The Data Loader module allows users 
    to load previously extracted or prepared 
    dataframes. The loaded dataframes can be 
    edited and saved to a new file for further 
    processing or analysis. Additionally, 
    the module provides additional information 
    about the loaded data to assist users in 
    their analysis tasks. Information scheme is
    constructed for extractor module data.__
    """)

# Checkbox to hide/unhide the "Data loader" section
show_data_loader = st.expander("__Show Data Loader__")

with show_data_loader:

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a CSV file that contains a prepared dataframe:", type=["csv"])

    if uploaded_file is not None:
        # Load DataFrame from uploaded file
        original_df = load_data(uploaded_file)

        # Initialize session state
        if 'original_tracklist' not in st.session_state:
            st.session_state['original_tracklist'] = pd.DataFrame()

        # Update session state
        st.session_state['original_tracklist'] = original_df

        # Initialize session state
        if 'editable_tracklist' not in st.session_state:
            st.session_state['editable_tracklist'] = pd.DataFrame()

            # Update session state
            st.session_state['editable_tracklist'] = original_df.copy()

        # Checkbox to toggle visibility of original DataFrame
        show_original = st.checkbox("Show Original Dataframe")

        if show_original:

            # Create tabs for Original DataFrame and Additional Summary
            tab1, tab2 = st.tabs(["Original Dataframe", "Additional Summary"])

            with tab1:
                st.dataframe(st.session_state['original_tracklist'])
                st.divider()

            with tab2:
                num_rows = len(st.session_state['original_tracklist'])
                st.write(f"Number of Rows: {num_rows}")
                num_columns = len(
                    st.session_state['original_tracklist'].columns)
                st.write(f"Number of Columns: {num_columns}")
                st.write(st.session_state['original_tracklist'].describe())

        # Button to toggle visibility of Editable DataFrame
        show_editable = st.checkbox("Show Editable Dataframe")

        st.divider()

        if show_editable:

            # Button to toggle visibility of Edit Settings
            editor_settings = st.checkbox('Edit Settings')

            if editor_settings:

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Button to toggle visibility of index setter
                    set_index = st.checkbox('Set index')

                    if set_index:

                        # Find columns with all different elements
                        unique_columns = [col for col in st.session_state['editable_tracklist'].columns if st.session_state['editable_tracklist'][col].nunique(
                        ) == len(st.session_state['editable_tracklist'])]  # !

                        # Radio buttons to select the index column
                        index_column = st.radio(
                            "Select the column to set as index:", unique_columns)

                        # Add a button to set index
                        if st.button("Set Index"):

                            editable_df = st.session_state['editable_tracklist']

                            # Set the selected column as the index
                            editable_df.set_index(index_column, inplace=True)
                            st.write("Index has been set")

                            # Update the editable_df in session state with the modified version
                            st.session_state['editable_tracklist'] = editable_df

                with col2:
                    # Button to toggle visibility of column dropper
                    drop_column = st.checkbox('Drop Column')

                    if drop_column:

                        # Get the list of columns in the editable dataframe
                        columns = st.session_state['editable_tracklist'].columns.tolist(
                        )

                        # Multi-select box to select columns to drop
                        columns_to_drop = st.multiselect(
                            'Select columns to drop:', columns)

                        if len(columns_to_drop) > 0:

                            editable_df = st.session_state['editable_tracklist']

                            # Drop the selected columns from the editable dataframe
                            editable_df.drop(
                                columns_to_drop, axis=1, inplace=True)
                            st.write("Columns have been dropped")

                            # Update the editable_df in session state with the modified version
                            st.session_state['editable_tracklist'] = editable_df

                with col3:
                    # Button to toggle visibility of dataframe sorter
                    sort_dataframe = st.checkbox('Sort Dataframe')

                    if sort_dataframe:

                        # Get the list of columns in the editable dataframe
                        columns = st.session_state['editable_tracklist'].columns.tolist(
                        )

                        # Selectbox to select the column to sort by
                        sort_column = st.selectbox(
                            'Select column to sort by:', columns)

                        # Radio buttons to select the sort order
                        sort_order = st.radio("Select sort order:", [
                                              'Ascending', 'Descending'])

                        editable_df = st.session_state['editable_tracklist']

                        # Sort the dataframe based on the selected column and sort order
                        if sort_order == 'Ascending':

                            editable_df.sort_values(
                                by=sort_column, ascending=True, inplace=True)
                        else:
                            editable_df.sort_values(
                                by=sort_column, ascending=False, inplace=True)

                        st.write("Dataframe has been sorted")

                        # Update the editable_df in session state with the modified version
                        st.session_state['editable_tracklist'] = editable_df

                with col4:
                    # Button to reset edited settings to original dataframe
                    reset_settings = st.button('Reset Edited Settings')

                    if reset_settings:

                        # Restore the original dataframe to the editable dataframe
                        original_df = st.session_state['original_tracklist']

                        # Update the editable_df in session state to original
                        st.session_state['editable_tracklist'] = original_df.copy(
                        )

                        st.write("Edited settings have been reset")

            st.write("Editable DataFrame:")
            st.dataframe(st.session_state['editable_tracklist'])

            # Button to save edited dataframe
            save_dataframe = st.button('Save Edited Dataframe')

            if save_dataframe:
                edited_df = st.session_state['editable_tracklist']
                save_data(edited_df, "edited_dataframe.csv")
                st.write("Edited Dataframe has been saved.")

st.divider()

################################################################
#Updater
#################################################################
st.header('Data Updater')
st.markdown(
    """
    __The Data Updater allows users to update existing tracklist
    by adding additional tracks to them. Only information 
    about tracks that are not yet included in the updated 
    tracklist will be extracted__
    """)

# Checkbox to hide/unhide the "Data loader" section
show_data_updater = st.expander("__Show Data Updater__")

with show_data_updater:

    # Tracklist to update loader
    tracklist_to_update = st.file_uploader(
        "__Upload the CSV file that includes the tracklist to be updated:__", type=["csv"])

    if tracklist_to_update is not None:

        # Load DataFrame from uploaded file
        df_to_update = load_data(tracklist_to_update)

        # Initialize session state
        if 'df_to_update' not in st.session_state:
            st.session_state['df_to_update'] = pd.DataFrame()

        # Update session state
        st.session_state['df_to_update'] = df_to_update

        st.write(df_to_update)

    st.divider()

    extraction_option_update = st.radio(
        '__Choose an option to extract tracklist to add:__', ('Enter URL', 'Upload URL file'))

    if extraction_option_update == 'Enter URL':

        user_input = st.text_input(
            "Enter a list of URLs that contain desired tracks, playlists, albums, or artists (only top songs) :")
        urls = user_input.split(',')

        if user_input is not None:
            start_extracting_update = st.button('Start')

            if start_extracting_update:

                st.write('Extraction in progress...')
                info_dict, url_types = get_info(sp, urls)
                extracted_df = extract_data(sp, info_dict, url_types)
                updated_df = pd.concat([df_to_update, extracted_df])
                updated_df = updated_df.drop_duplicates(subset=["Track URI"])

                if 'updated_df' not in st.session_state:
                    st.session_state['updated_df'] = pd.DataFrame()

                st.session_state['updated_df'] = updated_df

            if 'updated_df' in st.session_state:

                if st.checkbox('Show updated dataframe'):

                    st.write("Updated Dataframe:")
                    st.dataframe(st.session_state['updated_df'])

                    save_updated_dataframe = st.button(
                        'Save Updated Dataframe')

                    if save_updated_dataframe:
                        save_data(
                            st.session_state['updated_df'], "updated_dataframe.csv")
                        st.write("Updated Dataframe has been saved.")
                        st.write("File saved as 'updated_dataframe.csv'.")

    elif extraction_option_update == 'Upload URL file':

        tracklist_to_add = st.file_uploader(
            "Upload a list of URLs that contain desired tracks, playlists, albums, or artists (only top songs):", type=["txt"])

        if tracklist_to_add is not None:
            start_extracting_update = st.button('Start')
            urls_file_content = tracklist_to_add.read().decode("utf-8")
            urls = urls_file_content.split(',')

            if start_extracting_update:

                st.write('Extraction in progress...')
                info_dict, url_types = get_info(sp, urls)
                extracted_df = extract_data(sp, info_dict, url_types)
                updated_df = pd.concat([df_to_update, extracted_df])
                updated_df = updated_df.drop_duplicates(subset=["Track URI"])

                if 'updated_df' not in st.session_state:
                    st.session_state['updated_df'] = pd.DataFrame()

                st.session_state['updated_df'] = updated_df

            if 'updated_df' in st.session_state:

                if st.checkbox('Show updated dataframe'):

                    st.write("Updated Dataframe:")
                    st.dataframe(st.session_state['updated_df'])

                    save_updated_dataframe = st.button(
                        'Save Updated Dataframe')

                    if save_updated_dataframe:
                        save_data(
                            st.session_state['updated_df'], "updated_dataframe.csv")
                        st.write("Updated Dataframe has been saved.")
                        st.write("File saved as 'updated_dataframe.csv'.")

st.divider()

################################################################
#Recommender
#################################################################

st.header('Recommender')
st.markdown(
    """
    __The Recommender module allows users 
    to generate a list of recommendations based on 
    a set of provided tracks. These recommendations 
    are selected from another tracklist, which needs 
    to be uploaded by the user.__
    """)

# Checkbox to hide/unhide the "Recommender" section
show_recommender = st.expander("__Show Recommender__")

with show_recommender:

    # File upload
    main_tracklist_file = st.file_uploader(
        "Upload your primary tracklist, which will be used to generate recommendations.:", type=["csv"])
    sample_tracklist_file = st.file_uploader(
        "Upload Your sample tracklist from which the recommended tracks will be extracted:", type=["csv"])

    if main_tracklist_file and sample_tracklist_file is not None:

        # Load DataFrame from uploaded file
        main_tracklist = load_data(main_tracklist_file)
        sample_tracklist = load_data(sample_tracklist_file)

        # Initialize session state
        if 'main_tracklist' not in st.session_state:
            st.session_state['main_tracklist'] = pd.DataFrame()
        if 'sample_tracklist' not in st.session_state:
            st.session_state['sample_tracklist'] = pd.DataFrame()

        # Update session state
        st.session_state['main_tracklist'] = main_tracklist
        st.session_state['sample_tracklist'] = sample_tracklist

        if st.button('Generate Recommendations'):
            recommendations = recommender(
                st.session_state['main_tracklist'], st.session_state['sample_tracklist'])

            st.dataframe(recommendations.head(20))

st.divider()

################################################################
#Data Analysis
#################################################################

st.header('Data Analysis')
st.markdown(
    """
    __Data Analysis module.__
    """)

# Checkbox to hide/unhide the "Data Analysis" section
show_data_analysis = st.expander("__Show Data Analysis__")

with show_data_analysis:

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a CSV file that contains a tracklist to analysis:", type=["csv"])

    if uploaded_file is not None:
        # Load DataFrame from uploaded file
        tracklist_to_analyze = load_data(uploaded_file)

        # Initialize session state
        if 'tracklist_to_analyze' not in st.session_state:
            st.session_state['tracklist_to_analyze'] = pd.DataFrame()

        # Update session state
        st.session_state['tracklist_to_analyze'] = tracklist_to_analyze

        # Checkbox to toggle visibility of tracklist to analyze
        show_analyze = st.checkbox("Show Tracklist to analyze")

        if show_analyze:
            st.dataframe(tracklist_to_analyze)

        # Checkbox to toggle visibility of analysis
        show_analysis = st.checkbox("Data Analysis")

        plt.style.use("dark_background")
        #st.write(plt.style.available)
        if show_analysis:
            tab1, tab2, tab3, tab4 = st.tabs(
                ['Informations', 'Correlation matrix', 'Barplots', 'Scatterplots'])
            with tab1:

                ### Information###
                col1, col2 = st.columns([2, 5])
                with col1:
                    st.table({'Number of tracks': len(tracklist_to_analyze.iloc[:, 0]),
                              'Number of artists': tracklist_to_analyze['Artist Name'].nunique(),
                              'Number of genres': tracklist_to_analyze['Artist Genres'].nunique()})

                with col2:
                    # Calculate the mean values for each feature
                    mean_danceability = np.mean(
                        tracklist_to_analyze['danceability'])
                    mean_energy = np.mean(tracklist_to_analyze['energy'])
                    mean_speechiness = np.mean(
                        tracklist_to_analyze['speechiness'])
                    mean_acousticness = np.mean(
                        tracklist_to_analyze['acousticness'])
                    mean_instrumentalness = np.mean(
                        tracklist_to_analyze['instrumentalness'])
                    mean_liveness = np.mean(tracklist_to_analyze['liveness'])
                    mean_valence = np.mean(tracklist_to_analyze['valence'])
                    # Normalize the loudness feature
                    loudness_min = np.min(tracklist_to_analyze['loudness'])
                    loudness_max = np.max(tracklist_to_analyze['loudness'])
                    normalized_loudness = (
                        tracklist_to_analyze['loudness'] - loudness_min) / (loudness_max - loudness_min)
                    mean_loudness = np.mean(normalized_loudness)
                    # Normalize the tempo feature
                    tempo_min = np.min(tracklist_to_analyze['tempo'])
                    tempo_max = np.max(tracklist_to_analyze['tempo'])
                    normalized_tempo = (
                        tracklist_to_analyze['tempo'] - tempo_min) / (tempo_max - tempo_min)
                    mean_tempo = np.mean(normalized_tempo)

                    # Define the features and their mean values
                    features = ['Danceability', 'Energy', 'Speechiness', 'Acousticness',
                                'Instrumentalness', 'Liveness', 'Valence', 'Loudness', 'Tempo']
                    mean_values = [mean_danceability, mean_energy, mean_speechiness, mean_acousticness,
                                   mean_instrumentalness, mean_liveness, mean_valence, mean_loudness, mean_tempo]

                    # Create a radar plot
                    angles = np.linspace(
                        0, 2 * np.pi, len(features), endpoint=False).tolist()
                    mean_values += mean_values[:1]
                    angles += angles[:1]

                    fig, ax = plt.subplots(
                        figsize=(6, 6), subplot_kw={'polar': True})
                    ax.plot(angles, mean_values, color='g', linewidth=3)
                    ax.fill(angles, mean_values, color='g', alpha=0.3)

                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(features)
                    ax.yaxis.grid(True)
                    ax.set_title('Mean Audio Features Radar Plot')

                    st.pyplot(fig)

            with tab2:
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Get a list of all available colormaps
                    all_cmaps = plt.colormaps()
                    default_cmap = 'Greens'
                    # Select the colormap using a selectbox
                    selected_cmap = st.selectbox(
                        "Select Colormap", all_cmaps, index=all_cmaps.index(default_cmap))

                # with col2:
                ### Correlation matrix###

                # Calculate the correlation matrix
                correlation_matrix = tracklist_to_analyze.corr()

                # Create a figure and axis for the correlation matrix plot
                fig, ax = plt.subplots()

                # Create a heatmap of the correlation matrix
                sns.heatmap(correlation_matrix,
                            annot=False,
                            cmap=selected_cmap,
                            ax=ax,
                            linewidths=0.1,
                            linecolor='white',
                            square=False,
                            cbar_kws={"shrink": 0.8})

                # Set the plot title
                ax.set_title("Correlation Matrix")

                # Display the plot using Streamlit
                st.pyplot(fig)
                ######
                cols_to_choose = ['Track Popularity', 'Artist Popularity',
                         'danceability', 'energy', 'key', 'loudness', 'mode',
                         'speechiness', 'acousticness', 'instrumentalness',
                         'liveness', 'valence', 'tempo']
            with tab3:
                # Barplots
                option = st.radio('Choose what kind of barplot would You like to have:',
                                  ('Countplot', 'Barplot'), horizontal=True)
                if option == 'Countplot':
                    col1, col2 = st.columns(2)
                    with col1:
                        choose = st.selectbox(
                            'Choose column for countplot', tracklist_to_analyze.columns)
                    with col2:
                        if choose:
                            direction = st.selectbox(
                                'Choose direction', ('Horizontal', 'Vertical'))
                    if direction == 'Horizontal':
                        # Create a figure and axis for the correlation matrix plot
                        fig, ax = plt.subplots()
                        ax.set_title("Countplot")
                        sns.countplot(data=tracklist_to_analyze,
                                      y=choose, ax=ax)
                        st.pyplot(fig)
                    elif direction == 'Vertical':
                        # Create a figure and axis for the correlation matrix plot
                        fig, ax = plt.subplots()
                        ax.set_title("Countplot")
                        sns.countplot(data=tracklist_to_analyze,
                                      x=choose, ax=ax)
                        st.pyplot(fig)
                if option == 'Barplot':
                    col1, col2 = st.columns(2)
                    with col1:
                        choose_x = st.selectbox(
                            'Choose x axis column for barplot', cols_to_choose)
                    with col2:
                        choose_y = st.selectbox(
                            'Choose y axis column for barplot', cols_to_choose)

                    # Create a figure and axis for the correlation matrix plot
                    fig, ax = plt.subplots()
                    ax.set_title("Barplot")
                    sns.barplot(data=tracklist_to_analyze,
                                x=choose_x, y=choose_y, ax=ax)
                    st.pyplot(fig)
            with tab4:
                col1, col2, col3 = st.columns(3)
                with col1:
                    choose_x = st.selectbox(
                        'Choose x axis column', cols_to_choose)
                with col2:
                    choose_y = st.selectbox(
                        'Choose y axis column', cols_to_choose)
                with col3:
                    choose_hue = st.selectbox(
                        'Choose hue', cols_to_choose)
                if choose_x and choose_y:
                    # Create a figure and axis for the correlation matrix plot
                    fig, ax = plt.subplots()
                    ax.set_title("Scatterplot")
                    sns.scatterplot(data=tracklist_to_analyze,
                                    x=choose_x, y=choose_y, hue = choose_hue)
                    st.pyplot(fig)

st.divider()

# ################################################################
# #Genre Predictor

# st.header('Genre Predictor')
# st.markdown(
#     """
#     __Genre Predictor module.__
#     """)

# # Checkbox to hide/unhide the "Data Analysis" section
# show_genre_predictor = st.expander("__Show Genre Predictor__")

# with show_genre_predictor:
#     st.write('Leggo')
