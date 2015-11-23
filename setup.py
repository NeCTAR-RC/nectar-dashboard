#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()

setup(
    name='nectar-dashboard',
    version='0.1.0',
    description='nectar-dashboard',
    long_description=readme,
    author='Sam Morrison',
    author_email='sorrison@gmail.com',
    url='https://github.com/NeCTAR-RC/nectar-dashboard',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'local']),
    include_package_data=True,
    install_requires=["djangorestframework",
                      "pymsql",
                      "python-dateutil"],
    license="GPLv3+",
    zip_safe=False,
    keywords='NeCTAR-RC/nectar-dashboard',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
