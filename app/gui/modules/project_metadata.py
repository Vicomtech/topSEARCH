# -*- coding: utf-8 -*-
"""
    resource-scraper
    
    @author: tgarcianavarro - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: afernandezc - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @date: 17/02/2023
    @version: 0.2
"""

# Stdlib imports


# Third-party app imports
import streamlit as st

# Imports from your apps
from app.gui.utils.file_processing import load_configs, save_new_metadata


def project_metadata() -> dict:
    """
    This function loads the project configuration and displays it if it exists. It prompts the user to input new
    metadata for the project or edit the selected configuration. The function saves the new metadata and displays it.
    Returns:
        (dict): A dictionary containing the project metadata input by the user.
    """
    config = load_configs('project')  # Problema
    if config:
        show_loaded_config(config)
    new_metadata = input_project_metadata()
    edit_save_metadata(config, new_metadata)
    st.write(new_metadata)
    return new_metadata


def edit_save_metadata(config: dict, new_metadata: dict):
    """
    This function saves the new metadata when the user clicks the "Save Metadata" button,
    or updates the metadata when the user clicks the "Edit Metadata" button.
    Args:
        config (dict): A dictionary containing the current project metadata configuration.
        new_metadata (dict): A dictionary containing the new project metadata input by the user.
    """
    if st.button('Edit Metadata' if config else 'Save Metadata'):
        save_new_metadata(new_metadata)
        st.success("Project metadata added")


def input_project_metadata() -> dict:
    """
    Prompts the user to enter project-specific metadata categories, their values and possible synonyms.
    Returns:
         (dict): A dictionary containing user-entered project-specific metadata categories, values and synonyms
    """
    other_metadata_values = {}
    other_metadata = st.text_input("Metadata title (separated by commas)", '', key="other_metadata").strip().split(',')
    new_metadata = {}
    for data in other_metadata:
        if data:
            other_metadata_values[data] = st.text_area(
                f"Possible values for **{data.strip()}** (separated by commas)", '',
                key=f'data_{data.strip()}').strip().split(',')
            new_metadata[data] = {}
            for value in other_metadata_values[data]:
                if value:
                    values = st.text_area(f"Terms related to **{value.strip()}** (separated by commas)", '',
                                          key=f'value_{data.strip()}_{value.strip()}').strip().split(',')
                    new_metadata[data][value] = [v.strip() for v in values if v]
    return new_metadata


def show_loaded_config(config: dict):
    """
     This function displays the current project metadata configuration.
    Args:
         config (dict): A dictionary containing the current project metadata configuration.
    """
    categories = list(config.keys())
    st.session_state['other_metadata'] = ','.join(categories)
    for category in categories:
        data = list(config.get(category).keys())
        st.session_state[f'data_{category.strip()}'] = ','.join(data)
        for value in data:
            values = config.get(category).get(value)
            st.session_state[f'value_{category.strip()}_{value.strip()}'] = ','.join(values)
