import os
from setuptools import find_packages, setup

from simple_webpack.utils import get_version


here = os.path.abspath(os.path.dirname(__file__))

version = get_version()

with open(os.path.join(here, 'README.rst')) as readme:
    README = '\n' + readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-webpack',
    version=version,
    packages=find_packages(exclude=['django_simple_webpack']),
    include_package_data=True,
    license='MIT',
    description='A simple webpack bundle loader for Django.',
    long_description=README,
    url='https://github.com/gucciferXCIV/django-simple-webpack',
    author='Garrett Jenkins',
    author_email='suppalxciv@gmail.com',
    keywords=['django', 'webpack', 'react', 'static', 'assets', 'bundle'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
