#!/usr/bin/env python3
"""
BIM Real Options Valuation Model - Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bim-rov-valuation",
    version="1.0.1",
    author="Hanbin Lee",
    author_email="ehxhf789789@gmail.com",
    description="BIM Real Options Valuation Model for Construction Design Service Bidding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehxhf789789/01_Real_Options-Based_Bid_Decision_Support_Framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "bim-rov=src.valuation_engine:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.csv", "figures/*.png"],
    },
)
