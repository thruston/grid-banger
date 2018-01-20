#!/usr/bin/python

import distutils.core

distutils.core.setup(
    name='osgb',
    version='1.0.0',
    description='OSGB - high-precision geographic coordinate conversion library for Great Britain, based on OSTN',
    license='MIT Licence',
    author='Toby Thurston',
    author_email='toby@cpan.org',
    url='http://thurston.eml.cc',
    packages=['osgb'],
    package_data={'osgb': ['ostn_east_shift_82140', 'ostn_north_shift_-84180', 'gb-coastline.shapes']},
    scripts=['scripts/bngl', 'scripts/plot_maps.py'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

