#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = os.path.dirname(__file__)
exec(open(os.path.join(HERE, "construct3", "version.py")).read())

setup(name = "construct3",
    version = version_string, #@UndefinedVariable
    description = "Construct3: Binary parser combinators",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    license = "MIT",
    url = "http://construct.readthedocs.org",
    packages = ["construct3", "construct3.lib"],
    platforms = ["POSIX", "Windows"],
    requires = ["six"],
    install_requires = ["six"],
    keywords = "construct, data structure, binary, parser, builder, pack, unpack",
    #use_2to3 = False,
    #zip_safe = True,
    long_description = open(os.path.join(HERE, "README.md"), "r").read(),
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
)
