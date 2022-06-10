osgb
====

.. image:: https://github.com/thruston/grid-banger/actions/workflows/python-app.yml/badge.svg
    :target: https://github.com/thruston/grid-banger/actions/workflows/python-app.yml

.. image:: https://img.shields.io/pypi/v/osgb.svg
    :target: https://pypi.org/project/osgb/

Python routines for working with grid references as defined by the Ordnance Survey of Great Britain (OSGB).

Toby Thurston -- June 2022

The functions in this module convert from OSGB grid references to and from GPS
Latitude and Longitude, using formulae, and the OSTN15 data set, supplied by
OSGB. Conversions are accurate to approximately +/- 1mm. The scope is limited
to the same coverage as the Ordnance Survey maps: England, Wales, Scotland, and
the Isle of Man, but not Northern Ireland, nor the Channel Islands.

This implementation supersedes the ``osgb`` module written by Paul Agapow;
existing code should work unmodified, but the exported functions have been
re-implemented, so the results will be more accurate.

The implementation uses the Ordnance Survey's high-precision dataset
called OSTN15. This dataset is freely available for public use, but
remains (c) Crown copyright, Ordnance Survey and the Ministry of Defence
(MOD) 2016. All rights reserved.

The modules are designed to work with Python 2.7 and with Python 3.5 or better.
When I last checked they were very slightly faster with Python 2.7 than with
Python 3.6, but the functions are, and the results should be, identical.  If
you are still using Python 2, then use ``python2`` (or whatever you call it)
instead of ``python3`` below.

install
-------

::

    python3 setup.py install

or more likely

::

    pip3 install osgb

usage
-----

::

    import osgb

    (lat, lon) = osgb.grid_to_ll(324231, 432525)
    (easting, northing) = osgb.ll_to_grid(52.132341, -2.43256)

    grid_ref = osgb.format_grid(324231, 231423)
    (easting, northing) = osgb.parse_grid("TQ213455")

Each of the modules contains detailed documentation and examples in
"doctest" format:

::

    pydoc osgb/convert.py
    pydoc osgb/gridder.py


For more please see `the page at RTD <https://grid-banger.readthedocs.io/en/latest/>`_.

compatibility
-------------

The original ``osgb`` functions are also still provided for compatibility with old code, so
that code like this, should still work:

::

    from osgb import osgb_to_lonlat, lonlat_to_osgb

    (lon, lat) = osgb_to_lonlat("SD 30271 33770")
    grid_ref = lonlat_to_osgb(-3.058695, 53.795346, digits=5)

Note that the older ``osgb_to_lonlat`` returns latitude and longitude in the
opposite order to the newer ``grid_to_ll``.   If in doubt, note that for valid
OSGB grid references latitude will *always* be greater than longitude.

Note also that the older ``lonlat_to_osgb`` expects the arguments to have longitude
first and latitude second.  However the re-implemented version will determine
the correct sequence automatically, so the calling order does not actually matter.

The re-implementation also adds an optional ``model=`` parameter to each of these functions,
so you can use them with WGS84 coordinates.  Model defaults to ``OSGB36``, so if you leave
it out you will get the old functionality.

::

    (lon, lat) = osgb_to_lonlat("SD 30271 33770", model="WGS84")
    grid_ref = lonlat_to_osgb(-3.058695, 53.795346, digits=5, model="WGS84")

scripts
-------

The scripts directory contains some tools that show examples of how to use this module.

1. The first is a handy command-line conversion tool that will convert a grid reference to
latitude and longitude and vice versa.  With the ``--show`` switch it will try to open
the relevant map on StreetMap.co.uk.  With ``--random`` it will generate a random grid
reference for you. Try

::

    python3 bngl.py TQ 109 324
    python3 bngl.py --show 51.48 0
    python3 bngl.py --help

2. The script called ``plot_maps.py`` will create a map of the OSGB grid system.
To make this work you need to have a current TeX distribution with "mpost"
installed.  Optionally you can add the outlines of the supported map series.

::

    python3 scripts/plot_maps.py --series A

The two PDF files included are examples of the output.

3. The script called ``whatmaps.py`` reads a GPX file (of a track or a route or
   just a list of waymarks) and shows you all the OS maps that cover the points
   in the file.  This uses the external module called ``gpxpy`` to parse the
   GPX data.

4. The script called ``zero-points.py`` prints out a list of all the "meeting of myriad" points
   in the UK that are on an OSGB map.  These are the points with grid references that are all zeros
   like NJ000000 (just above Loch Echtachan) or OV000000 (Beast Cliff).  If you plan on visiting them 
   all, beware that you will need a boat for some of them.



test
----

You can run ``python -m doctest`` against the main modules.

You can also run the ``osgb/test/test_ostn_standard_points....`` routines to check that there are no errors
converting the forty standard points given by the OSGB.

::

    python3 -m doctest osgb/convert.py
    python3 -m doctest osgb/gridder.py
    python3 osgb/test/test_ostn_standard_points_to_grid.py
    python3 osgb/test/test_ostn_standard_points_to_ll.py
    python3 osgb/test/test_some_more_places.py

or, if you have pytest installed, you can do that in one go with

::

    python3 -m pytest --doctest-modules

These tests are automatically run on Github against the currently supported range of Python versions.

You can also run ``test/bench_mark.py`` to see how fast you can go on your system.

::

    python3 test/bench_mark.py

This should produce something like:

::

    Grid banger bench mark running under CPython 3.6.4 on Darwin-17.4.0-x86_64-i386-64bit
    ll_to_grid: 84231/s 0.0119 ms per call
    grid_to_ll: 22564/s 0.0443 ms per call

contents
--------

::

    LICENCE.txt
    README.rst
    requirements.txt
    setup.py
    docs/
    osgb/convert.py
    osgb/gridder.py
    osgb/legacy_interface.py
    osgb/maps-explorer.txt
    osgb/maps-harvey-mountain.txt
    osgb/maps-harvey-superwalker.txt
    osgb/maps-landranger.txt
    osgb/maps-one-inch.txt
    osgb/gb_coastline.shapes
    osgb/ostn_east_shift_82140
    osgb/ostn_north_shift_-84180
    osgb/test/OSTN15_OSGM15_TestFiles_README.txt
    osgb/test/OSTN15_OSGM15_TestInput_ETRStoOSGB.txt
    osgb/test/OSTN15_OSGM15_TestInput_OSGBtoETRS.txt
    osgb/test/OSTN15_OSGM15_TestOutput_ETRStoOSGB.txt
    osgb/test/OSTN15_OSGM15_TestOutput_OSGBtoETRS.txt
    osgb/test/bench_mark.py
    osgb/test/test_ostn_standard_points_to_grid.py
    osgb/test/test_ostn_standard_points_to_ll.py
    osgb/test/test_some_more_places.py
    scripts/bngl.py
    scripts/plot_maps.py
    scripts/whatmaps.py
    Index_for_map_series_A.pdf
    Index_for_map_series_B.pdf
