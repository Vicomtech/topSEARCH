# -*- coding: utf-8 -*-
"""

    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

import time
import zipfile

import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt

from app.topsearch.utils.plots import plot_cumulative, plot_genre_counts, plot_video_tags, plot_common_words, \
    plot_news_keyword_counts, likes_rate_metric, create_stacked_distribution_plot

# Page configuration
st.set_page_config(
    page_title="topSEARCH Analytics",
    layout="wide"
)

_, column, _ = st.columns(3)
column.markdown("<h1 style='text-align: center'>Search comparison</h1>", unsafe_allow_html=True)


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


def render_tab1(options: list, searches: dict):
    """
    Renders the first tab with pie charts and metrics for the selected options.
    Args:
        options (list): A list of selected search keys.
        searches (dict): A dictionary containing lists of DataFrames for each search key.
    """
    num_columns = len(options)
    cols = st.columns(num_columns)

    for option, col in zip(options, cols):
        col.subheader(f"{option}")

        data_list = searches[option]
        lengths = [len(item) for item in data_list]

        labels = ['Apps', 'Videos', 'Podcasts', 'News']

        fig, ax = plt.subplots()
        ax.pie(lengths, labels=labels, autopct='%1.1f%%', colors=sns.color_palette('Set2'), startangle=90)
        ax.set_aspect('equal')
        plt.tight_layout()

        col.pyplot(fig, clear_figure=True)

        col.metric(f'Total resources', sum(lengths), None)
        for idx, length in enumerate(lengths):
            col.metric(f"Total {labels[idx].lower()}", length, None)


def render_tab3(options: list, searches: dict):
    """
    Renders the third tab with cumulative plots and metrics for Apps, Videos, Podcasts, and News.

    Args:
        options (list): A list of selected search keys.
        searches (dict): A dictionary containing lists of DataFrames for each search key.
    """
    # Apps
    st.subheader('Apps')

    col1, col2, col3 = st.columns(3)
    app_vars = col1.selectbox('Filter by', ['Count', 'ratings', 'installs'])
    genre_filter = col3.multiselect('Genre', ['Medicina', 'Educación', 'Salud y forma física'])
    date_filter = col2.selectbox('Date', ['All time', 'Past year', 'Past month', 'Past week'],
                                 key='app')

    fig_apps = plot_cumulative(
        searches, app_vars, options, 'genres', genre_filter, date_filter, 0
    )

    st.pyplot(fig_apps, clear_figure=True)

    st.divider()

    # Videos
    st.subheader('Videos')

    col1, col2, col3 = st.columns(3)
    video_vars = col1.selectbox('Filter by', ['Count', 'likeCount', 'viewCount', 'commentCount',
                                              'subscriberCount', 'duration', 'likes_rate'])
    tag_filter = col3.multiselect('Genre', ['lung', 'cancer', 'smoking'])
    date_filter = col2.selectbox('Date', ['All time', 'Past year', 'Past month', 'Past week'],
                                 key='video')

    fig_videos = plot_cumulative(
        searches, video_vars, options, 'tags', tag_filter, date_filter, 1
    )

    st.pyplot(fig_videos, clear_figure=True)

    st.divider()

    # Podcasts
    st.subheader('Podcasts')

    col1, col2, col3 = st.columns(3)
    podcast_vars = col1.selectbox('Filter by', ['Count', 'trackTime'])
    pod_kw_filter = col3.multiselect('Genre', ['cancer', 'lung', 'breast', 'patients'])
    date_filter = col2.selectbox('Date', ['All time', 'Past year', 'Past month', 'Past week'],
                                 key='podcast')

    fig_podcasts = plot_cumulative(
        searches, podcast_vars, options, 'description', pod_kw_filter, date_filter, 2
    )

    st.pyplot(fig_podcasts, clear_figure=True)

    st.divider()

    # News
    st.subheader('News')

    col1, col2, col3 = st.columns(3)
    news_vars = col1.selectbox('Filter by', ['Count', 'textLength'])
    kw_filter = col3.multiselect('Genre', ['lung', 'breast', 'cancer', 'treatment'])
    date_filter = col2.selectbox('Date', ['All time', 'Past year', 'Past month', 'Past week'],
                                 key='news')

    fig_news = plot_cumulative(
        searches, news_vars, options, 'keywords', kw_filter, date_filter, 3
    )

    st.pyplot(fig_news, clear_figure=True)


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
#         options = st.multiselect('Select by search', searches.keys(), max_selections=3)
#
#         if options:
#
#             start_time = time.perf_counter()
#
#             num_columns = len(options)
#
#             # tabs
#             tab1, tab2, tab3, tab4, tab5 = st.tabs(
#                 ['General', 'Genres', 'Trends', 'Metrics', 'Duration plots']
#             )
#
#             # General tab
#             with tab1:
#                 render_tab1(options, searches)
#
#             # Genres tab
#             with tab2:
#                 if num_columns > 0:
#                     # Add as many columns as needed
#                     cols = st.columns(num_columns)
#
#                     # Show metrics for each selected app in their respective columns
#                     for i, col in enumerate(cols):
#                         col.header(options[i])
#
#                         col.subheader('Apps')
#
#                         figure = plot_genre_counts(searches, options, 'genres', i)
#                         col.pyplot(figure)
#
#                         col.subheader('Videos')
#
#                         figure = plot_video_tags(searches, options, 'tags', i)
#                         col.pyplot(figure)
#
#                         # col.subheader('Podcasts')
#
#                         # figure = plot_common_words(searches, options, 'description', i)
#                         # col.pyplot(figure)
#
#                         # col.subheader('News')
#
#                         # figure = plot_news_keyword_counts(searches, options, 'keywords', i)
#                         # col.pyplot(figure)
#
#             # Trends tab
#             with tab3:
#                 render_tab3(options, searches)
#
#             # Metrics tab
#             with tab4:
#                 if num_columns > 0:
#                     # Add as many columns as needed
#                     cols = st.columns(num_columns)
#
#                     # Show metrics for each selected app in their respective columns
#                     for i, col in enumerate(cols):
#                         col.header(options[i])
#
#                         likes_rate_total = likes_rate_metric(searches, options, i)
#                         downloads_total = searches[options[i]][0]['installs'].sum()
#                         avg_subs = searches[options[i]][1]['subscriberCount'].mean()
#                         avg_score = searches[options[i]][0]['score'][0:2].mean()
#                         # avg_text_length = searches[options[i]][3]['textLength'].mean()
#
#                         col.metric('Likes rate', round(likes_rate_total, 3), None)
#                         col.metric('App downloads', downloads_total, None)
#                         col.metric('Average subscribers', avg_subs.round(0), None)
#                         col.metric('Average app rating', avg_score.round(0), None)
#                         # col.metric('Average article length', avg_text_length.round(0), None)
#
#             # Duration plots tab
#             with tab5:
#                 # Videos
#                 st.subheader('Videos')
#
#                 slider_options = [2, 5]
#                 time_slider = st.select_slider('Enter bar width', options=slider_options, key='slider_videos')
#
#                 fig_duration = create_stacked_distribution_plot(searches, options, 'duration', 1, time_slider)
#                 st.pyplot(fig_duration)
#
#                 st.divider()
#
#                 # Podcasts
#                 st.subheader('Podcasts')
#
#                 slider_options = [5, 10, 15, 20]
#                 time_slider = st.select_slider('Enter bar width', options=slider_options, key='slider_podcasts')
#
#                 fig_duration = create_stacked_distribution_plot(searches, options, 'trackTime', 2, time_slider)
#                 st.pyplot(fig_duration)
#
#                 st.divider()
#
#                 # Videos
#                 # st.subheader('News')
#                 #
#                 # slider_options = [1, 2.5, 5]
#                 # time_slider = st.select_slider('Enter bar width', options=slider_options, key='slider_news')
#                 #
#                 # fig_duration = create_stacked_distribution_plot(searches, options, 'duration', 3, time_slider)
#                 # st.pyplot(fig_duration)
#
#                 print("Execution time Comparison:", time.perf_counter() - start_time)
#         else:
#             st.warning('Please select at least one option.')
def main():
    # Display the "Coming soon" message
    st.write("### Coming soon")


if __name__ == "__main__":
    main()
