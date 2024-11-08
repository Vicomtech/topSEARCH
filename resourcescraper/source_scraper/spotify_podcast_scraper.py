import time

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from resourcescraper.resource_scraper.scraper import Scraper


class SpotifyPodcastScraper(Scraper):

    def __init__(self, queries:list[str], lang:str="en", country:str="ES", groups:dict=None):
        """
        Init function

        Args:
            queries (list[str]): List of string queries with the terms to search for in the Play and App Store.
            lang (str): The language to look for.
            country (str): Country where the apps must be available.
            groups (dict): Dictionary of groups to search for.
        """
        super().__init__(groups=groups)
        self.queries = queries
        self.lang = lang
        self.country = country
        self.keep = ['id', 'name', 'release_date', 'description', 'duration_ms', 'external_urls', 'languages']

    def search(self):
        """
        For each query, it gets all the matching apps in the App Store with the Itunes API.

        Returns:
            Pandas DataFrame with iOS apps.
        """
        spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        podcasts = []
        for query in self.queries:
            res = spotify.search(q=query, type='episode', limit=50, market=str(self.country).upper())
            podcasts += res["episodes"]["items"]
            while res["episodes"]["next"]:
                try:
                    res = spotify.next(res["episodes"])
                    podcasts += res["episodes"]["items"]
                except:
                    time.sleep(1)
            time.sleep(3)
        # s = [x["id"] for x in podcasts]
        # podcasts = spotify.episodes(s, market=str(self.country).upper())["episodes"]
        return podcasts

    def clean(self, podcasts):
        """
        Removes duplicates, cleans the String values of the apps and drops unwanted columns.

        Args:
            podcasts: Pandas DataFrame of iOS apps.

        Retruns:
            Returns a clean DataFrame with podcasts and without duplicates.
        """
        names = set()
        result = []
        for podcast in podcasts:
            if not podcast["id"] in names:
                aux = self.clean_podcast(podcast)
                names.add(podcast["id"])
                result.append(aux)
        return result

    def clean_podcast(self, podcast: dict) -> dict:
        """
        Cleans the String values of the app and drops unwanted columns.

        Args:
            podcast (dict): Dict with column as key and value.

        Returns:
            dict: Returns a clean app dict.
        """
        result = {}
        for key, value in podcast.items():
            if key in self.keep:
                if key == 'external_urls':
                    result[key] = value['spotify']
                else:
                    result[key] = value
        return result

    def __call__(self):
        """
        Executes the podcast retrieval and processing workflow.

        Returns:
            A pandas DataFrame containing the processed podcast data.
        """
        podcasts = self.search()
        podcasts = self.clean(podcasts)
        df = pd.json_normalize(podcasts)
        df = df[self.keep]
        print("# Spotify podcasts: " + str(len(df)))
        return df
