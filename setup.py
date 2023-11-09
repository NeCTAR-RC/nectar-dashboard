#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

readme = open('README.rst').read()

setuptools.setup(
    name='nectar-dashboard',
    version='7.0',
    description='nectar-dashboard',
    long_description=readme,
    author='Sam Morrison',
    author_email='sorrison@gmail.com',
    url='https://github.com/NeCTAR-RC/nectar-dashboard',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["horizon>=23.0.0,<24.0.0",
                      "django~=3.2",
                      "djangorestframework",
                      "django-filter",
                      "mysqlclient",
                      "python-dateutil",
                      "python-freshdesk",
                      "django-cors-headers",
                      "manukaclient>=0.7.0",
                      "gnocchiclient",
                      "django-mathfilters",
                      "django-select2-forms @ git+https://github.com/NeCTAR-RC/django-select2-forms.git@nectar/master#egg=django-select2-forms",
                      "django-countries<7.5",
                      "langstrothclient>=0.5.0"
                      ],
    license="GPLv3+",
    zip_safe=False,
    keywords='NeCTAR-RC/nectar-dashboard',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)
