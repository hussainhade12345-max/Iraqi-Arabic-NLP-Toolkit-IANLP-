"""
Setup configuration for Iraqi Arabic NLP Toolkit (IANLP)
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="iraqi-nlp",
    version="0.1.0",
    author="Hussein Hadeh",
    author_email="hussainhade12345@gmail.com",
    description="A labeled dataset and toolkit for Iraqi Arabic NLP research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "regex>=2021.8.0",
        "scikit-learn>=1.0.0",
        "nltk>=3.6.0",
    ],
)
