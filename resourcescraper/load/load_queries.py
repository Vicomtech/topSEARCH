from itertools import product


class LoadQueries:
    def __init__(self, words: [[]]):
        self.search_fields = words
        super().__init__()

    def check(self):
        """
        Check that the search fields are a list of lists.
        """
        if isinstance(self.search_fields, list):
            for elem in self.search_fields:
                if not isinstance(elem, list):
                    raise Exception(f'{elem} is not a list')
        else:
            raise Exception(f'{self.search_fields} is not a list')

    def make_combinations(self) -> list[str]:
        """
        Return all combinations of search fields.

        Returns:
            list[str]: A list of strings, where each string is a combination of search fields,
            with individual fields separated by a space.
        """
        return [' '.join(p) for p in product(*self.search_fields)]

    def __call__(self):
        """
        Check the search fields and return all combinations of search fields.
        """
        self.check()
        return self.make_combinations()
