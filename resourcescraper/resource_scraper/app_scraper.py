from datetime import datetime

import pandas as pd

from resourcescraper.resource_scraper.scraper import Scraper
from resourcescraper.source_scraper.android_app_scraper import AndroidAppScraper
from resourcescraper.source_scraper.ios_app_scraper import IosAppScraper


class AppScraper(Scraper):
    """
        This class calls AndroidAppScraper and IosAppScraper to gather mobile apps and merges both of them with the
        correct format and columns.
    """

    def __init__(self, queries: list[str], groups:dict=None, lang:str="en", country:str="ES", free:bool=True):
        """
        Init function.

        Args:
            queries (list[str]): List of string queries with the terms to search for in the Play and App Store.
            groups (dict): Dict with custom groups as keys and list of lists of synonyms as value.
            lang (str): The language to look for.
            country (str): Country where the apps must be available.
            free (bool): Boolean indicating whether the apps are free or not.
        """
        super().__init__(groups)
        if groups is None:
            groups = {}
        self.queries = queries
        self.groups = groups
        self.lang = lang
        self.free = free
        self.country = country
        # Pre-defined column mapping functions to set the same name to columns with the same meaning
        self.android_map = {
            'genre': 'genres',
            'released': 'releaseDate',
            'updated': 'currentVersionReleaseDate',
            "minInstalls": "installs"
        }
        self.ios_map = {
            'trackName': 'title',
            'averageUserRating': 'score',
            'userRatingCount': 'ratings',
            'artistName': 'developer',
            'artistId': 'developerId',
            'sellerUrl': 'developerWebsite',
            'bundleId': 'appId',
            'trackViewUrl': 'url',
            'contentAdvisoryRating': 'contentRating'
        }
        self.rating_map = {
            'Everyone': '4+',
            'Teen': '12+'
        }
        self.keep = ["appId", "title", "description", "url", "genres", "developer", "developerWebsite", "score",
                     "ratings", "summary",
                     "currentVersionReleaseDate", "languageCodesISO2A", "os", "privacyPolicy", "privacyPolicyUrl",
                     "contentRating", "free", "price", "installs", "inAppProductPrice"]

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
        columns = list(df.columns)
        for old, new in map.items():
            idx = columns.index(old)
            columns[idx] = new
        df.columns = columns
        return df

    @staticmethod
    def datetime_to_date(value: str) -> str:
        """
        Removes the time from a string timestamp and changes the format.

        Args:
            value (str): String timestamp with format "%Y-%m-%dT%H:%M:%SZ".

        Returns:
            str: Returns a String date with format "%b %d, %Y".

        self.datetime_to_date('2022-01-01T01:01:01Z').
        """
        dt_object = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        date_str = dt_object.strftime("%b %d, %Y")
        return date_str

    @staticmethod
    def timestamp_to_date(value: str) -> str:
        """
        Converts a unix timestamp to String date.

        Args:
            value (str): String unix timestamp.

        Returns:
            str: Returns a String date with format "%b %d, %Y".

        self.datetime_to_date('2022-01-01T01:01:01Z').
        """
        dt_object = datetime.fromtimestamp(int(value))
        date_str = dt_object.strftime("%b %d, %Y")
        return date_str

    def map_content_rating(self, x:str) -> str:
        """
        Maps the values given for content rating to match the iOS format (4+, 12+ and 17+).

        Args:
            x (str): A string rating.

        Returns:
            str: Returns a parsed rating.
        """
        for k, v in self.rating_map.items():
            if str(x).__contains__(k):
                return v
        return x

    def parse_android(self, df):
        """
        Parses android variables to match iOS in format and content.

        Args:
            df: Pandas DataFrame with the apps that have been found.

        Returns:
            A pandas DataFrame with the correct format and column names.
        """
        df['currentVersionReleaseDate'] = df['currentVersionReleaseDate'].map(lambda x: self.timestamp_to_date(x))
        # TODO: check this depending the language
        df['languageCodesISO2A'] = "[\'EN\']"
        df['score'] = df['score'].replace({'None': None}).astype(float)
        df['genres'] = df['genres'].map(lambda x: [x])
        df['privacyPolicyUrl'] = df['privacyPolicy']
        df['privacyPolicy'] = df['privacyPolicy'].map(lambda x: x != "None")
        df['free'] = df['free'].map(lambda x: x == 'True')
        df['contentRating'] = df['contentRating'].map(lambda x: self.map_content_rating(x))
        df['ratings'] = df['ratings'].map(lambda x: int(x) if x != "None" else 0)
        return df

    def parse_ios(self, df):
        """
        Parses iOS variables to match iOS in format and content.

        Args:
            df: Pandas DataFrame with the apps that have been found.
        Returns:
            A pandas DataFrame with the correct format and column names.
        """
        df['currentVersionReleaseDate'] = df['currentVersionReleaseDate'].map(lambda x: self.datetime_to_date(x))
        df['releaseDate'] = df['releaseDate'].map(lambda x: self.datetime_to_date(x))
        df['free'] = df['price'].map(lambda x: x == "0.0")
        # All iOS apps have a privacy policy
        df['privacyPolicy'] = True
        df['installs'] = "0.0"
        df['ratings'] = df['ratings'].map(lambda x: int(x) if x != "None" else 0)
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
        # Android
        android = AndroidAppScraper(
            self.queries, lang=self.lang, country=self.country, free=self.free, groups=self.groups)()
        android = self.map_names(android, self.android_map)
        android = self.parse_android(android)
        # iOS
        ios = IosAppScraper(self.queries, lang=self.lang, country=self.country, groups=self.groups)()
        ios = self.map_names(ios, self.ios_map)
        ios = self.parse_ios(ios)
        # Merge
        df = pd.concat([android, ios], axis=0)
        df = df.fillna("None")
        df = df[self.keep].reset_index(drop=True)
        df = self.find_keywords(df)
        df['privacyPolicy'] = df['privacyPolicy'].astype(bool)
        df = df.drop_duplicates(subset=['appId'], keep='first')
        return df
