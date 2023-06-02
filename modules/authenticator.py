####################################################
#-----------Spotify API user credentials-----------#
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
####################################################

#----------------Client keys------------------#
client_id = ''
secret = ''
#---------------------------------------------#

#--------------------------------Authenticator-----------------------------------#
def authenticator(client_id = client_id, secret = secret):
    client_credentials_manager = SpotifyClientCredentials(client_id = client_id, 
                                                          client_secret = secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    return sp
#--------------------------------------------------------------------------------#
