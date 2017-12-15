#-*- encoding: UTF-8 -*-
from __future__ import print_function
from setuptools import setup
import re
import os
import sys


long_description = (
    "query online dictionaries, and help you remember vocabularie "
    "based on forgetting curve"
)

def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name="wordmemo",
    version=get_version("wordmemo"),
    #url='http://www.github.com',
    license='GNU',
    description='online english dictionaries query; space repetation word learning',
    long_description=long_description,
    author='Farland Liu',
    author_email='farland@163.com',  # SEE NOTE BELOW (*)
    packages=get_packages("wordmemo"),
    include_package_data=True,              

    install_requires = [       
    'bs4',
    'click >=3.3',
    'colorama>=0.3.9'
    ],

    entry_points={
        'console_scripts':[
            'bing = pyDict.bing:cli',
            'col = pyDict.col:cli',
        ]
     },
     classifiers=[
        'Development Status :: 3 - Developing/Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: students, education',
        'License :: OSI Approved :: GNU License',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Language',
        'Topic :: English as the seconde Language',
    ],

    
 )