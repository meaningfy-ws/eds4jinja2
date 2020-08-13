# setup.py
# Date: 12/08/2020
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('requirements-dev.txt') as f:
    requirements_dev = f.read().splitlines()

extras = {
    'test': requirements_dev,
}

__version__ = "0.0.18"

setup(
    name="edt4jinja2",
    version=__version__,
    install_requires=requirements,
    tests_require=requirements_dev,
    extras_require=extras,
    include_package_data=True,
    # package_data={'': ['*.txt'], },
    author="Eugeniu Costetchi",
    author_email="costezki.eugen@gmail.com",
    maintainer="Eugeniu Costetchi",
    maintainer_email="costezki.eugen@gmail.com",
    description="Embed the data source specifications in your JINJA templates directly, " \
                "and enjoy the dynamic data contexts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # long_description_content_type="text/x-rst",
    url="https://github.com/meaningfy-ws/eds4jinja2",
    platforms='any',
    keywords='template, jinja, rdf, sparql, linked-data, data-source, dynamic-context',
    packages=find_packages(exclude=("tests",)),
    # exclude=["tests", "test_*"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires='>=3.6',
)
