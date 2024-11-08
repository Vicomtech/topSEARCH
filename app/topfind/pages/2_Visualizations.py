# -*- coding: utf-8 -*-
"""

    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

import time
import zipfile
from typing import Tuple

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from app.topfind.utils.plots import likes_rate_metric

# Page configuration
st.set_page_config(
    page_title="topFIND Analytics",
    layout="wide"
)


_, column, _ = st.columns(3)
column.markdown("<h1 style='text-align: center'>Visualizations</h1>", unsafe_allow_html=True)


def process_zip_file(file, searches: dict):
    """
    Processes a ZIP file containing CSV files and stores the data in a dictionary.
    Args:
        file: The ZIP file to be processed.
        searches (dict): A dictionary to store the DataFrames, with keys derived from the ZIP file name.
    """
    # Open the ZIP file
    zf = zipfile.ZipFile(file)

    # Get the filename without the extension to use as the key
    key = ' '.join([word.capitalize() for word in file.name.split('.')[0].split('_')[3:]])

    # Initialize a list to store DataFrames for this key
    searches[key] = []

    # Iterate through the files in the ZIP archive
    for filename in zf.namelist():
        # Check if the file is a CSV file
        if filename.endswith('.csv'):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(zf.open(filename))

            # Append the DataFrame to the list for this key
            searches[key].append(df)


def get_date_range(filter_type: str, date_series: pd.Series) -> Tuple[None | int, None | int]:
    """
    Returns a date range based on the specified filter type.
    Args:
        filter_type (str): The type of date filter to apply. Options are 'All time', 'Past year', 'Past month',
        'Past week'.
        date_series (pd.Series): A pandas Series containing datetime values.

    Returns:
        tuple or None: A tuple containing the start and end dates if a filter is applied, or None if 'All time' is
        selected.

    Raises:
        ValueError: If an invalid filter type is provided.
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


@st.cache_data
def plot_cumulative(searches: dict, label: list, content_num: int):
    """
    Plots the cumulative percentage increase of counts over time from a specified DataFrame.
    Args:
        searches (dict): A dictionary containing lists of DataFrames.
        label (list): A list where the first element is the key to access the DataFrame in the `searches` dictionary.
        content_num (int): The index of the DataFrame within the list associated with the key.

    Returns:
        The matplotlib figure object containing the plot.
    """
    df = searches[label[0]][content_num].copy()  # Make a copy of the DataFrame

    df['time'] = pd.to_datetime(df['time'])

    # Sort the DataFrame by the date column
    sorted_dataframe = df.sort_values(by='time')

    # Create 'Month' and 'Count' columns for each dataframe
    sorted_dataframe['Week'] = sorted_dataframe['time'].dt.isocalendar().week
    sorted_dataframe['Count'] = sorted_dataframe.groupby('Week')['time'].transform('count')

    # Calculate percentage increase
    sorted_dataframe['Percentage Increase'] = sorted_dataframe['Count'].pct_change() * 100

    # Create the line plot
    figure, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sorted_dataframe['time'], sorted_dataframe['Percentage Increase'], label=label[0])

    # Set the plot title and axis labels
    ax.set_title('Percentage Increase of Count over time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Percentage Increase')

    # Display the legend
    ax.legend()

    # Display the plot
    plt.show()
    return figure


# def main():
#     """
#     Main function to upload and process ZIP files, and display visualizations and metrics.
#     """
#     files = st.file_uploader("Upload zip files", type="zip", accept_multiple_files=True)
#
#     if files:
#         searches = {}
#         for file in files:
#             process_zip_file(file, searches)
#
#         option = st.multiselect('Select by search', searches.keys(), max_selections=1)
#
#         if option:
#
#             start_time = time.perf_counter()
#
#             # tabs
#             tab1, tab2 = st.tabs(
#                 ['General', 'Metrics']
#             )
#
#             with tab1:
#                 # Apps
#                 st.subheader('Apps')
#
#                 fig_apps = plot_cumulative(searches, option, 0)
#                 st.pyplot(fig_apps, clear_figure=True)
#
#                 st.divider()
#
#                 # Videos
#                 st.subheader('Videos')
#
#                 fig_videos = plot_cumulative(searches, option, 1)
#                 st.pyplot(fig_videos, clear_figure=True)
#
#                 st.divider()
#
#                 # Podcasts
#                 st.subheader('Podcasts')
#
#                 fig_podcasts = plot_cumulative(searches, option, 2)
#                 st.pyplot(fig_podcasts, clear_figure=True)
#
#                 st.divider()
#
#                 # News
#                 st.subheader('News')
#
#                 fig_news = plot_cumulative(searches, option, 3)
#                 st.pyplot(fig_news, clear_figure=True)
#
#             with tab2:
#                 st.header(option[0])
#
#                 likes_rate_total = likes_rate_metric(searches, option, 0)
#                 downloads_total = searches[option[0]][0]['installs'].sum()
#                 avg_subs = searches[option[0]][1]['subscriberCount'].mean()
#                 avg_score = searches[option[0]][0]['score'][0:2].mean()
#                 # avg_text_length = searches[option[0]][3]['textLength'].mean()
#
#                 st.metric('Likes rate', round(likes_rate_total, 3), None)
#                 st.metric('App downloads', downloads_total, None)
#                 st.metric('Average subscribers', avg_subs.round(0), None)
#                 st.metric('Average app rating', avg_score.round(0), None)
#                 # st.metric('Average article length', avg_text_length.round(0), None)
#
#             print("Execution time Visualizations:", time.perf_counter() - start_time)
#
#         else:
#             st.warning('Please select an option.')
#             st.stop()

def main():
    # Display the "Coming soon" message
    st.write("### Coming soon")


if __name__ == "__main__":
    main()
