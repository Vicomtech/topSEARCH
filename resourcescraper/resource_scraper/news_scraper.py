# import multiprocessing
from datetime import datetime

import pandas as pd
import requests
from gnews import GNews
from newspaper import Article, Config

from resourcescraper.resource_scraper.scraper import Scraper
from resourcescraper.utils.timeout import timeout


class NewsScraper(Scraper):
    """Class to gather news from GoogleNews"""

    def __init__(self, queries: list[str], language: str, country: str,
                 news_name:str='Google_News',
                 user_agent:str='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/50.0.2661.102 Safari/537.36',
                 groups:dict=None):
        """
        Init function.

        Args:
            queries (list[str]): List of string queries with the terms to search for in GoogleNews.
            groups (dict): Dictionary of string keywords to look for in news.
            language (str): The language to look for.
            country (str): The country to look in.
            news_name (str): The site to search news.
            user_agent (str): The user agent to look for in Google News site.
        """
        super().__init__(groups)
        self.queries = queries
        self.groups = groups
        self.lang = language
        self.country = country
        self.news_name = news_name
        self.user_agent = user_agent

    def search(self):
        """
        For each query, it gets all the matching news in GoogleNews.

        Returns:
            Pandas DataFrame with news.
        """
        search_query = self.queries[0]
        date = datetime.today()
        start_date = datetime.strptime(f'{date.day}/{date.month}/{date.year-3}', '%d/%m/%Y')
        end_date = datetime.strptime(f'{date.day}/{date.month}/{date.year}', '%d/%m/%Y')
        googlenews = GNews(language=self.lang, country=self.country, start_date=start_date, end_date=end_date)
        results = googlenews.get_news(search_query)
        df_news = pd.DataFrame(results)
        df_news = df_news.rename(columns={'published date': 'publishedAt', 'url': 'URL'})
        for x in range(df_news.shape[0]):
            df_news.iloc[x]['publisher'] = df_news.iloc[x]['publisher']['title']

        return df_news

    @timeout(10, "Timeout exceeded")
    def parse(self, resource: dict):
        """
        Parse content to extract metadata of each news.

        Args:
            resource (dict): Dictionary of news.

        Returns:
            list: DataFrame with news.
        """
        # print('resource: ', resource)
        config = Config()
        config.browser_user_agent = self.user_agent
        # try:
            # if self.news_name == 'Google_News':
                # Go through the redirect url
                # url = resource['URL']
                # article = Article(url, config=config)
                # article.download()
                # article.parse()
                # article.nlp()
                # # Extract metadata
                # res = self.extract_from_response(article, resource)
                # return pd.DataFrame(pd.Series(res, dtype=object)).T
        # except Exception as e:
        #     return None
        return resource

    def extract_from_response(self, response, resource: dict):
        """
        Extracts relevant information from a response object and combines it with additional data from the given
        resource dictionary.

        Args:
            response: A response object containing various attributes like publish date, meta description, text,
            authors, etc.
            resource (dict): A dictionary containing additional news details, such as the title and media source.

        Returns:
             dict[str, int]: A dictionary containing extracted data including: 'publishedAt', 'description', 'title',
             'URL', 'language', 'mediaTitle', 'authors', 'summary', 'content', 'textLength' and 'keywords'.
        """
        res = {'publishedAt': response.publish_date.strftime("%Y-%m-%d"),
               'description': response.meta_description,
               'title': resource['title'],
               'URL': response.url,
               'language': self.lang,
               'mediaTitle': resource['media'],
               'authors': response.authors,
               'summary': response.summary,
               'content': response.text}
        words = len(response.text.split())
        res['textLength'] = words
        res['keywords'] = response.keywords
        return res

    def clean(self, results: list):
        """
        Removes duplicates and GoogleSupport news.

        Args:
            results (list): List of news.

        Returns:
            Returns a clean DataFrame with news and without duplicates or GoogleSupport news.
        """
        final_results = []
        added = set()
        cont = 0
        for _, item in results.iterrows():
            # Look to news id
            if not hash(str(item)) in added and "title" in item and not item["title"] is None:
                added.add(hash(str(item)))
                final_results.append(item)
            else:
                cont += 1
        clean_news = pd.DataFrame(final_results)
        return clean_news

    def __call__(self):
        """
        Main function that scraps GoogleNews news and adds them in a single DataFrame.

        Returns:
            Pandas DataFrame with news.
        """
        print('######### Input #########')
        print(str(self.queries))
        print('######### Search #########')
        news = self.search()
        # news_list = self.parse_resources(resources=news)
        # clean_news = self.clean(news_list)
        df = self.find_keywords(pd.DataFrame(news))
        print("# News: " + str(len(df)))
        df = df.drop_duplicates(subset=['URL'], keep='first')
        return df
