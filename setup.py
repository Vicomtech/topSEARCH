# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()
with open('CONTRIBUTING.md') as f:
    contributing = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    name='resourcescraper',
    version='0.0.1',
    description='example set up file for installing the gui',
    long_description=readme,
    author='Ander Cejudo (Vicomtech), Teresa García-Navarro (Vicomtech), Yone Tellechea (Vicomtech), Amaia Calvo (Vicomtech)',
    author_email='acejudo@vicomtech.org',
    url=' ',
    # contributing=contributing,
    package_dir={
        '': '.'},
    packages=find_packages(where='.', exclude=('tests', 'docs'))
)
