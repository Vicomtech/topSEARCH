from collections import Counter
from typing import Tuple

import altair as alt
import numpy as np
import pandas as pd
import seaborn as sns
import squarify
from matplotlib import pyplot as plt
from nltk import word_tokenize
from nltk.corpus import stopwords


def load_time_table(byte_objects_df: dict, labels: list, durations: list):
    """
    Creates a DataFrame summarizing the amount of data and corresponding durations.
    Args:
        byte_objects_df (dict): A dictionary where keys are labels and values are DataFrames.
        labels (list): A list of labels for the DataFrame index.
        durations (list): A list of durations corresponding to each label.

    Returns:
        A DataFrame with the amount of data and durations for each label.
    """
    # Calculate the length of each dataframe in byte_objects
    amount = [len(df) for df in byte_objects_df.values()]

    # Create a dictionary with the data
    data = {
        'Amount': amount,
        'Time': durations
    }

    # Create a dataframe
    df = pd.DataFrame(data, index=labels)

    return df


def plot_dataframe_lengths(byte_objects_df: dict, labels: list):
    """
    Plots a pie chart showing the lengths of DataFrames.
    Args:
        byte_objects_df (dict): A dictionary where keys are labels and values are DataFrames.
        labels (list): A list of labels for the pie chart.

    Returns:
        The matplotlib figure object containing the pie chart.
    """
    dataframe_lengths = [len(df) for df in byte_objects_df.values()]

    plt.pie(dataframe_lengths, labels=labels, autopct='%1.1f%%')
    plt.axis('equal')

    return plt.gcf()


def transform_byte_objects(byte_objects_df: dict):
    """
    Transforms a dictionary of DataFrames by extracting, concatenating, and normalizing 'time' columns.
    Args:
        byte_objects_df (dict): A dictionary where keys are labels and values are DataFrames containing a 'time' column.

    Returns:
        A DataFrame with normalized counts of 'time' values grouped by month.
    """
    # Extract the 'time' columns from each dataframe
    time_columns = [df['time'] for df in byte_objects_df.values()]

    # Concatenate these columns vertically
    concatenated = pd.concat(time_columns)

    # Convert the concatenated column to datetime
    concatenated = pd.to_datetime(concatenated)

    # Sort the concatenated column by date in ascending order
    sorted_df = concatenated.sort_values().reset_index(drop=True)

    # Reset the index to convert Float64Index to RangeIndex
    sorted_df = sorted_df.reset_index()

    # Create an all ones column named 'One'
    sorted_df['One'] = 1

    # Group the 'One' values by month and sum them to get the count
    sorted_df['Count'] = sorted_df.groupby(sorted_df['time'].dt.to_period('M'))['One'].transform('sum')

    # Normalize the 'Count' column from 0 to 100
    max_count = sorted_df['Count'].max()
    min_count = sorted_df['Count'].min()
    sorted_df['Count'] = ((sorted_df['Count'] - min_count) / (max_count - min_count)) * 100

    return sorted_df


def plot_count_over_time(df):
    """
    Plots a line chart showing the count over time with zooming functionality.

    Args:
        df: A DataFrame containing 'time' and 'Count' columns.

    Returns:
        An Altair chart object displaying the count over time.
    """
    # Create the Altair Chart object
    df['time'] = pd.to_datetime(df['time'])  # Convert time column to datetime if it's not already

    # Filter out the last 2 months
    last_two_months = df['time'].max() - pd.DateOffset(months=2)
    last_four_years = df['time'].max() - pd.DateOffset(years=4)
    filtered_df = df[df['time'] <= last_two_months]
    filtered_df = filtered_df[filtered_df['time'] >= last_four_years]
    chart = alt.Chart(filtered_df).mark_line().encode(
        x='time',
        y='Count'
    ).properties(
        title='Interest over time'
    ).configure_axis(
        labelFontSize=12,  # Adjust the label font size as needed
        titleFontSize=14,  # Adjust the title font size as needed
        grid=True,  # Show grid lines
        gridOpacity=1,  # Set the opacity of grid lines
        gridDash=[1, 1]  # Set the dash pattern for grid lines
    ).configure_axisY(
        title=None  # Remove the y-axis label
    )

    # Enable zooming functionality
    selection = alt.selection_interval(bind='scales', encodings=['x'])
    chart = chart.add_selection(selection).transform_filter(selection)

    # Display the chart
    return chart


