import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

from resourcescraper.resource_scraper.scraper import Scraper


class ApplePodcastScraper(Scraper):

    def __init__(self, queries:list[str], lang:str="en", country:str="ES", groups:dict={}):
        """
        Init function

        Args:
            queries (list[str]): List of string queries with the terms to search for in the Play and App Store.
            lang(str): The language to look for.
            country(str): Country where the apps must be available.
            groups(dict): Dictionary of groups to search for.
        """
        super().__init__(groups=groups)
        self.queries = queries
        self.lang = lang
        self.country = country
        # removed 'artistName' and genres
        self.keep = ['trackId', 'trackName', "trackViewUrl", 'releaseDate', 'trackTimeMillis', 'trackPrice']

    def search(self):
        """
        For each query, it gets all the matching podcasts in the App Store with the Itunes API.

        Returns:
            Pandas DataFrame with iOS podcasts.
        """
        for query in self.queries:
            query_parsed = '+'.join(query.split(' '))
            url = (f'https://itunes.apple.com/search?term={query_parsed}'
                   f'&media=podcast&callback=result&limit=200&country={self.country}')
            response = requests.get(url)
            result = json.loads(response.content.decode("utf-8").replace("\\n", '').replace("\n", '')[7:-2])
            # For each show
            for episode in result["results"]:
                url = (f"https://itunes.apple.com/lookup?id={episode['trackId']}"
                       f"&media=podcast&entity=podcastEpisode&limit=5")
                response = requests.get(url)
                res = json.loads(response.content.decode('utf-8').replace("\\n", '').replace("\n", ''))
                yield from res["results"]

    def parse(self, podcast):
        """
        Retrieves the privacy policy link and the description of the apps with web scraping.

        Args:
            podcast: Pandas DataFrame with the Podcast information.

        Returns:
            Pandas DataFrame with the privacy policy and description filled in.
        """
        response = requests.get(podcast["trackViewUrl"])
        soup = BeautifulSoup(response.content, "html.parser")
        descriptions = soup.find_all("p", attrs={"data-test-bidi": "", "dir": "false"})
        if len(descriptions) > 0:
            description = descriptions[0].getText()
        else:
            description = ""
        podcast["description"] = description
        return pd.DataFrame(podcast).T

    def clean(self):
        """
        Removes duplicates, cleans the String values of the apps and drops unwanted columns.

        Returns:
            Returns a clean DataFrame with podcasts and without duplicates.
        """
        names = set()
        result = []
        for podcast in self.search():
            if not podcast["trackId"] in names:
                aux = self.clean_podcast(podcast)
                names.add(podcast["trackId"])
                result.append(aux)
        return result

    def clean_podcast(self, podcast:dict) -> dict:
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
                result[key] = str(value).replace('\n', '').replace("\r", '')
        return result

    def __call__(self):
        podcasts = self.clean()
        df = pd.json_normalize(podcasts)
        df = df[self.keep]
        df = self.parse_resources(resources=df)
        print("# Apple podcasts: " + str(len(df)))
        return df
