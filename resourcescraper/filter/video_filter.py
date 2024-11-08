from datetime import datetime

import langdetect
# from nltk.corpus import stopwords
from unidecode import unidecode

from resourcescraper.utils.select_resources import SelectResources


class VideoFilter:

    def __init__(self, df_videos, apply_filters: list, queries: list | str, queries2:list | str):
        """
        Args:
            df_videos: Dataframe containing the searched videos.
            apply_filters (list): List containing filter information.
            queries (list of str): List of search keywords.
            queries2 (list of str): List of keywords for the keyword_search function.
        """

        super().__init__()
        self.videos = df_videos
        self.queries = queries
        self.queries2 = queries2
        self.apply_filter = apply_filters
        self.filters = {
            'keywords': self.keyword_search,
            'language': self.check_language,
            'licensed': self.check_licensedContent,
            'duration': self.check_duration,
            'views': self.check_viewCount,
            'likes': self.check_likeCount,
            'subscribers': self.check_subscriberCount,
            'recent_update': self.check_recent_update
        }

    def filter(self):
        """
        Applies inclusion and exclusion criteria to filter the videos.
        """
        # Filter by inclusion and exclusion criteria
        print("######### Filter #########")
        for video_filter in self.apply_filter:
            print("Filter: " + video_filter[0])
            self.videos = self.filters[video_filter[0]](video_filter[1])
            print("\tRemaining videos: " + str(len(self.videos)))
        # self.videos.to_csv("videos_filtered_ordered.csv", encoding='utf-8-sig')
        pass

    def keyword_search(self, value: bool):
        """
        Performs a keyword search on the videos based on the provided value.
        Args:
            value (bool): Boolean indicating whether the keyword filter should be applied (True) or not (False).

        Returns:
            DataFrame containing the videos that have passed the keyword filter. If no filtering is
            applied, the original DataFrame may be returned.
        """
        if value:
            res = []
            self.queries2 = [unidecode(item) for sublist in self.queries2 for item in sublist]
            for _, video in self.videos.iterrows():
                has = True
                for query in self.queries2:
                    has = True
                    term = query
                    if not unidecode(str(video["title"]).lower()).__contains__(unidecode(str(term).lower())):
                        if not unidecode(str(video["description"]).lower()).__contains__(unidecode(str(term).lower())):
                            if not unidecode(str(video["description_complete"]).lower()).__contains__(
                                    unidecode(str(term).lower())):
                                if not unidecode(str(video["tags"]).lower()).__contains__(unidecode(str(term).lower())):
                                    has = False
                    if has:
                        break
                res.append(has)
            return self.videos.loc[res]
        else:
            return self.videos

    def check_language(self, value: str):
        """
        This method filters the videos based on the specified language. It searches for videos that match the provided
        language and returns a DataFrame containing the filtered results.
        Args:
            value (str): Language to look for in the video resources.

        Returns:
            DataFrame containing the videos that have passed the language filter. If no videos match the
            specified language, an empty DataFrame may be returned.
        """
        res = []
        for index, video in self.videos.iterrows():
            if video["title"]:
                match = self.text_has_language(str(video["title"]), value)
                if match is False:
                    match = self.text_has_language(str(video["description"]), value)
                res.append(match)
            else:
                res.append(True)
        return self.videos.loc[res]

    @staticmethod
    def text_has_language(text: str, language: str) -> bool:
        """
        This function analyzes the input text and checks for the presence of the specified language. It returns True if
        the language is detected, otherwise returns False.

        Args:
            text (str): The text to be analyzed for language detection.
            language (str): The language to look for in the text.

        Returns:
            bool: True if the specified language is detected in the text, False otherwise.
        """
        detected_language = langdetect.detect(text)
        if detected_language[0] == language:
            return True
        else:
            return False

    def check_licensedContent(self, value):
        return SelectResources(self.videos).value_equal('licensedContent', value)

    def check_duration(self, value):
        return SelectResources(self.videos).value_lte('duration', value)

    def check_viewCount(self, value):
        return SelectResources(self.videos).value_gte('viewCount', value)

    def check_likeCount(self, value):
        return SelectResources(self.videos).value_gte('likeCount', value)

    def check_subscriberCount(self, value):
        return SelectResources(self.videos).value_gte('subscriberCount', value)

    @staticmethod
    def difference_date_today(date: datetime) -> float:
        """
        This function calculates the absolute difference in years between the specified date and the current date.
        It returns the difference as a floating-point number.

        Args:
            date (datetime): A datetime object representing the date to compare.

        Returns:
            float: The absolute difference in years between the specified date and today.
        """
        today = datetime.today()
        return abs((today - date).days) / 365

    def check_recent_update(self, value: int):
        """
        This method filters the podcasts in the DataFrame to identify those that have been updated within the specified
        number of years. It checks the difference between the last update date of each podcast and today, returning
        only those that meet the criteria.

        Args:
            value (int): The maximum number of years allowed between the
                         last update of the podcast and today.

        Returns:
            A DataFrame containing the podcasts that have been updated within the specified timeframe.
        """
        updates = self.videos["publishedAt"].tolist()
        updated = map(lambda x: self.difference_date_today(datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")) < value, updates)
        return self.videos.loc[updated]

    def __call__(self):
        self.filter()
        return self.videos
