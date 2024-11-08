from typing import Tuple

from resourcescraper.utils.constants import (ALLOWED_APP_METADATA, ALLOWED_VIDEO_METADATA, ALLOWED_PODCAST_METADATA,
                                             ALLOWED_NEWS_METADATA)


class LoadExportMetadata:
    """
    Class for checking and returning metadata fields.

    Args:
        api_fields (list): List of API fields to check. Default is an empty list.
        scrap_fields (dict): Dictionary of scrape fields to check. Default is an empty dictionary.
    """

    def __init__(self, resource, api_fields:list=None , scrap_fields:dict=None):
        if scrap_fields is None:
            scrap_fields = {}
        if api_fields is None:
            api_fields = []
        self.api_fields = api_fields
        self.scrap_fields = scrap_fields
        self.resource = resource
        super().__init__()

    def check_api_fields(self):
        """
        Checks if the API fields specified in the `api_fields` list are allowed, raising an exception if not.
        """
        if self.api_fields:
            for field in self.api_fields:
                if self.resource == 'apps':
                    if field not in ALLOWED_APP_METADATA:
                        raise Exception(
                            f'Field {field} is not an allowed metadata field. Choose one of the following: \n {ALLOWED_APP_METADATA}')
                if self.resource == 'videos':
                    if field not in ALLOWED_VIDEO_METADATA:
                        raise Exception(
                            f'Field {field} is not an allowed metadata field. Choose one of the following: \n {ALLOWED_VIDEO_METADATA}')
                if self.resource == 'podcasts':
                    if field not in ALLOWED_PODCAST_METADATA:
                        raise Exception(
                            f'Field {field} is not an allowed metadata field. Choose one of the following: \n {ALLOWED_PODCAST_METADATA}')
                if self.resource == 'news':
                    if field not in ALLOWED_NEWS_METADATA:
                        raise Exception(
                            f'Field {field} is not an allowed metadata field. Choose one of the following: \n {ALLOWED_NEWS_METADATA}')

    def check_scrape_fields(self):
        """
        Checks if the scrape fields specified in the `scrap_fields` dictionary are valid.
        """
        if self.scrap_fields:
            for field, values in self.scrap_fields.items():
                if not isinstance(values, dict):
                    raise Exception(
                        f'The project-specific metadata defined contains errors. The value of {field} has to be a dict')
                for value, synonyms in values.items():
                    if not isinstance(synonyms, list):
                        raise Exception(
                            f'The project-specific metadata defined contains errors. The synonyms of {value} has to be a list')

    def check(self):
        """
        Calls both `check_api_fields()` and `check_scrape_fields()` to perform the necessary checks
         on both sets of metadata fields.
        """
        self.check_api_fields()
        self.check_scrape_fields()

    def __call__(self) -> Tuple[list, dict]:
        """
        Calls the `check()` method and returns the `api_fields` and `scrap_fields`.
        """
        self.check()
        return self.api_fields, self.scrap_fields
