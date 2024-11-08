import json
from datetime import datetime

import pandas as pd
import requests

from resourcescraper.resource_scraper.scraper import Scraper
from resourcescraper.source_scraper.apple_podcast_scraper import ApplePodcastScraper
from resourcescraper.source_scraper.spotify_podcast_scraper import SpotifyPodcastScraper


class PodcastScraper(Scraper):

    def __init__(self, queries:list[str], groups:dict=None, lang:str="en", country:str="ES"):
        """
        Init function

        Args:
            queries (list[str]): List of string queries with the terms to search for in Spotify and Apple Podcasts.
            lang (str): The language to look for.
            country (str): Country where the podcasts must be available.
            groups (dict): Dictionary of groups to search for.
        """
        super().__init__(groups)
        if groups is None:
            groups = {}
        self.queries = queries
        self.groups = groups
        self.lang = lang
        self.country = country
        self.podcasts = []
        self.map_spotify = {
            'name': 'title',
            'external_urls': 'trackViewUrl',
            'release_date': 'releaseDate',
            'duration_ms': 'trackTimeMillis'
        }
        self.map_apple = {
            'trackId': 'id',
            'trackName': 'title',
            'trackPrice': 'free'
        }
        self.spotify = None
        self.apple = None

    def search(self):
        """
        For each query, it gets all the matching apps in the App Store with the Itunes API.

        Returns:
            Pandas DataFrame with iOS apps.
        """
        podcasts = []
        for query in self.queries:
            query_parsed = '+'.join(query.split(' '))
            url = f'https://itunes.apple.com/search?term={query_parsed}&media=podcast&entity=podcastEpisode&callback' \
                  f'=result&limit=200&country={self.country}'
            response = requests.get(url)
            result = json.loads(response.content.decode("utf-8").replace("\\n", '').replace("\n", '')[7:-2])
            podcasts += result["results"]
        return podcasts

    def clean(self, podcasts):
        """
        Removes duplicates, cleans the String values of the apps and drops unwanted columns.

        Args:
            podcasts: Pandas DataFrame of iOS apps.

        Returns:
            Returns a clean DataFrame with podcasts and without duplicates.
        """
        names = set()
        result = []
        for podcast in podcasts:
            if not podcast["trackId"] in names:
                names.add(podcast["trackId"])
                result.append(podcast)
        return result

    @staticmethod
    def map_names(df, map: dict):
        """
        Changes the name of the columns in the given dataframe.

        Args:
            df: Input pandas DataFrame.
            map (dict): Dict with the current name as key and the new name as value.

        Returns:
            Pandas DataFrame object with the columns renamed as specified.

        Raises:
            KeyError when a key is not in df.columns.
        """
        # print(str(df))
        columns = list(df.columns)
        for old, new in map.items():
            idx = columns.index(old)
            columns[idx] = new
        df.columns = columns
        return df

    @staticmethod
    def datetime_to_date(value:str):
        """
        Removes the time from a string timestamp and changes the format.

        Args:
            value (str): String timestamp with format "%Y-%m-%dT%H:%M:%SZ".

        Returns:
            Returns a String date with format "%b %d, %Y".

        # >>> self.datetime_to_date('2022-01-01T01:01:01Z')
        """
        try:
            dt_object = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            date_str = dt_object.strftime("%Y-%m-%d")
            return date_str
        except:
            return "2001-01-01"

    @staticmethod
    def parse_spotify(df):
        """
        Parses android variables to match iOS in format and content.

        Args:
            df: Pandas DataFrame with the apps that have been found.

        Returns:
            A pandas DataFrame with the correct format and column names.
        """
        df['free'] = True
        # df['releaseDate'].map(lambda x: self.datetime_to_date(x))
        # df['contentRating'] = df['contentRating'].map(lambda x: self.map_content_rating(x))
        return df

    def parse_apple(self, df):
        """
            Parses android variables to match iOS in format and content.

        Args:
            df: Pandas DataFrame with the apps that have been found.

        Returns:
            A pandas DataFrame with the correct format and column names.
        """
        df['free'] = df['free'].map(lambda x: x == "0.0")
        # Example timestamp for Apple: 2020-11-23T22:41:00Z
        df['releaseDate'] = df['releaseDate'].map(lambda x: self.datetime_to_date(x))
        return df

    def __call__(self):
        """
        Main function that scraps Android and iOS apps and adds them in a single DataFrame.

        Returns:
            Pandas DataFrame with apps.
        """
        print('######### Input #########')
        print(str(self.queries))
        print('######### Search #########')
        # Spotify
        spotify = SpotifyPodcastScraper(self.queries, lang=self.lang, country=self.country)()
        spotify = self.map_names(spotify, self.map_spotify)
        spotify = self.parse_spotify(spotify)
        spotify['provider'] = 'Spotify'
        # Apple
        apple = ApplePodcastScraper(self.queries, lang=self.lang, country=self.country)()
        apple = self.map_names(apple, self.map_apple)
        apple['provider'] = 'Apple'
        apple = self.parse_apple(apple)
        # Merge
        df = pd.concat([spotify, apple], axis=0, ignore_index=True)
        df = df.fillna("None")
        df = self.find_keywords(df)
        df = df.drop_duplicates(subset=['id'], keep='first')
        return df
