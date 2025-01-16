import warnings
from datetime import datetime

import pandas
import nltk
import langdetect
from nltk.corpus import stopwords
from pandas.errors import SettingWithCopyWarning

from resourcescraper.utils.select_resources import SelectResources

warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


class AppFilter:
    """Filters the given apps based on specified filter criteria"""

    def __init__(self, apps, queries: list[str], apply_filters: list):
        """
        Init function.

        Args:
            apps: Pandas DataFrame with apps.
            queries (list[str]): List of string queries with the terms to search for resources.
            apply_filters (list): List of tuples with the filter and the value to be applied.
        """
        super().__init__()
        self.apps = apps
        nltk.download('stopwords')
        self.queries = queries
        # TODO: Load this array from file at the beginning
        self.apply_filter = apply_filters
        # Available filters
        self.filters = {
            'keyword_search': self.keyword_search,
            'privacy_policy': self.check_privacy_policy,
            'score': self.check_score,
            'free': self.check_price,
            'recent_update': self.check_recent_update,
            'developer_has_website': self.check_has_website,
            'language': self.check_language,
            'ratings': self.check_ratings
        }

    def keyword_search(self, value: bool):
        """
        This filter only accepts an app when at least one of the queries (all the words) appear either in the title,
        description or in the summary.

        Args:
            value (bool): Boolean indicating if this filter is applied.

        Returns
            Pandas DataFrame with the apps that have at least one of the queries.
        """
        if value:
            res = []
            for index, app in self.apps.iterrows():
                has = True
                for query in self.queries:
                    query = [word for word in query.split(" ") if word not in stopwords.words()]
                    i = 0
                    while i < len(query) and has:
                        term = query[i]
                        if not str(app["title"]).lower().__contains__(str(term).lower()):
                            if not str(app["description"]).lower().__contains__(str(term).lower()):
                                if app["summary"] is None or not str(app["summary"]).lower().__contains__(
                                        str(term).lower()):
                                    has = False
                        i += 1
                    if has:
                        break
                res.append(has)
            return self.apps.loc[res]
        else:
            return self.apps

    def filter(self):
        """
        Main loop that applies each of the filters in self.apply_filters and shows how many resources are left
        in each step.

        Returns:
            Pandas DataFrame with the apps that have passed the filters.
        """
        all_apps = self.apps
        # Filter by inclusion and exclusion criteria
        print("######### Filter #########")
        for app_filter in self.apply_filter:
            print("Filter: " + app_filter[0])
            self.apps = self.filters[app_filter[0]](app_filter[1])
            if app_filter[0] != "privacy_policy" and app_filter[0] != "free":
                passed = self.matches_filter(list(all_apps["appId"]), list(self.apps["appId"]))
                all_apps[app_filter[0]] = passed
            print("\tRemaining Android apps: " + str(len(SelectResources(self.apps).value_equal('os', 'Android'))))
            print("\tRemaining iOS apps: " + str(len(SelectResources(self.apps).value_equal('os', 'iOS'))))
        # all.to_csv("../../resources/apps/apps_filtered_all.csv", index=False)

    @staticmethod
    def matches_filter(ids: list[str], remaining_ids: list[str]) -> list[bool]:
        """
        Computes a list of booleans indicating if the corresponding id in the same position in the ids parameter
        has passed the filter.

        Args:
            ids (list[str]): List of all the apps ids.
            remaining_ids (list[str]): List of the ids that have passed the filter.

        Returns:
            list[bool]: List of boolean indicating which of the ids have passed the filter.
        """
        res = []
        for app_id in ids:
            res.append(app_id in remaining_ids)
        return res

    def check_privacy_policy(self, value: bool):
        """
        Checks if the resources (i.e. app) have or not a privacy policy available.

        Args:
            value (bool): Boolean indicating if the resource needs to have a privacy policy or not.

        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        if value:
            return SelectResources(self.apps).value_equal('privacyPolicy', value)
        else:
            return self.apps

    def check_ratings(self, value: bool):
        """
        Checks if the resources (i.e. app) have or not a privacy policy available.

        Args:
            value (bool): Boolean indicating if the resource needs to have a privacy policy or not.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        if value:
            return SelectResources(self.apps).value_gte('ratings', value)
        else:
            return self.apps

    @staticmethod
    def convert_type(value, type):
        """
        Converts a given value to the specified type. If the value is None or the string "None", it defaults to
        converting the value 1 to the specified type.

        Args:
            value: The value to be converted.

        Returns:
            The value converted to the specified type, or the default conversion of 1 if the value is None or "None",
            or if an exception occurs during conversion.
        """
        if value is not None or value != "None":
            try:
                return type(value)
            except:
                return type(1)
        return type(1)

    def check_score(self, value: int):
        """
        Checks if the resources (i.e. app) have a score higher than the given value. All the apps that do not have
        any rating are also accepted.

        Args:
            value (int): An int between 0 and 5.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        if value < 0 or value > 5:
            raise ValueError("The score value must be between 0 and 5")
        self.apps['score'] = self.apps['score'].map(lambda x: self.convert_type(x, float))
        self.apps['ratings'] = self.apps['ratings'].map(lambda x: self.convert_type(x, int))
        df1 = SelectResources(self.apps).value_gte('score', float(value))
        # Score 0 but ratings 0 also
        df21 = SelectResources(self.apps).value_equal('score', 0)
        df22 = SelectResources(df21).value_equal('ratings', 0)
        return pandas.concat([df1, df22], axis=0)

    def check_price(self, value: bool):
        """
        Checks if the resources (i.e. app) are free or not.

        Args:
            value (bool): A boolean indicating if only free apps are accepted or all of them.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        if value:
            return SelectResources(self.apps).value_equal('free', value)
        else:
            return self.apps

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
        Checks if the resources (i.e. app) have been updated recently.

        Args:
            value (int): Int indicating the maximum number of years between the last update of the app and today.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        updates = self.apps["currentVersionReleaseDate"].tolist()
        updated = map(lambda x: self.difference_date_today(datetime.strptime(x, "%b %d, %Y")) < value, updates)
        return self.apps.loc[updated]

    def check_has_website(self, value: bool):
        """
        Checks if the resources (i.e. app) have a URL pointing to de developer's website.

        Args:
            value (bool): Boolean indicating if the resource needs to have a developer's website.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        if value:
            return SelectResources(self.apps).value_not_equal('developerWebsite', "None")
        else:
            return SelectResources(self.apps).value_equal('developerWebsite', "None")

    def check_language(self, value: str):
        """
        Checks if the resources (i.e. app) have a matching language. This is checked with the values provided in
        the app's languageCodesISO2A column or with a language detection library that tries to extract the language
        from the title, description and summary.

        Args:
            value (str): Language to look for in the resource.
        Returns:
            Pandas DataFrame with the apps that have passed the filter.
        """
        res = []
        for index, row in self.apps.iterrows():
            try:
                match = str(value).upper() in row["languageCodesISO2A"]
                match = match or self.text_has_language(row["title"], value)
                match = match or self.text_has_language(row["description"], value)
                try:
                    # Only Android has summary
                    match = match or self.text_has_language(row["summary"], value)
                except:
                    pass
                res.append(match)
            except:
                res.append(True)
        res = self.apps.loc[res]
        # res.to_csv("../../resources/apps/apps_filtered_before_keyword.csv", index=False)
        return res

    @staticmethod
    def text_has_language(text: str, language: str) -> bool:
        """
        Detects if the text has the given language.

        Args:
            text (str): String.
            language (str): String of the language to look for.

        Returns:
            bool: Boolean indicating if the language has been detected in the provided text.
        """
        _, _, detected_languages = langdetect.detect(text)
        for lang in detected_languages:
            if lang[1] == language:
                return True
        return False

    def clean(self):
        """
        Removes columns that were necessary for filtering but do not add up valuable information.
        """
        del self.apps["free"]
        del self.apps["privacyPolicy"]
        del self.apps["summary"]

    def __call__(self):
        """
        Main method that applies the filters and cleans the resulting apps' data.

        Returns:
            Pandas DataFrame with the apps that have passed the filters.
        """
        self.filter()
        self.clean()
        return self.apps.sort_values(['ratings'], ascending=False)
