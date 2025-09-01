"""Setup script for Social Scrubber."""

import os

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="social-scrubber",
    version="0.1.0",
    description="A Python tool to help you bulk-delete your posts from Twitter, Mastodon, and Bluesky",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hossain Khan",
    author_email="",
    url="https://github.com/hossain-khan/social-scrubber",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "social-scrubber=social_scrubber.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
