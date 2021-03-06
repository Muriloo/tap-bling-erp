#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-bling-erp",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Murilo",
    url="https://github.com/Muriloo",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_bling_erp"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python==5.9.1",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    tap-bling-erp=tap_bling_erp:main
    """,
    packages=["tap_bling_erp"],
    package_data = {
        "schemas": ["tap_bling_erp/schemas/*.json"]
    },
    include_package_data=True,
)
