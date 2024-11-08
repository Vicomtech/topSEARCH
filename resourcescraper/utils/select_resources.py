import pandas as pd

"""Selects resources (i.e. rows) from a DataFrame given a column and a value"""


class SelectResources:
    """
    Constructor of the class

    Args:
        data: DataFrame
    """

    def __init__(self, data):
        self.data = data

    def value_equal(self, col:str, value):
        """
        Function that filters the instances

        Args:
            col (str): The selected column
            value: Value to match
        Returns:
            Filtered DataFrame
        """
        return self.data.loc[self.data[col] == value]

    def value_gte(self, col:str, value):
        """
        Function that filters the instances

        Args:
            col (str): The selected column
            value: Value to match
        Returns:
            Filtered DataFrame
        """
        return self.data.loc[pd.to_numeric(self.data[col]) >= value]

    def value_lte(self, col:str, value):
        """
        Function that filters the instances

        Args:
            col (str): The selected column
            value: Value to match
        Returns:
            Filtered DataFrame
        """
        return self.data.loc[pd.to_numeric(self.data[col]) <= value]

    def value_not_equal(self, col:str, value):
        """
        Function that filters the instances

        Args:
            col (str): The selected column
            value: Value to match
        Returns:
            Filtered DataFrame
        """
        return self.data.loc[self.data[col] != value]

    def value_in(self, col:str, value):
        """
        Function that filters the instances

        Args:
            col (str): The selected column
            value: Value to match
        Returns:
            Filtered DataFrame
        """
        return self.data.loc[str(value).upper() in self.data[col]]
