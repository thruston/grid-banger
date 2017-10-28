#!/usr/bin/python

import distutils.core

distutils.core.setup(
    name='osgb',
    version='0.0.1',
    description='OSGB high-precision coordinate conversion library based on OSTN',
    license='MIT Licence',
    author='Toby Thurston',
    author_email='toby@cpan.org',
    url='http://thurston.eml.cc',
    packages=['osgb'],
    package_data={'osgb': ['ostn02.data']},
    scripts=['scripts/bngl'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

