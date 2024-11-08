# -*- coding: utf-8 -*-
"""
    resource-scraper

    This module provides utility functions for loading and saving JSON configuration files.
    
    @author: tgarcianavarro - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 17/02/2023
    @version: 0.2
"""

# Stdlib imports
import json
import os
from enum import Enum

# Third-party app imports


# Imports from your apps
from app.gui.utils.constants import APPS_CONFIG_JSON, VIDEOS_CONFIG_JSON, PROJECTS_JSON, PODCASTS_CONFIG_JSON, \
    NEWS_CONFIG_JSON


def load_configs(config_path: str) -> dict:
    """
    Load a JSON configuration file located at `config_path` and return its contents as a Python dictionary.
    Args:
     config_path (str): The path to the JSON configuration file.
    Returns:
        (dict): The contents of the JSON configuration file as a dictionary.
    """
    path = get_path(config_path)
    return read_json(path)


def read_json(path: str) -> dict:
    """
    Read a JSON file located at `path` and return its contents as a Python dictionary.
    Args:
        path (str): The path to the JSON file.
    Returns:
        (dict): The contents of the JSON file as a dictionary.
    """
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    print('Incorrect path.')
    return {}


class Resource(Enum):
    APPS = 'apps'
    VIDEOS = 'videos'
    PODCASTS = 'podcasts'
    NEWS = 'news'
    PROJECT = 'project'


def get_path(resource: str) -> str:
    """
    Get the path to the JSON configuration file for the given `resource` or project.
    Args:
        resource (str): The name of the resource for which to get the configuration file path.
    Returns:
        (str): The path to the JSON configuration file for the given resource.
   """
    return {
        Resource.APPS: APPS_CONFIG_JSON,
        Resource.VIDEOS: VIDEOS_CONFIG_JSON,
        Resource.PODCASTS: PODCASTS_CONFIG_JSON,
        Resource.NEWS: NEWS_CONFIG_JSON,
        Resource.PROJECT: PROJECTS_JSON
    }.get(Resource(resource), '')


def save_config(config_name: str, tab: str, queries: list, lang: str, country: str, synonyms: list,
                filter_values: dict, metadata: dict) -> None:
    """
    Save the given configuration parameters to the JSON configuration file for the specified `tab`.
    Args:
        config_name (str): The name of the configuration.
        tab (str): The tab (i.e., resource) for which to save the configuration.
        queries (list): The list of queries to be performed for the given resource.
        lang (str): The language in which to perform the queries.
        country (str): The country in which to perform the queries.
        synonyms (dict): A dictionary of synonyms for the queries.
        filter_values (dict): A dictionary of values to be used for filtering the query results.
        metadata (dict): A dictionary of metadata for the given resource.
    """
    configs = load_configs(tab)
    configs[config_name] = {
        'queries': queries,
        'lang': lang,
        'country': country,
        'queries_synonyms': synonyms,
        'filter_values': filter_values,
        'metadata': metadata,
    }
    with open(get_path(tab), "w") as f:
        json.dump(configs, f)


def save_new_metadata(new_metadata: dict):
    """
    Save the given metadata to the JSON configuration file for projects.
    Args:
        new_metadata (dict): A dictionary of metadata for projects.
    """
    with open(PROJECTS_JSON, "w") as f:
        json.dump(new_metadata, f)
