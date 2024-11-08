from datetime import datetime

import langdetect
from unidecode import unidecode

from resourcescraper.utils.select_resources import SelectResources


class PodcastFilter:

    # TODO: Add attributes
    def __init__(self, podcasts, queries, apply_filters):
        super().__init__()
        self.podcasts = podcasts
        # nltk.download('stopwords')
        self.queries = queries
        # TODO: Load this array from file at the beginning
        self.apply_filter = apply_filters
        # Available filters
        self.filters = {
            'keywords_search': self.keyword_search,
            'free': self.check_price,
            'recent_update': self.check_recent_update,
            'language': self.check_language
        }

    def check_language(self, value: str):
        """
        Checks if the resources (i.e. podcast) have a matching language. This is checked with the values provided in
        the podcast's languageCodesISO2A column or with a language detection library that tries to extract the
        language from the title, description and summary.

        Args:
            value (str): Language to look for in the resource.

        Returns:
            Pandas DataFrame with the podcasts that have passed the filter.
        """
        res = []
        for index, row in self.podcasts.iterrows():
            try:
                match = str(value).upper() in row["languages"]
                match = match or self.text_has_language(row["title"], value)
                match = match or self.text_has_language(row["description"], value)
                res.append(match)
            except:
                res.append(True)
        res = self.podcasts.loc[res]
        # res.to_csv("../../resources/podcast/podcast_filtered_before_keyword.csv", index=False)
        return res

    def check_price(self, value: bool):
        """
        Checks if the resources (i.e. podcast) are free or not.

        Args:
            value (bool): A boolean indicating if only free podcasts are accepted or all of them.

        Returns:
            Pandas DataFrame with the podcasts that have passed the filter.
        """
        if value:
            return SelectResources(self.podcasts).value_equal('free', value)
        else:
            return self.podcasts

    @staticmethod
    def text_has_language(text: str, language: str) -> bool:
        """
        Detects if the text has the given language.

        Args:
            text (str): String.
            language (str): String of the language to look for.

        Returns
            bool: Boolean indicating if the language has been detected in the provided text.
        """
        _, _, detected_languages = langdetect.detect(text)
        for lang in detected_languages:
            if lang[1] == language:
                return True
        return False

    @staticmethod
    def difference_date_today(date: datetime) -> float:
        """
        Computes the difference in years between the given day and today.

        Args:
            date (datetime): Datetime object.

        Returns:
            float: Float with the difference in years.
        """
        today = datetime.today()
        return abs((today - date).days) / 365

    def check_recent_update(self, value: int):
        """
        Checks if the resources (i.e. podcast) have been updated recently.

        Args:
            value (int): Int indicating the maximum number of years between the last update of the podcast and today.

        Returns:
            Pandas DataFrame with the podcasts that have passed the filter.
        """
        updates = self.podcasts["releaseDate"].tolist()
        updated = map(lambda x: self.difference_date_today(datetime.strptime(x, "%Y-%m-%d")) < value, updates)
        return self.podcasts.loc[updated]

    def keyword_search(self, value: bool):
        """
        This filter only accepts a podcast when at least one of the queries (all the words) appear either in the title,
        description or in the summary.

        Args:
            value: Boolean indicating if this filter is applied.

        Returns:
            Pandas DataFrame with the podcasts that have at least one of the queries.
        """
        if value:
            res = []
            self.queries = [unidecode(item) for sublist in self.queries for item in sublist]
            for _, podcast in self.podcasts.iterrows():
                has = True
                for query in self.queries:
                    has = True
                    term = query
                    if not unidecode(str(podcast["title"]).lower()).__contains__(unidecode(str(term).lower())):
                        if not unidecode(str(podcast["description"]).lower()).__contains__(
                                unidecode(str(term).lower())):
                            has = False
                        # i += 1
                    if has:
                        break
                res.append(has)
            return self.podcasts.loc[res]
        else:
            return self.podcasts

    def filter(self):
        """
        Main loop that applies each of the filters in self.apply_filters and shows how many resources are left
        in each step

        Returns:
            Pandas DataFrame with the podcasts that have passed the filters
        """
        all_podcasts = self.podcasts
        # Filter by inclusion and exclusion criteria
        print("######### Filter #########")
        for podcast_filter in self.apply_filter:
            print("Filter: " + podcast_filter[0])
            self.podcasts = self.filters[podcast_filter[0]](podcast_filter[1])
            if podcast_filter[0] != "free":
                passed = self.matches_filter(list(all_podcasts["id"]), list(self.podcasts["id"]))
                all_podcasts[podcast_filter[0]] = passed
            print("\tRemaining Spotify podcasts: " + str(
                len(SelectResources(self.podcasts).value_equal('provider', 'Spotify'))))
            # print("\tRemaining Apple podcasts: " + str(
            #     len(SelectResources(self.podcasts).value_equal('provider', 'Apple'))))
        # all.to_csv("../../resources/podcast/podcasts_filtered_all.csv", index=False)

    @staticmethod
    def matches_filter(ids: list[str], remaining_ids: list[str]) -> list[bool]:
        """
        Computes a list of booleans indicating if the corresponding id in the same position in the ids parameter
        has passed the filter

        Args:
            ids (list[str]): List of all the podcasts ids
            remaining_ids (list[str]): List of the ids that have passed the filter

        Returns:
            list[bool]: List of boolean indicating which of the ids have passed the filter
        """
        res = []
        for podcast_id in ids:
            res.append(podcast_id in remaining_ids)
        return res

    # TODO: Call previous methods
    def __call__(self):
        self.filter()
        del self.podcasts["free"]
        return self.podcasts
