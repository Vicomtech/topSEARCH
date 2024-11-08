import multiprocessing

import pandas as pd
from joblib import Parallel, delayed
from unidecode import unidecode
import nltk
from nltk.corpus import stopwords


class Scraper:

    def __init__(self, groups:dict):
        """
        Args:
            groups (dict): Dictionary containing the cancer types.
        """
        self.groups = groups

    def parse_resources(self, resources=None):
        """
        Calls again to the API to get more metadata for each video.

        Args:
            resources (list): All resources if already searched.

        Returns:
            DataFrame of all resources with corresponding parse metadata.
        """
        # Parallelize
        p = multiprocessing.cpu_count()
        if resources is None:
            res = Parallel(n_jobs=p)(delayed(self.parse)(pd.DataFrame(resource)) for resource in self.search())
        else:
            res = Parallel(n_jobs=p)(delayed(self.parse)(resource) for i, resource in resources.iterrows())
            res = [s for s in res if s is not None and len(s) > 0]
        res = pd.concat(res)
        res = res.dropna(how='all')
        res = res.dropna(how='all', axis=1)
        return res

    def search(self):
        raise NotImplementedError("Override by child")

    def parse(self, resource):
        raise NotImplementedError("Override by child")

    def find_keywords(self, resources, lan:str='english'):
        """
        Looks for the given keyword groups of self.groups in the title, description, and summary of each news.
        For example:
            self.groups = {
                'cancerTypes': [['breast', 'mammary']]
            }
            title = "Breast cancer for nutrition"
            In this example, 'breast' is found in the title so, in the column cancerTypes, ['breast'] is added.

        Args:
            resources: Pandas DataFrame with the news that have been found.
            lan (str): language of the resources ('english', 'en', 'spanish' ).
        Retruns:
            Pandas DataFrame with an added column per group in self.groups and a list of terms that have been found
            per news.
        """
        nltk.download('stopwords')
        stop_words = set(stopwords.words(lan))
        news_data = resources.copy()
        news_data['combined_text'] = news_data['title'].fillna("") + " " + news_data['description'].fillna("")
        if "tags" in news_data.columns:
            news_data['combined_text'] = news_data['combined_text'] + news_data['tags'].fillna("")

        # Process each group
        for group_name, group_terms in self.groups.items():
            print("Group: " + group_name)
            for group_terms_list in group_terms:
                col_name = f'{group_name}_{group_terms_list[0]}'
                terms_set = {unidecode(term.lower()) for term in group_terms_list}
                news_data[col_name] = news_data.apply(
                    lambda row: [term for term in terms_set if all([unidecode(str(word).lower()) in unidecode(row["combined_text"].lower()) for word in term.split() if word not in stop_words])],
                    axis=1
                )

        del news_data['combined_text']
        return news_data

    def clean(self):
        raise NotImplementedError("Override by class")
