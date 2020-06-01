#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

readme = open('README.rst').read()

setuptools.setup(
    name='nectar-dashboard',
    version='5.0',
    description='nectar-dashboard',
    long_description=readme,
    author='Sam Morrison',
    author_email='sorrison@gmail.com',
    url='https://github.com/NeCTAR-RC/nectar-dashboard',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["horizon<17",
                      "trove-dashboard<14"
                      "django",
                      "djangorestframework",
                      "django-filter<2",
                      "pymysql",
                      "python-dateutil",
                      "manukaclient"],
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
