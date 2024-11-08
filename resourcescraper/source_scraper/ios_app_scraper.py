import json

import bs4
import pandas as pd
import requests

from resourcescraper.resource_scraper.scraper import Scraper


class IosAppScraper(Scraper):
    """Class to gather iOS apps from App Store"""

    def __init__(self, queries:list[str], lang:str="en", country:str="ES", groups:dict=None):
        """
        Init function

        Args:
            queries (list[str]): List of string queries with the terms to search for in the Play and App Store.
            lang (str): The language to look for.
            country (str): Country where the apps must be available.
            groups (dict): Dictionary of groups where the apps are available.
        """
        super().__init__(groups)
        self.queries = queries
        self.lang = lang
        self.country = country
        self.drop_columns = ['sellerName', 'minimumOsVersion', 'trackContentRating', 'primaryGenreId',
                             'primaryGenreName', 'genreIds', 'isVppDeviceBasedLicensingEnabled', 'trackId',
                             'wrapperType', 'kind', 'artistViewUrl', 'isGameCenterEnabled', 'features',
                             'ipadScreenshotUrls', 'appletvScreenshotUrls', 'supportedDevices', 'screenshotUrls',
                             'artworkUrl60', 'artworkUrl512', 'artworkUrl510', 'artworkUrl100', 'currency',
                             'trackPrice', 'formattedPrice']

    def search(self):
        """
        For each query, it gets all the matching apps in the App Store with the Itunes API.

        Returns:
            Pandas DataFrame with iOS apps.
        """
        apps = []
        for query in self.queries:
            query_parsed = '+'.join(query.split(' '))
            url = (f'https://itunes.apple.com/search?term={query_parsed}'
                   f'&entity=software&callback=result&limit=200&country={self.country}')
            response = requests.get(url)
            result = json.loads(response.content.decode("utf-8").replace("\\n", '').replace("\n", '')[7:-2])
            apps += result["results"]
        return apps

    def get_additional_metadata(self, apps):
        """
        Retrieves the privacy policy link and the description of the apps with web scraping.

        Args:
            apps: Pandas DataFrame with Apps.

        Returns:
            Pandas DataFrame with the privacy policy and description filled in.
        """
        res = {
            'privacyPolicy': [],
            'description': []
        }
        for i, app in apps.iterrows():
            try:
                response = requests.get(app["trackViewUrl"])
                soup = bs4.BeautifulSoup(response.content, "html.parser")
                res["privacyPolicy"].append(soup.find_all("a", class_="link icon icon-after icon-external")[-1]["href"])
                description = soup.find_all("div", class_="section__description")[0].getText()
                description = description.replace("\n", " ").replace("Description", "")
                if str(self.lang).lower() != "en":
                    res["description"].append(description)
            except:
                res["privacyPolicy"].append(None)
                res["description"].append(None)
        apps["privacyPolicyUrl"] = res["privacyPolicy"]
        if str(self.lang).lower() != "en":
            apps["description"] = res["description"]
        return apps

    def clean(self, apps):
        """
        Removes duplicates, cleans the String values of the apps and drops unwanted columns.

        Args:
            apps: Pandas DataFrame of iOS apps.

        Returns:
            Returns a clean DataFrame with Android apps and without duplicates.
        """
        names = set()
        result = []
        for app in apps:
            if not app["bundleId"] in names:
                aux = self.clean_app(app)
                names.add(app["bundleId"])
                result.append(aux)
        return result

    def clean_app(self, app: dict) -> dict:
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
        Main function to load iOS apps.

        Returns:
            Clean pandas DataFrame with iOS apps.
        """
        apps = self.search()
        apps = self.clean(apps)
        df = pd.json_normalize(apps)
        # df = self.get_additional_metadata(df)
        df["os"] = "iOS"
        # df.to_csv('../../resources/apps/ios_apps.csv', index=False)
        print("# iOS apps: " + str(len(df)))
        return df
