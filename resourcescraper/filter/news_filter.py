import pandas as pd
from unidecode import unidecode


class NewsFilter:
    def __init__(self, news, queries: list[str]):
        """
        Init function.

        Args:
            news: Pandas DataFrame with news.
            queries (list[str]): List of string queries with the terms to search for resources.
        """
        super().__init__()
        self.news = news
        # nltk.download('stopwords')
        self.queries = queries

    def filter(self):
        """
        This filter only accepts news when at least one of the queries (all the words) appear either in the title,
        description or in the summary or at least twice in content of the news.

        Returns:
            Pandas DataFrame with the news that have at least one of the queries.
        """
        res = []
        self.queries = [unidecode(item) for sublist in self.queries for item in sublist]
        for _, news in self.news.iterrows():
            has = True
            for query in self.queries:
                has = True
                # query = [unidecode(word) for word in query.split(" ") if word not in stopwords.words()]
                # i = 0
                # while has:
                term = query
                if not unidecode(str(news['title']).lower()).__contains__(unidecode(str(term).lower())):
                    if not unidecode(str(news['description']).lower()).__contains__(unidecode(str(term).lower())):
                        if news['summary'] is None or not unidecode(str(news['summary']).lower()).__contains__(
                                unidecode(str(term).lower())):
                            if news['content'] is None or (
                                    unidecode(str(news['content']).lower()).count(
                                        unidecode(str(term).lower())) < 2):
                                has = False
                # i += 1
                if has:
                    break
            res.append(has)

        return self.news.loc[res]

    @staticmethod
    def clean(filtered_news):
        """
        Removes columns that were necessary for filtering but do not add up valuable information.

        Args:
            filtered_news: Pandas DataFrame with news.

        Returns:
            Pandas DataFrame with the relevant columns.
        """
        # del filtered_news['content']
        return filtered_news

    def __call__(self):
        """
        Main method that applies the filter to news' data.

        Returns:
            Pandas DataFrame with the news that have passed the filter.
        """
        filtered_news = self.filter()
        news = self.clean(filtered_news)
        return pd.DataFrame(news)
