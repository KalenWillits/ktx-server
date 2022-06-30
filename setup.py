from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Weboscket server framework for highly dynamic communication.'

# Setting up
setup(
    name='ktx-server',
    version=VERSION,
    author='Kilthunox',
    url='https://github.com/KalenWillits/ktx-server',
    author_email='<kalenwillits@gmail.com>',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'websockets'
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
