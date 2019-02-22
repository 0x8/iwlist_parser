from setuptools import setup, find_packages

setup(
    name = "iwlist_parser",
    version = "1.0.0",

    author = "Ian Guibas",
    author_email = "unlisted",
    
    description = "Parses iwlist results into structures.",
    long_description = "Module that parses iwlist results into" \
                       "a digestible structure for various uses.",

    packages = find_packages(),
)
