
# Imports
from splinter import Browser
import pandas as pd
import time
from selenium import webdriver
import json
import pprint
def init_browser():
    """ Initialize test browser session for scraping """
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    #executable_path = {"executable_path": "chromedriver"}
    return Browser('chrome', **executable_path, headless=False)
    #return Browser("chrome", **executable_path, headless=False)

def test():
    """ Returns static cities array, for testing purposes """
    # Import test dataset from test_city.py
    from data.test_city import cities
    return cities

def scrape_spotify_info(limiting, limit):
    """ Obtain Spotify ID information for each track in city-specific playlists
        (for selected cities from Cities.py)

        Args:
            limiting -- If we are limiting the for loop (boolean)
            limit -- The limit threshold
    """
    # Import actual dataset from Cities.py
    from data.Cities import cities

    # Initialize browser that we can re-use
    browser = init_browser()

    # Lopo through all cities in the array
    i = 0
    for city in cities:
        # Exit out of for loop at specified limit, if we are limiting city iterations
        if limiting == True and i == limit:
            break
        # Increment counter
        i += 1

        # Take the first URL in our list (as a test)
        city_url = city["spotify_url"]
        browser.visit(city_url)

        # Wait for page to load
        time.sleep(5)

        # Import Beautiful Soup to parse through HTML of page
        from bs4 import BeautifulSoup as bs

        # Pass the HTML output from the splinter session
        html = browser.html
        soup = bs(html, 'html.parser')

        # Get iFRAME URL for the actual playlist, and visit it
        iframe = soup.find("iframe")["src"]
        browser.visit(iframe)

        # Wait for page to load
        time.sleep(10)

        # Pass the HTML output from the splinter session
        html = browser.html
        soup = bs(html, 'html.parser')
        playlist = json.loads(soup.find('script', id = 'resource').text)
        #pprint.pprint(playlist)

        #print (playlist['tracks']['items'][0]['track']['album']['artists'][0]['name'])
        #print (playlist['tracks']['items'][0]['track']['id'])
        #print (playlist['tracks']['items'][0]['track']['name'])

        songs = []

        track_id = playlist['tracks']['items'][0]['track']['id']

        # Get the Artist and song name
        artist_name = playlist['tracks']['items'][0]['track']['album']['artists'][0]['name']
        song_name = playlist['tracks']['items'][0]['track']['name']
        songs.append({
                "artist": artist_name,
                "name": song_name,
                "track_id": track_id
        })

    # Determine top arists
    dfArtists = pd.DataFrame(songs)

    # Get the unique list of artists
    dfUniqueArtists = pd.DataFrame(dfArtists["artist"].value_counts()).reset_index()

    # Merge above dataframes so we can keep track of the top artists' track IDs
    dfMergedArtists = pd.merge(dfArtists, dfUniqueArtists, left_on = 'artist', right_on = 'index')

    # Rename columns
    dfMergedArtists = dfMergedArtists.rename(columns={"artist_x": "Artist","name": "Track Name"})
    dfMergedArtists = dfMergedArtists[["Artist", "Track Name", "track_id"]]
    top_artist_listing = dfUniqueArtists["index"]

    # Set list of top artists
    top_artists = list(top_artist_listing)

    # Loop through all top artists, and assign their first track_id, which we'll need for Spotify API lookup
    #
    #    Artist object in the format:
    #    [
    #        { 'Bobby Johnson': [ 'lakjdsfasf', '23kjlksjsdf', '2kjas90ksads'] },
    #        { 'Jane Doe': ['0kkjdkjsfasf', '9jkkjlksjsdf', '83skas90ksads'] },
    #        ...
    #    ]
    artists = []
    for artist in top_artists:
        dfTrack = dfMergedArtists.loc[dfMergedArtists["Artist"] == artist]
        artist_tracks = list(dfTrack["track_id"])

        # Build artists object for this city
        artist_info = { "artist": artist, "tracks": artist_tracks }
        artists.append(artist_info)

    # Update our object array value with top artists for this city
    city["top_artists"] = artists

    # Update object array with all track_ids for this city
    city["track_ids"] = list(dfArtists["track_id"])

# Return the array of objects we just built
    return cities
