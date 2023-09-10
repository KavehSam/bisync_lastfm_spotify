from user_env import *

import spotipy
import pylast
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler

SCOPE = 'user-library-modify user-library-read playlist-modify-public playlist-read-private playlist-modify-private'
CACHE_FILENAME = "spotify_cache.cache"
# Replace it with your actual callback end-point
SPOTIFY_REDIRECT_URI = "https://NAME_OF_YOUR_FUNCTION_APP.azurewebsites.net"


def get_spotify_liked_songs(sp, limit):
    print("Fetch Spotify liked songs...")
    liked_songs = []
    i = 0
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            liked_songs.append((track['name'], track['artists'][0]['name']))
        i += 1
        if limit is not None and i > limit:
            break
        results = sp.next(results)
    return liked_songs


def get_lastfm_loved_tracks(limit):
    lastfm_network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)    
    user = lastfm_network.get_user(LASTFM_USERNAME)
    print("Fetch Lasftm loved songs...")
    loved_songs = []
    if limit is not None and limit < 20:
        limit = 20
    pay_load = user.get_loved_tracks(limit=limit)
      
    for loved_track in pay_load:
        loved_songs.append((loved_track.track.title, loved_track.track.artist.name))
         
    return loved_songs


def add_to_spotify_liked_songs(sp, track_name, artist_name):
    query = f"{track_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    if results and results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        sp.current_user_saved_tracks_add(tracks=[track_id])
        # print(f"Added {track_name} by {artist_name} to Spotify liked songs...")
        return True
    else:
        # print(f"Failed to find {track_name} by {artist_name} on Spotify.")
        return False


def add_to_lastfm_loved_tracks(track_name, artist_name):
    lastfm_network = pylast.LastFMNetwork(
        api_key=LASTFM_API_KEY,
        api_secret=LASTFM_API_SECRET,
        username=LASTFM_USERNAME,
        password_hash=LASTFM_PASS,
    )   
    try:
        track = lastfm_network.get_track(artist_name, track_name)
        track.love()
        # print(f"Added {track_name} by {artist_name} to Last.fm loved tracks...")
        return True
    except Exception as e:
        # print(f"Failed to add {track_name} by {artist_name} to Last.fm loved tracks. Error: {e}")
        return False


def create_cache_handler(username):
    """ Function to create CacheFileHandler instance with the desired cache file path


    Returns:
        obj: Spotify CacheFileHandler instance
    """    
    return CacheFileHandler(username=username)


def spotify_connect():
    """ Create CacheFileHandler instance with the external storage directory path

    Returns:
        obj: Spotify SpotifyOAuth instance
    """    
    cache_handler = create_cache_handler(SPOTIFY_USERNAME)

    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_handler=cache_handler,
    ) 


def bi_directional_sync(limit):
    """ Bi-directional Synchronization between Spotify liked songs and Lastfm loved tracks

    Args:
        limit (int): max number of songs to query 

    Returns:
        str: Spotify user token
    """ 
       
    printout = []
    # Authenticate with Spotify
    token = spotipy.util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=SCOPE,
                                    client_id=SPOTIFY_CLIENT_ID,
                                    client_secret=SPOTIFY_CLIENT_SECRET,
                                    redirect_uri=SPOTIFY_REDIRECT_URI)
    if token:        
        sp = spotipy.Spotify(auth=token)        
        liked_songs =  get_spotify_liked_songs(sp, limit)
        lastfm_loved_tracks =  get_lastfm_loved_tracks(limit)
      
        # Synchronize Spotify liked songs with Last.fm loved tracks
        num_liked_songs = 0
        for song, artist in liked_songs:
            if (song, artist) not in lastfm_loved_tracks and add_to_lastfm_loved_tracks(song, artist):
                num_liked_songs += 1
        printout.append(f"Total of {num_liked_songs} songs were added to Lasfm Love tracks.")        
        print(printout[-1])

        # Synchronize Last.fm loved tracks with Spotify liked songs 
        num_liked_songs = 0            
        for song, artist in lastfm_loved_tracks:
            if (song, artist) not in liked_songs and add_to_spotify_liked_songs(sp, song, artist):
                num_liked_songs += 1
                
        printout.append(f"Total of {num_liked_songs} songs were added to Spotify liked songs.")                    
        print(printout[-1])
        
        printout.append("Synchronization completed.")
    else:
        printout.append("Unable to get Spotify access token.")
    
    print(printout[-1])
    return token
        
        
