# bisync_lastfm_spotify
Bi-directional synchronization between Lastfm loved tracks and Spotify like songs


# Prerequisites
1. Spotify developer account
2. Lastfm account
3. Spotify account
4. Microsoft Azure acount (optional)

## Credentials
- Enter your credentials in user_env.py, for spotify you need to first create a new app in order to get SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.
- SPOTIFY_REDIRECT_URI must match the callback url of your spotify app. If you are going to deploy it as Azure function then set it according to the name of the azure function app.
- Create an Azure function app (optional).


# Query from Lastfm and on-demand spotify play list generation
In your Spotify profile, create two playlist with the names "Query similar tracks from LastFM" and "Query similar artists from LastFM", make sure that their visibility is public. 
## get lastfm similar tracks for a song in Spotify 
Just add any song to the "Query similar tracks from LastFM" play list. Similar tracks are fetched from LastFm and a Spotify play list is added with the name "Similar tracks to {artist_name}--{song_name}" accordingly. 
If the query is successful the track is omitted from the "Query similar tracks from LastFM", otherwise it will be kept. 
## get lastfm similar artists for a song in Spotify 
Just add any song to the "Query similar artists from LastFM" play list. Similar artists are fetched from LastFm and a Spotify play list is added with the name "Similar artists to {artist_name}" accordingly. 
If the query is successful the track is omitted from the "Query similar artists from LastFM", otherwise it will be kept. 