def plot_video_tags(searches: dict, options: list, column_name: str, idx: int):
    """
    Plots the top 5 tags from a specified column in a DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        column_name (str): The name of the column containing tags.
        idx (int): The index of the DataFrame within the list associated with the key.

    Returns:
        The matplotlib figure object containing the plot.
    """
    # Convert the column to string before splitting
    searches[options[idx]][1][column_name] = searches[options[idx]][1][column_name].astype(str)

    # Now, you can safely use the .str accessor
    tags_list = searches[options[idx]][1][column_name].str.split(';')

    # Create a flat list of all tags, excluding ' '
    all_tags = [tag.strip() for sublist in tags_list for tag in sublist if tag.strip() != '']

    # Count the occurrences of each tag
    tag_counts = pd.Series(all_tags).value_counts().head(5)

    # Plot the top 5 tags using seaborn
    fig = plt.figure()
    squarify.plot(sizes=tag_counts.values, label=tag_counts.index, alpha=0.8)
    plt.axis('off')
    plt.title('Top 5 tags')
    return fig


def plot_genre_counts(searches: dict, options: list, column_name: str, idx: int):
    """
    Plots the top 5 genres from a specified column in a DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        column_name (str): The name of the column containing genres.
        idx (int): The index of the DataFrame within the list associated with the key.

    Returns:
        The matplotlib figure object containing the plot.
    """
    # Split the genres string and create a list of genres
    genres_list = (searches[options[idx]][0][column_name]
                   .apply(lambda x: [genre.strip() for genre in x.strip("[]").split(",")]))

    # Create a flat list of all genres
    all_genres = [genre for sublist in genres_list for genre in sublist]

    # Count the occurrences of each genre
    genre_counts = pd.Series(all_genres).value_counts().head(5)

    # Plot the genre counts using seaborn
    fig = plt.figure()
    squarify.plot(sizes=genre_counts.values, label=genre_counts.index, alpha=0.8)
    plt.axis('off')
    plt.title('Top 5 genres')
    return fig


def plot_common_words(searches: dict, options: list, column_name: str, idx: int):
    """
    Plots the top 5 common words from a specified column in a DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        column_name (str): The name of the column containing text data.
        idx (int): The index of the DataFrame within the list associated with the key.

    Returns:
        The matplotlib figure object containing the plot.
    """
    # Convert the column to string
    searches[options[idx]][2][column_name] = searches[options[idx]][2][column_name].astype(str)

    # Join the values after converting to string
    combined_text = ' '.join(searches[options[idx]][2][column_name].values)

    # Tokenize the combined text into individual words
    words = word_tokenize(combined_text)

    # Remove stop words from the word list
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.lower() not in stop_words]

    # Count the occurrences of each word
    word_counts = Counter(words)

    # Get the most common words and their counts
    most_common_words = word_counts.most_common(5)

    # Extract the words and counts separately
    common_words, counts = zip(*most_common_words)

    # Create the labels for the treemap
    labels = [f'{word} ({count})' for word, count in most_common_words]

    # Plot the genre counts using seaborn
    fig = plt.figure()
    squarify.plot(sizes=counts, label=labels, alpha=0.8)
    plt.axis('off')
    plt.title('Top 5 keywords')
    # return fig


def plot_news_keyword_counts(searches: dict, options: list, column_name: str, idx: int):
    """
    Plots the top 5 keywords from a specified column in a DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        column_name (str): The name of the column containing keywords.
        idx (int): The index of the DataFrame within the list associated with the key.

    Returns:
        The matplotlib figure object containing the plot.
    """
    # Split the 'tags' column into individual tags
    # tags_list = searches[options[idx]][3][column_name].str.split().explode().value_counts()

    # Sort the tags in descending order
    # sorted_tags = tags_list.sort_values(ascending=False)

    # Select the top 5 tags
    # kw_counts = sorted_tags[:5]

    # Plot the genre counts using seaborn
    # fig = plt.figure()
    # squarify.plot(sizes=kw_counts.values, label=kw_counts.index, alpha=0.8)
    # plt.axis('off')
    # plt.title('Top 5 keywords')
    # return fig


def get_date_range(filter_type: str, date_series) -> Tuple[None | int, None | int]:
    """
    Returns a date range based on the specified filter type.
    Args:
        filter_type (str): The type of date filter to apply. Options are 'All time', 'Past year', 'Past month', 'Past week'.
        date_series: A pandas Series containing datetime values.

    Returns:
        tuple or None: A tuple containing the start and end dates if a filter is applied, or None if 'All time' is selected.
    """
    if filter_type == 'All time':
        return None
    elif filter_type == 'Past year':
        end_date = date_series.max()
        start_date = end_date - pd.DateOffset(years=1)
    elif filter_type == 'Past month':
        end_date = date_series.max()
        start_date = end_date - pd.DateOffset(months=1)
    elif filter_type == 'Past week':
        end_date = date_series.max()
        start_date = end_date - pd.DateOffset(weeks=1)
    else:
        raise ValueError('Invalid date filter type')

    return start_date, end_date


