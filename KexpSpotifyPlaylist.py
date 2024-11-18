import requests
import spotipy
import dotenv
import spotipy.util as util
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SPOTIFY_REFRESH_TOKEN = get_env("SPOTIFY_REFRESH_TOKEN")
SPOTIFY_CLIENT_ID = get_env("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_env("SPOTIFY_CLIENT_SECRET")


OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
""" Creates a Spotify playlist of the latest songs played on Seattle's KEXP 90.3 FM radio station. """


class KexpSpotifyPlaylist:
    def __init__(self):

        """ 1. Gets a JSON object of Kexp 90.3 FM's stream history using the Requests library and the Kexp API endpoint
            2. Iterates through the JSON object, retrieves each song played on Kexp 90.3 FM and appends them to a list
            4. Accesses the user's Spotify client.
            5. Iterates through the Kexp song list, searches Spotify for each song, appends each song URI to a list
            6. Creates a Spotify playlist and returns the Spotify playlist's URI.
            7. Adds the list of Spotify song URIs to the Spotify playlist.

        """

        """ Kexp stream API endpoint """
        self.kexp_endpoint = "https://legacy-api.kexp.org/play/"

        """ The title of the Spotify playlist that the Kexp songs will be appended to."""
        self.playlist_title = "KEXP - {Date}".format(Date=datetime.today())

        """ Scope for Spotify client token """
        # More info on scopes here: https://developer.spotify.com/documentation/general/guides/scopes/
        self.scope = "playlist-modify-public"

        self.kexp_json = self.get_kexp_json_from_api()
        self.kexp_list = self.get_kexp_list_from_json()
        self.sp = self.get_spotify_client()
        self.spotify_uris = self.get_spotify_uris()
        self.spotify_playlist = self.create_spotify_playlist()
        self.spotify_playlist_id = self.get_spotify_playlist_id()
        self.add_uris_to_playlist()

    def get_kexp_json_from_api(self):

        """ Gets a JSON object of Kexp 90.3 FM's stream history using the Requests library and the Kexp API endpoint."""

        return requests.get(self.kexp_endpoint).json()

    def get_kexp_list_from_json(self):

        """ Creates a list to append songs
            Iterates through the Kexp stream history json object
            Filters out advertisements/commercial breaks by getting "Media Plays" (songs) only
            Gets the artist and song name for each Media Play item in the json object and formats it as "artist - song"
            Removes a subset of characters that are unfriendly to Spotify's search client
            Appends each artist - song string to the list

        """

        self.kexp_list = []

        for item in self.kexp_json["results"]:

            if item["playtype"]["name"] == "Media play":

                current_artist = item["artist"]["name"]
                current_song = item["track"]["name"]

                track = "{artist} {song}".format(artist=current_artist, song=current_song)

                # Todo: Find a more elegant/comprehensive way to replace search-breaking characters
                track = track.replace("feat", "",).replace("&", "")

                self.kexp_list.append(track)

        return self.kexp_list

    def get_spotify_client(self):

        """ Creates a token from our Spotify client info(from our secrets.py file).
        This token is used to create a spotify object.
        A Spotify object is used to interact with our Spotify Client to search for songs, make playlists, etc.

        """

        token = util.prompt_for_user_token(spotify_username,
                                           self.scope,
                                           spotify_client_id,
                                           spotify_secret,
                                           redirect_url)

        return spotipy.Spotify(auth=token)

    def get_spotify_uris(self):

        """ Creates a list to append Spotify song URIs
            Iterates through the list of Kexp songs
            Searches Spotify for each Kexp song
            Gets a Spotify song URI for each search result.
            Appends each Spotify song URI to the list

        """

        uri_list = []

        for song in self.kexp_list:

            try:

                result = self.sp.search(song)

                uri = result["tracks"]["items"][0]["uri"]

                uri_list.append(uri)

            except IndexError:

                # When no Spotify result is returned, prints each song title
                print("No results for: {song}".format(song=song))

                pass

        return uri_list

    def create_spotify_playlist(self):

        """ Creates a Spotify playlist titled according to playlist_title set in our __init__ method."""

        # Todo: datetime is formatted yyyy-mm-dd hh:mm:ms..... Not very readable in spotify. Need to work out format.

        return self.sp.user_playlist_create(spotify_username, self.playlist_title)

    def get_spotify_playlist_id(self):

        """ Returns the Spotify playlist ID for the playlist that we just created."""

        return self.spotify_playlist["uri"]

    def add_uris_to_playlist(self):

        """ Adds the list of Spotify song URIs to the Spotify Playlist ID that we created."""

        self.sp.user_playlist_add_tracks(user=spotify_username,
                                         playlist_id=self.spotify_playlist_id,
                                         tracks=self.spotify_uris)


if __name__ == '__main__':
    ks = KexpSpotifyPlaylist()
