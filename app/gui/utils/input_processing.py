# -*- coding: utf-8 -*-
"""
    topSEARCH

    @author: tgarcianavarro - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 17/02/2023
    @version: 0.2
"""
from typing import List, Optional, Dict

# Stdlib imports


# Third-party app imports
import streamlit as st

# Imports from your apps
from app.gui.utils.file_processing import load_configs
from resourcescraper.load.load_export_metadata import LoadExportMetadata
from resourcescraper.load.load_filters import LoadFilters
from resourcescraper.load.load_queries import LoadQueries


def process_app_inputs(queries: List[str], synonyms: List[List[str]], filter_values: Dict[str, str], metadata: List,
                       new_metadata: Optional[Dict], resource: str):
    """
    Process the inputs for the application.
    Args:
        queries (List[str]): a list of search queries.
        synonyms (List[List[str]]): a list of lists of synonyms, where each list corresponds to the synonyms of a query.
        filter_values (Dict[str, str]): a dictionary where the keys are the names of the filters and the values are 
        their selected values.
        metadata (List): a list containing metadata to include.
        new_metadata (Optional[Dict]): a dictionary containing project-specific metadata to be included.
        resource (str): A string containing the resource type.
    Returns:
        (List): a list containing all the search queries, containing all the combinations of the synonyms.
        (Dict): a dictionary containing the processed filters where the keys are the names of the filters and the 
        values are their selected values.
        (List): a list containing the processed metadata.
        (Dict): a dictionary containing the processed project-specific metadata.
    """
    processed_queries = process_queries(queries, synonyms)
    processed_filters = process_filters(filter_values, resource)
    processed_metadata, processed_other_metadata = process_metadata(metadata, new_metadata, resource)
    return processed_queries, processed_filters, processed_metadata, processed_other_metadata


def process_queries(queries: List[str], synonyms: List) -> List:
    """
    Process the search queries and their synonyms.
    Args:
        queries (List[str]): a list of search queries.
        synonyms (List): a list of lists of synonyms, where each list corresponds to the synonyms of a query.
    Returns
        (List): a list containing all the search queries, containing all the combinations of the synonyms.
    """
    queries_with_synonyms = []
    if queries != ['']:
        for i, query in enumerate(queries):
            if synonyms != ['']:
                queries_with_synonyms.append([query] + synonyms[i])
            else:
                queries_with_synonyms.append([query])
    load_queries = LoadQueries(queries_with_synonyms)
    return load_queries()


def process_filters(filter_values: Dict[str, str], resource: str) -> Dict:
    """
    Process the filters.
    Args:
        filter_values (Dict[str, str]): a dictionary where the keys are the names of the filters and the values are
        their selected values.
        resource (str): A string containing the resource type.
    Returns:
        processed_filters (Dict): a dictionary containing the processed filters where the keys are the names of
        the filters and the values are their selected values.
    """
    load_filters = LoadFilters(filter_values, resource)
    return load_filters()


def process_metadata(metadata: List, project_metadata: Optional[Dict], resource: str):
    """
    Process the metadata.
    Args:
        metadata (List): a list containing metadata to include.
        project_metadata (Optional[Dict]): a dictionary containing project-specific metadata to be included.
        resource (str): A string containing the resource type.
    Returns:
        (List): a list containing the processed metadata.
        (Dict): a dictionary containing the processed project-specific metadata.
    """
    # TODO revisar q es load_export_metadata()
    load_export_metadata = LoadExportMetadata(resource, metadata, project_metadata)
    return load_export_metadata()


def select_configuration(resource: str):
    """
    If selected by the user, loads a saved configuration and sets the values using session state variables.
    Args:
        resource (str): A string containing the resource type.
    """
    # TODO averiguar q es resource
    config_name = st.session_state.get('selected_config_' + resource)
    saved_configs = load_configs(resource)
    if config_name != '-':
        config = saved_configs.get(config_name)
        update_session_state(config, resource)


def update_session_state(config: Dict, resource: str):
    """
    This function updates the session state of the Streamlit app with the information from the given config dictionary.
    Args:
        config (Dict): A dictionary containing the inputs of the selected configuration.
        resource (str): A string containing the resource type.
    """

    # Extract relevant information from the config
    country, filter_values, lang, metadata, queries, queries_synonyms = get_config_values(config)

    # Update the session state with the extracted information
    st.session_state['queries' + '_' + resource] = ', '.join(queries)  # Update the queries input field
    for i, synonyms in enumerate(queries_synonyms):
        query = queries[i].strip()
        # Update the synonyms input field for each term of the query
        st.session_state[f'{query}_synonyms' + '_' + resource] = ', '.join(synonyms)
    if lang:
        st.session_state['lang' + '_' + resource] = lang  # Update the language input field
    if country:
        st.session_state['country' + '_' + resource] = country  # Update the country input field
    st.session_state['filters' + '_' + resource] = list(filter_values.keys())  # Update the filter selection input field
    for k, v in filter_values.items():
        # Update the input fields of the values of the selected filters
        st.session_state[f'filter_{k}_value' + '_' + resource] = v
    st.session_state['metadata' + '_' + resource] = metadata  # Update the metadata input field


def get_config_values(config: Dict) -> [str, Dict, str, List, List, List]:
    """
    Extracts configuration values from the provided dictionary.
    Args:
        config (Dict): A dictionary containing the inputs of the selected configuration.
    Returns:
        (str): A string indicating the country.
        (Dict): A dictionary containing the filter values.
        (str): A string containing language.
        (List): A list containing the metadata.
        (List): A list containing the queries.
        (List): A list containing the synonyms of the queries.
    """
    queries = config.get('queries', [])
    queries_synonyms = config.get('queries_synonyms', [])
    lang = config.get('lang')
    country = config.get('country')
    filter_values = config.get('filter_values', {})
    metadata = config.get('metadata', [])
    return country, filter_values, lang, metadata, queries, queries_synonyms


def transform_dictionary(input_dict: Dict) -> Dict:
    """

    Args:
        input_dict (Dict): A dictionary where each key maps to another dictionary. The inner dictionary's keys are
        strings and values are lists.
    Returns:
        (Dict): A transformed dictionary where each key maps to a list of lists. Each inner list contains a stripped
        subkey followed by its corresponding values.
    """
    transformed_dict = {}

    for key, values in input_dict.items():
        transformed_values = []
        for subkey, subvalues in values.items():
            transformed_values.append([subkey.strip()] + subvalues)
        transformed_dict[key] = transformed_values

    return transformed_dict