def plot_cumulative(searches: dict, variable_column: str, labels: list, genre_column: str, genres: list = None,
                    date_filter_sort: str = None, content_num: int = 0):
    """
    Plots cumulative data over time for specified labels, with optional genre and date filtering.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        variable_column (str): The name of the column to plot.
        labels (list): A list of selected search keys.
        genre_column (str): The name of the column containing genre information.
        genres (list, optional): A list of genres to filter by. Defaults to None.
        date_filter_sort (str, optional): The date filter to apply. Options are 'All time', 'Past year', 'Past month', 'Past week'. Defaults to None.
        content_num (int, optional): The index of the DataFrame within the list associated with the key. Defaults to 0.

    Returns:
        The matplotlib figure object containing the plot.
    """
    dfs = []

    for label in labels:
        dfs.append(searches[label][content_num])

    dataframes = dfs

    # Sort the dataframes by the date column
    sorted_dataframes = [data.sort_values(by='time') for data in dataframes]

    # Convert the 'time' column to datetime-like data type for each dataframe
    for dataframe in sorted_dataframes:
        dataframe['time'] = pd.to_datetime(dataframe['time'])  # Convert 'time' column to datetime-like data type
        dataframe['Month'] = dataframe['time'].dt.month
        dataframe['Count'] = dataframe.groupby('Month')['time'].transform('count')

    # Filter dataframes based on genre
    if genres:
        sorted_dataframes = [data[np.logical_and.reduce([data[genre_column].apply(
            lambda x: genre in x) for genre in genres])] for data in sorted_dataframes]

    # Filter dataframes based on date range
    if date_filter_sort:
        if date_filter_sort == 'All time':
            pass
        else:
            date_range = get_date_range(date_filter_sort, sorted_dataframes[0]['time'])
            sorted_dataframes = [data[data['time'].between(date_range[0], date_range[1])] for data in
                                 sorted_dataframes]

    # Create the line plots
    figure, ax = plt.subplots(figsize=(10, 6))

    for dataframe, label in zip(sorted_dataframes, labels):
        ax.plot(dataframe['time'], dataframe[variable_column], label=label)

    # Set the plot title and axis labels
    ax.set_title(f'{variable_column} over time')
    ax.set_xlabel('Time')
    ax.set_ylabel(f'{variable_column}')

    # Display the legend
    ax.legend()

    # Display the plot
    return figure


def likes_rate_metric(searches: dict, options: list, idx: int) -> float:
    """
    Calculates the likes rate metric for a specified DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        idx (int): The index of the DataFrame within the list associated with the key.

    Returns:
        float: The likes rate, calculated as the sum of 'likeCount' divided by the sum of 'viewCount'.
    """
    # Calculate the sum of 'likeCount' in video_df
    sum_like_count = searches[options[idx]][1]['likeCount'].sum()
    sum_view_count = searches[options[idx]][1]['viewCount'].sum()

    # Calculate the final 'usefulness' variable
    likes_rate = sum_like_count / sum_view_count
    return likes_rate


def create_stacked_distribution_plot(searches: dict, options: list, column_name: str, content_num: int, slider: int):
    """
    Creates a stacked distribution plot for a specified column across multiple DataFrames.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        options (list): A list of selected search keys.
        column_name (str): The name of the column to plot.
        content_num (int): The index of the DataFrame within the list associated with the key.
        slider (int): The bin width for the histogram.

    Returns:
        The matplotlib figure object containing the plot.
    """
    dfs = []

    for option in options:
        dfs.append(searches[option][content_num])

    figure = plt.figure()

    # Create the stacked distribution plot
    sns.histplot(data=dfs[0], x=column_name, color='blue', binwidth=slider)

    if len(options) > 1:
        sns.histplot(data=dfs[1], x=column_name, color='red', alpha=0.75, binwidth=slider)
        if len(options) == 3:
            sns.histplot(data=dfs[2], x=column_name, color='yellow', alpha=0.75, binwidth=slider)

    # Add labels and title
    plt.legend(options)
    plt.xlabel(column_name + ' (minutes)')
    plt.ylabel('Count')
    plt.title(f'Distribution of {column_name}')

    # Display the plot
    return figure
