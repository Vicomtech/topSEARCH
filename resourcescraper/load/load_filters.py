from resourcescraper.utils.constants import ALLOWED_APP_FILTERS, ALLOWED_VIDEO_FILTERS, ALLOWED_PODCAST_FILTERS, \
    ALLOWED_NEWS_FILTERS


class LoadFilters:
    def __init__(self, filter_values: dict, resource: str):
        """
        Initializes the LoadFilters class with a dictionary of filter values.

        Args:
            filter_values (dict): A dictionary of filter values.
            resource (str): String indicating the resource type.
        """
        self.names = list(filter_values.keys())
        self.values = filter_values.values()
        self.as_dict = filter_values
        self.resource = resource
        super().__init__()

    def check(self):
        """
        Checks whether the filter names and values are allowed.

        Raises:
            Exception: If a filter name or value is not allowed.
        """
        for name, value in zip(self.names, self.values):
            if self.resource == 'apps':
                if name not in ALLOWED_APP_FILTERS.keys():
                    raise Exception(f'{name} is not an allowed filter')
                if type(value) != ALLOWED_APP_FILTERS.get(name):
                    raise Exception(f'{name} filter was expecting {ALLOWED_APP_FILTERS.keys()} '
                                    f'and received {value} which '
                                    f'is {type(value)}')
            elif self.resource == 'videos':
                if name not in ALLOWED_VIDEO_FILTERS.keys():
                    raise Exception(f'{name} is not an allowed filter')
                if type(value) != ALLOWED_VIDEO_FILTERS.get(name):
                    raise Exception(f'{name} filter was expecting {ALLOWED_VIDEO_FILTERS.keys()} '
                                    f'and received {value} which '
                                    f'is {type(value)}')
            elif self.resource == 'podcasts':
                if name not in ALLOWED_PODCAST_FILTERS.keys():
                    raise Exception(f'{name} is not an allowed filter')
                if type(value) != ALLOWED_PODCAST_FILTERS.get(name):
                    raise Exception(f'{name} filter was expecting {ALLOWED_PODCAST_FILTERS.keys()} '
                                    f'and received {value} which '
                                    f'is {type(value)}')
            elif self.resource == 'news':
                if name not in ALLOWED_NEWS_FILTERS.keys():
                    raise Exception(f'{name} is not an allowed filter')
                if type(value) != ALLOWED_NEWS_FILTERS.get(name):
                    raise Exception(f'{name} filter was expecting {ALLOWED_NEWS_FILTERS.keys()} '
                                    f'and received {value} which '
                                    f'is {type(value)}')

    def __call__(self) -> list:
        """
        Calls the check method and returns a list of tuples containing the filter names and values.

        Returns:
            list: A list of tuples containing the filter names and values.
        """
        self.check()
        return list(zip(self.names, self.values))
