# -*- coding: utf-8 -*-
"""
    resource-scraper
    
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 17/07/2023
    @version: 0.1
"""
from typing import Any, Tuple

# Stdlib imports


# Third-party app imports
import streamlit as st

# Imports from your apps
from app.gui.utils.file_processing import load_configs, save_config
from app.gui.utils.input_processing import select_configuration, process_app_inputs, transform_dictionary
from resourcescraper.filter.podcast_filter import PodcastFilter
from resourcescraper.resource_scraper.podcast_scraper import PodcastScraper
from resourcescraper.utils.constants import LANGS, COUNTRIES, ALLOWED_PODCAST_FILTERS, ALLOWED_PODCAST_METADATA


def podcasts(new_metadata: dict[Any, dict]):
    """
    Handles the input and processing of information related to the podcast scraping functionality of the
    resource-scraper. It loads and displays previously saved configurations, allows the user to select and enter
    queries, filters, and metadata, and provides options to submit and save configurations.
    Args:
     new_metadata (dict[Any, dict]): contains project-specific metadata categories.
    """
    resource = 'podcasts'
    saved_configs = load_configs(resource)
    st.selectbox("Select Configuration", ['-'] + list(saved_configs.keys()), key='selected_config' + '_' + resource,
                 on_change=select_configuration, args=(resource,))
    with st.expander("Queries", expanded=True):
        country, lang, queries, synonyms = input_queries()
    with st.expander("Filters", expanded=True):
        filter_values = input_filters()
    with st.expander("Metadata", expanded=True):
        metadata = st.multiselect(
            " ", ALLOWED_PODCAST_METADATA, key='metadata' + '_' + resource, placeholder='Select metadata')
    actions(country, filter_values, lang, metadata, new_metadata, queries, synonyms)


def actions(country: str, filter_values: dict, lang: str, metadata: dict, new_metadata: dict[Any, dict], queries: list,
            synonyms: list):
    """
    Provides options to submit and save the configuration, handles the actions taken by the user once inputs have
    been submitted. It is responsible for processing and displaying the submitted queries, filters, and metadata. It
    also provides options to submit and save the configuration.
    Args:
        country (str): The country for which the scraping configuration is applied.
        filter_values (dict): A dictionary containing various filter options.
        lang (str): The language preference for scraping.
        metadata (dict): A dictionary containing various filter options.
        new_metadata (dict[Any, dict]): A dictionary containing new metadata.
        queries (list): The search queries used for the scraping.
        synonyms (list): A list of synonyms that are used in queries or filters.
    """
    cols = st.columns(2)
    submit(cols, country, filter_values, lang, metadata, new_metadata, queries, synonyms)
    save(cols, country, filter_values, lang, metadata, queries, synonyms)


def save(cols, country: str, filter_values: dict, lang: str, metadata: dict, queries: list, synonyms: list):
    """
     Saving of configurations for the app scraper.
     Args:
        cols: A Streamlit columns object.
        country (str): The country for which the scraping configuration is applied.
        filter_values (dict): A dictionary containing various filter options.
        lang (str): The language preference for scraping.
        metadata (dict): A dictionary containing various filter options.
        queries (list): The search queries used for the scraping.
        synonyms (list): A list of synonyms that are used in queries or filters.
    """
    resource = 'podcasts'
    with cols[1]:
        with st.expander("Save configuration", expanded=False):
            config_name = st.text_input("Configuration Name", key='config_name' + '_' + resource)
            if st.button("Save", key='save_button' + '_' + resource):
                save_config(config_name, resource, queries, lang, country, synonyms, filter_values, metadata)
                st.success("Saved configuration successfully")


def submit(cols, country: str, filter_values: dict, lang: str, metadata: dict, new_metadata: dict, queries: list,
           synonyms: list):
    """
    Submission of inputs for the app scraper.
    Args:
        cols: A Streamlit columns object
        country (str): The country for which the scraping configuration is applied.
        filter_values (dict): A dictionary containing various filter options.
        lang (str): The language preference for scraping.
        metadata (dict): A dictionary containing various filter options.
        new_metadata (dict): A dictionary containing new metadata.
        queries (list): The search queries used for the scraping.
        synonyms (list): A list of synonyms that are used in queries or filters.
    """
    resource = 'podcasts'
    with cols[0]:
        if st.button("Submit", key='submit_button' + '_' + resource):
            try:
                processed_queries, processed_filters, processed_metadata, processed_other_metadata = process_app_inputs(
                    queries, synonyms, filter_values, metadata, new_metadata, resource)
                st.success("Processed inputs successfully")
                st.markdown(f"""
                **Queries**: 
                {processed_queries}
                \n
                **Filters**:
                {processed_filters}
                \n
                **Metadata**:
                {processed_metadata + list(processed_other_metadata.keys())}
                """)

                with st.spinner('Wait for it...'):

                    groups = transform_dictionary(processed_other_metadata)

                    podcasts_df = PodcastScraper(processed_queries, groups, lang=lang, country=country)()
                    podcasts_df = PodcastFilter(podcasts_df, [processed_queries], processed_filters)()
                    podcasts_csv = podcasts_df.to_csv(index=False).encode('utf-8')

                st.success('Done!')

                # st.dataframe(podcasts_df)

                st.download_button(
                    "Download",
                    podcasts_csv,
                    "search_podcasts.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(e)


def input_filters() -> dict:
    """
    Displays the filter values' inputs for the app scraper.
    Returns:
         (dict): Filter values entered by the user.
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


def input_queries() -> Tuple[str, str, list, list]:
    """
    Displays the queries inputs for the app scraper.
    Returns:
         (str): The country for which the scraping configuration is applied.
         (str): The language preference for scraping.
         (list): The search queries used for the scraping.
         (list): A list of synonyms that are used in queries or filters.
    """
    resource = 'podcasts'
    queries = st.text_input("Separated by commas", key='queries' + '_' + resource).split(',')
    synonyms = []
    for i, query in enumerate(queries):
        if query != '':
            synonyms.append(st.text_area(f"Synonyms for **{query.strip()}** (separated by commas)",
                                         key=f'{query.strip()}_synonyms' + '_' + resource).split(','))
    lang_cols = st.columns(2)
    with lang_cols[0]:
        lang = st.selectbox("Language", LANGS, key='lang' + '_' + resource)
    with lang_cols[1]:
        country = st.selectbox("Country", COUNTRIES, key='country' + '_' + resource)
    return country, lang, queries, synonyms
