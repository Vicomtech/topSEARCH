# -*- coding: utf-8 -*-
"""
    resource-scraper
    
    @author: tgarcianavarro - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 20/09/2023
    @version: 0.1
"""
from typing import Any

# Stdlib imports


# Third-party app imports
import streamlit as st

# Imports from your apps
from resourcescraper.utils.constants import ALLOWED_APP_FILTERS, ALLOWED_VIDEO_FILTERS, ALLOWED_PODCAST_FILTERS, \
    ALLOWED_NEWS_FILTERS


def input_app_filters() -> dict[Any, str | None | int | bool]:
    """
    Displays the filter values' inputs for the app scraper.
    Returns
        (dict[Any, str | None | int | bool]): Filter values entered by the user.
    """
    resource = 'apps'
    filters = st.multiselect(
        "", ALLOWED_APP_FILTERS.keys(), key='filters' + '_' + resource, placeholder='Select filters')
    filter_values = {}
    for app_filter in filters:
        if ALLOWED_APP_FILTERS.get(app_filter) == str:
            filter_values[app_filter] = st.text_input(
                f"Value for **{app_filter}**", key=f'filter_{app_filter}_value' + '_' + resource)
        elif ALLOWED_APP_FILTERS.get(app_filter) == int:
            filter_values[app_filter] = st.number_input(
                f"Value for **{app_filter}**", step=1, key=f'filter_{app_filter}_value' + '_' + resource)
        elif ALLOWED_APP_FILTERS.get(app_filter) == float:
            filter_values[app_filter] = st.number_input(
                f"Value for **{app_filter}**", key=f'filter_{app_filter}_value' + '_' + resource)
        elif ALLOWED_APP_FILTERS.get(app_filter) == bool:
            filter_values[app_filter] = st.checkbox(
                f"Check if you want **{app_filter}** to be TRUE (not checked = FALSE)",
                key=f'filter_{app_filter}_value' + '_' + resource)
        else:
            filter_values[app_filter] = st.text_input(
                f"Value for **{app_filter}**", key=f'filter_{app_filter}_value' + '_' + resource)
    return filter_values


def input_video_filters() -> dict[Any, str | None | int | bool]:
    """
    Displays the filter values' inputs for the app scraper.
    Returns:
        (dict[Any, str | None | int | bool]): Filter values entered by the user.
    """
    resource = 'videos'
    filters = st.multiselect(
        "", ALLOWED_VIDEO_FILTERS.keys(), key='filters' + '_' + resource, placeholder='Select filters')
    filter_values = {}
    for video_filter in filters:
        if ALLOWED_VIDEO_FILTERS.get(video_filter) == str:
            filter_values[video_filter] = st.text_input(
                f"Value for **{video_filter}**", key=f'filter_{video_filter}_value' + '_' + resource)
        elif ALLOWED_VIDEO_FILTERS.get(video_filter) == int:
            filter_values[video_filter] = st.number_input(
                f"Value for **{video_filter}**", step=1, key=f'filter_{video_filter}_value' + '_' + resource)
        elif ALLOWED_VIDEO_FILTERS.get(video_filter) == float:
            filter_values[video_filter] = st.number_input(
                f"Value for **{video_filter}**", key=f'filter_{video_filter}_value' + '_' + resource)
        elif ALLOWED_VIDEO_FILTERS.get(video_filter) == bool:
            filter_values[video_filter] = st.checkbox(
                f"Check if you want **{video_filter}** to be TRUE (not checked = FALSE)",
                key=f'filter_{video_filter}_value' + '_' + resource)
        else:
            filter_values[video_filter] = st.text_input(
                f"Value for **{video_filter}**", key=f'filter_{video_filter}_value' + '_' + resource)
    return filter_values


def input_podcast_filters():
    """
    Displays the filter values' inputs for the podcast scraper.
    Returns:
        (dict[Any, str | None | int | bool]): Filter values entered by the user.
    """
    resource = 'podcasts'
    filters = st.multiselect(
        "", ALLOWED_PODCAST_FILTERS.keys(), key='filters' + '_' + resource, placeholder='Select filters')
    filter_values = {}
    for podcast_filter in filters:
        if ALLOWED_PODCAST_FILTERS.get(podcast_filter) == str:
            filter_values[podcast_filter] = st.text_input(
                f"Value for **{podcast_filter}**", key=f'filter_{podcast_filter}_value' + '_' + resource)
        elif ALLOWED_PODCAST_FILTERS.get(podcast_filter) == int:
            filter_values[podcast_filter] = st.number_input(
                f"Value for **{podcast_filter}**", step=1, key=f'filter_{podcast_filter}_value' + '_' + resource)
        elif ALLOWED_PODCAST_FILTERS.get(podcast_filter) == float:
            filter_values[podcast_filter] = st.number_input(
                f"Value for **{podcast_filter}**", key=f'filter_{podcast_filter}_value' + '_' + resource)
        elif ALLOWED_PODCAST_FILTERS.get(podcast_filter) == bool:
            filter_values[podcast_filter] = st.checkbox(
                f"Check if you want **{podcast_filter}** to be TRUE (not checked = FALSE)",
                key=f'filter_{podcast_filter}_value' + '_' + resource)
        else:
            filter_values[podcast_filter] = st.text_input(
                f"Value for **{podcast_filter}**", key=f'filter_{podcast_filter}_value' + '_' + resource)
    return filter_values


def input_news_filters()-> dict[Any, str | None | int | bool]:
    """
    Displays the filter values' inputs for the news scraper.
    Returns:
        (dict[Any, str | None | int | bool]): Filter values entered by the user.
    """
    resource = 'news'
    filters = st.multiselect(
        "", ALLOWED_NEWS_FILTERS.keys(), key='filters' + '_' + resource, placeholder='Select filters')
    filter_values = {}
    for news_filter in filters:
        if ALLOWED_NEWS_FILTERS.get(news_filter) == str:
            filter_values[news_filter] = st.text_input(f"Value for **{news_filter}**",
                                                       key=f'filter_{news_filter}_value' + '_' + resource)
        elif ALLOWED_NEWS_FILTERS.get(news_filter) == int:
            filter_values[news_filter] = st.number_input(f"Value for **{news_filter}**", step=1,
                                                         key=f'filter_{news_filter}_value' + '_' + resource)
        elif ALLOWED_NEWS_FILTERS.get(news_filter) == float:
            filter_values[news_filter] = st.number_input(f"Value for **{news_filter}**",
                                                         key=f'filter_{news_filter}_value' + '_' + resource)
        elif ALLOWED_NEWS_FILTERS.get(news_filter) == bool:
            filter_values[news_filter] = st.checkbox(
                f"Check if you want **{news_filter}** to be TRUE (not checked = FALSE)",
                key=f'filter_{news_filter}_value' + '_' + resource)
        else:
            filter_values[news_filter] = st.text_input(f"Value for **{news_filter}**",
                                                       key=f'filter_{news_filter}_value' + '_' + resource)
    return filter_values
