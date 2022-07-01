from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'Weboscket server framework for highly dynamic communication.'
with open('README.md') as readme:
    LONG_DESCRIPTION=readme.read()

# Setting up
setup(
    name='lexicons',
    version=VERSION,
    author='Kilthunox',
    url='https://github.com/KalenWillits/lexicons',
    author_email='<kalenwillits@gmail.com>',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'websockets',
        'orjson',
        'ipython',
    ],
    keywords=['python', 'websockets', 'server'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ]
)


