"""
    PYTEMPLATE: template project to illustrate the structure of a python-based repository.

    File: config.py
    Description: Contains relative paths regarding project files and folders,
        as well as constants relative to the whole project
    Author: dscorza
    Company: Vicomtech
    Date: 16/09/2019
"""
import os


def build_abspath(sub_path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), sub_path))


resources_path = build_abspath('resources')
test_file_path = build_abspath('test_file')
