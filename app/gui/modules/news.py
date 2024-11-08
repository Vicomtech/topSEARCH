# -*- coding: utf-8 -*-
"""
    resource-scraper
    
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 17/07/2023
    @version: 0.1
"""
from typing import Any

# Stdlib imports


# Third-party app imports
import streamlit as st

# Imports from your apps
from app.gui.utils.file_processing import load_configs, save_config
from app.gui.utils.input_processing import select_configuration, process_app_inputs, transform_dictionary
from resourcescraper.filter.news_filter import NewsFilter
from resourcescraper.resource_scraper.news_scraper import NewsScraper
from resourcescraper.utils.constants import LANGS, COUNTRIES, ALLOWED_NEWS_FILTERS, ALLOWED_NEWS_METADATA


def news(new_metadata: dict[Any, dict]):
    """
    Handles the input and processing of information related to the news scraping functionality of the
    resource-scraper. It loads and displays previously saved configurations, allows the user to select and enter
    queries, filters, and metadata, and provides options to submit and save configurations.
    Args:
         new_metadata (dict[Any, dict]): A dictionary containing new metadata.
    """
    resource = 'news'
    saved_configs = load_configs(resource)
    st.selectbox("Select Configuration", ['-'] + list(saved_configs.keys()), key='selected_config' + '_' + resource,
                 on_change=select_configuration, args=(resource,))
    with st.expander("Queries", expanded=True):
        country, lang, queries, synonyms = input_queries()
    with st.expander("Filters", expanded=True):
        filter_values = input_filters()
    with st.expander("Metadata", expanded=True):
        metadata = st.multiselect(
            " ", ALLOWED_NEWS_METADATA, key='metadata' + '_' + resource, placeholder='Select metadata')
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
    submit(cols, filter_values, lang, metadata, new_metadata, queries, synonyms)
    save(cols, country, filter_values, lang, metadata, queries, synonyms)


def save(cols, country: str, filter_values: dict, lang: str, metadata: dict, queries: list, synonyms: list):
    """
    Saving of configurations for the news scraper
    Args:
        cols: A Streamlit columns object.
        country (str): The country for which the scraping configuration is applied.
        filter_values (dict): A dictionary containing various filter options.
        lang (str): The language preference for scraping.
        metadata (dict): A dictionary containing various filter options.
        queries (list): The search queries used for the scraping.
        synonyms (list): A list of synonyms that are used in queries or filters.
    """
    resource = 'news'
    with cols[1]:
        with st.expander("Save configuration", expanded=False):
            config_name = st.text_input("Configuration Name", key='config_name' + '_' + resource)
            if st.button("Save", key='save_button' + '_' + resource):
                save_config(config_name, resource, queries, lang, country, synonyms, filter_values, metadata)
                st.success("Saved configuration successfully")


def submit(cols, filter_values: dict, lang: str, metadata: dict, new_metadata: dict[Any, dict], queries: list,
           synonyms: list):
    """
    Submission of inputs for the news scraper
    Args:
        cols: A Streamlit columns object.
        filter_values (dict): A dictionary containing various filter options.
        lang (str): The language preference for scraping.
        metadata (dict): A dictionary containing various filter options.
        new_metadata (dict[Any, dict]): A dictionary containing new metadata.
        queries (list): The search queries used for the scraping.
        synonyms (list): A list of synonyms that are used in queries or filters.
    """
    resource = 'news'
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

                # TODO Use st.status() for indicating when it's searching and filtering
                with st.spinner('Wait for it...'):

                    medios = ['Infosalus', 'ConSalud', 'AECC', 'FECMA (Federación Española de cáncer de mama)',
                              'GEPAC (Grupo español de pacientes con cáncer)', 'GEICAM',
                              'EuropaColon España (Asociación de pacientes con cáncer colorrectal)',
                              'Cancer.net (from American Society of Clinical Oncology)',
                              'Cancer.org (from American Society of Clinical Oncology)',
                              'Asociación Española de Afectados de Cáncer de Pulmón',
                              'ANCAP (Asociación de Cáncer de Próstata)', 'Unoentrecienmil.org',
                              'Fundación Josep Carreras', 'Revista Española de Salud Pública', 'Fundación Fero',
                              'Instituto Catalán de Oncología', 'Saber Vizir', 'EFESalud',
                              'SEOP (Sociedad Española de Oncología Médica)',
                              'AECIMA (Asociación Española de Cirujanos de la mama)',
                              'SESPM (Sociedad Española de Senología y Patología Mamaria)',
                              'CNIO (Centro Nacional Investigaciones Oncológicas)',
                              'GECP (Grupo Español Cancer Pulmón)', 'Hospital Universitari Vall D’Hebron',
                              'Hospital Universitario 12 de Octubre', 'Clínica Universidad de Navarra',
                              'Hospital General Universitario Gregorio Marañón', 'Hospital Clínic Barcelona',
                              'CNN en Español']

                    groups = transform_dictionary(processed_other_metadata)

                    news_df = NewsScraper(queries=processed_queries, medios=medios, language=lang, groups=groups)()
                    news_df = NewsFilter(news_df, [processed_queries])()
                    news_csv = news_df.to_csv(index=False).encode('utf-8')

                st.success('Done!')

                st.download_button(
                    "Download",
                    news_csv,
                    "search_news.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(e)


def input_filters():
    """
     Displays the filter values' inputs for the news scraper.
    :return: Filter values entered by the user
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


def input_queries():
    """
    Displays the queries inputs for the news scraper.
    :return: Queries values entered by the user.
    """
    resource = 'news'
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
