from user_env import (LASTFM_API_KEY, LASTFM_API_SECRET,
                      SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, 
                      SPOTIFY_USERNAME)

import spotipy
import pylast
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler


# Replace these with your actual API credentials
SPOTIFY_REDIRECT_URI = "https://NAME_OF_YOUR_FUNCTION_APP.azurewebsites.net"
SCOPE = 'playlist-modify-public playlist-read-private playlist-modify-private'
CACHE_FILENAME = "spotify_cache.cache"


def get_playlist_id(sp, playlist_name):
    playlists = sp.current_user_playlists()
    return next(
        (
            playlist['id']
            for playlist in playlists['items']
            if playlist['name'] == playlist_name
        ),
        None,
    )


def get_playlist_tracks(sp, playlist_id):
    playlist_tracks = []

    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for track in tracks:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        playlist_tracks.append((track_name, artist_name))

    return playlist_tracks


def create_playlist(sp, playlist_name, public=False):
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name, public=public)
    return playlist['id']


def add_track_to_spotify_playlist(sp, track_name, artist_name, playlist_id):
    query = f"{track_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    if results and results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        sp.playlist_add_items(playlist_id, items=[track_id])
        print("Track added to the playlist successfully.")
  
        
def remove_track_from_spotify_playlist(sp, track_name, artist_name, playlist_id):
    query = f"{track_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    if results and results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        sp.playlist_remove_all_occurrences_of_items(playlist_id, items=[track_id])
        print("Track removed from the playlist successfully.")        


def get_similar_tracks_lastfm(track_name, artist_name):
    network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)
    
    # Get the track object
    track = network.get_track(artist_name, track_name)   
    # Get similar tracks for the given track
    similar_tracks = track.get_similar()

    return [(similar_track.item.get_name(), similar_track.item.get_artist().get_name()) for similar_track in similar_tracks]


def get_similar_artists(artist_name):
    network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)
    
    # Get the artist object
    artist = network.get_artist(artist_name)  
    # Get similar artists for the given artist
    similar_artists = artist.get_similar()
    
    return [similar_artist.item.get_name() for similar_artist in similar_artists]


def get_artist_top_tracks(artist_name, limit=10):
    network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

    # Get the artist object
    artist = network.get_artist(artist_name)
    # Get the artist's top tracks
    top_tracks = artist.get_top_tracks(limit=limit)

    return [(track.item.get_name(), artist_name) for track in top_tracks]


# Function to create CacheFileHandler instance with the desired cache file path
def create_cache_handler(username):
    return CacheFileHandler(username=username)


def spotify_connect():
    # Create CacheFileHandler instance with the external storage directory path
    cache_handler = create_cache_handler(SPOTIFY_USERNAME)

    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_handler=cache_handler,
    ) 


def lasftm_similars(token):
    # Authenticate with Spotify    
    sp = spotipy.Spotify(auth=token)              
    
    # get similar tracks
    _que_playlist_id = get_playlist_id(sp, "Query similar tracks from LastFM")
    playlist_tracks = get_playlist_tracks(sp, _que_playlist_id)
    
    for song, artist in playlist_tracks:
        playlist_name = f"Similar tracks to {artist}--{song}"
        _playlist_id = get_playlist_id(sp, playlist_name)
        if _playlist_id is None:
            similar_tracks = get_similar_tracks_lastfm(song, artist)
            if len(similar_tracks):                    
                _playlist_id = create_playlist(sp, playlist_name)
                for track_name, artist_name in similar_tracks:
                    add_track_to_spotify_playlist(sp, track_name, artist_name, _playlist_id)
                
                remove_track_from_spotify_playlist(sp, song, artist, _que_playlist_id)
                print("Similar tracks playlist was created successfully.")                   
                
    # get similar artists
    _playlist_id = get_playlist_id(sp, "Query similar artists from LastFM")
    playlist_tracks = get_playlist_tracks(sp, _playlist_id)
    
    artist_tracks = []
    for song, artist in playlist_tracks:
        playlist_name = f"Similar artists to {artist}"
        _playlist_id = get_playlist_id(sp, playlist_name)
        if _playlist_id is None:            
            similar_artists = get_similar_artists(artist)
            if len(similar_artists):
                for sim_artist in similar_artists:
                    artist_tracks += get_artist_top_tracks(sim_artist)
            
            if len(artist_tracks):                 
                _playlist_id = create_playlist(sp, playlist_name)
                for track_name, artist_name in artist_tracks:
                    add_track_to_spotify_playlist(sp, track_name, artist_name, _playlist_id)   
            
            remove_track_from_spotify_playlist(sp, song, artist, _que_playlist_id)    
            print("Similar artists playlist was created successfully.")
        
