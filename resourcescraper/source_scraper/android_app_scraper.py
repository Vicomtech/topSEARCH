import pandas as pd
import requests
from google_play_scraper import app as app_searcher

from resourcescraper.resource_scraper.scraper import Scraper


class AndroidAppScraper(Scraper):
    """Class to gather Android apps from Google Play"""

    def __init__(self, queries:list[str], lang:str="en", country:str="ES", free:bool=True, groups:dict={}):
        """
        Init function.

        Args:
            queries (list[str]): List of string queries with the terms to search for in the Play and App Store.
            lang (str): The language to look for.
            country (str): Country where the apps must be available.
            free (bool): Boolean indicating whether the apps are free or not.
            groups (dict): Dictionary of groups to search for.
        """
        super().__init__(groups)
        self.queries = queries
        self.lang = lang
        self.country = country
        self.free = 1 if free else 2
        self.drop_columns = ["video", "contentRatingDescription", "genreId", "videoImage", "descriptionHTML",
                             "currency", "sale", "saleText", "saleTime",
                             "originalPrice", "offersIAP", "icon", "headerImage", "screenshots", "videoImage",
                             "recentChangesHTML", "comments", "installs"]
        self.api_key = "42cfd21d3d4e866ff842f53442d28905dc196721555756ab9f79de6b04e1e9a0"

    def search(self):
        """
        For each query, it gets all the matching apps in the Play Store with the SerpAPI.

        Returns:
            Pandas DataFrame with Android apps.
        """
        apps = []
        for query in self.queries:
            q = '+'.join(query.split(' '))
            ##
            url = (f'https://serpapi.com/search?engine=google_play&q={q}&store=apps&api_key={self.api_key}&hl='
                   f'{self.lang}&gl={str(self.country).lower()}')
            # result = search(query, n_hits=30)
            first = True
            cont = 0
            next_page = None
            while cont < 30 and (next_page is not None or first):
                if first:
                    response = requests.get(url)
                    first = False
                else:
                    response = requests.get(next_page)
                if response.status_code == 200:
                    data = response.json()
                    try:
                        next_page = data["serpapi_pagination"]["next"] + "&api_key=" + self.api_key
                    except:
                        next_page = None
                    for app in data["organic_results"][0]["items"]:
                        metadata = self.search_app(app["product_id"])
                        apps.append(metadata)
                else:
                    print("Unable to call serpapi")
                    cont = 17
                cont += 1
        return apps

    def search_app(self, name: str) -> dict:
        """
        Given an app id, all the app metada is returned.

        Args:
            name (str): String id of the app in the Play Store.

        Returns:
            dict: A Dict with all the app metadata.
        """
        result = app_searcher(name, lang=self.lang, country=self.country)
        return result

    def clean(self, apps):
        """
        Removes duplicates, cleans the String values of the apps and drops unwanted columns.

        Args:
            apps: Pandas DataFrame of Android apps.

        Returns:
            Returns a clean DataFrame with Android apps and without duplicates.
        """
        names = set()
        result = []
        for app in apps:
            if not app["appId"] in names:
                aux = self.clean_app(app)
                names.add(app["appId"])
                result.append(aux)
        return result

    def clean_app(self, app:dict) -> dict:
        """
        Cleans the String values of the app and drops unwanted columns.

        Args:
            app (dict): Dict with column as key and value.

        Returns:
            dict: Returns a clean app dict.
        """
        result = {}
        for key, value in app.items():
            if key not in self.drop_columns:
                result[key] = str(value).replace('\n', '').replace("\r", '')
        return result

    def __call__(self):
        """
        Main function to load Android apps.

        Returns:
            Clean pandas DataFrame with Android apps.
        """
        apps = self.search()
        # print(apps)
        apps = self.clean(apps)
        df = pd.json_normalize(apps)
        df["os"] = "Android"
        # df.to_csv('../../resources/apps/android_apps.csv', index=False)
        print("# Android apps: " + str(len(df)))
        return df
