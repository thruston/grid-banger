osgb
====

Python routines for working with grid references as defined by the Ordnance
Survey of Great Britain (OSGB).

Toby Thurston -- 10 Nov 2017 

The functions in this module convert from OSGB grid references to and from GPS
Lat/Lon with using OSGB formulae and the OSTN15 data set.  Conversions are
accurate to approximately +/- 1mm.  The scope of OSGB is limited to the same
coverage as the Ordnance Survey maps:  England, Wales, Scotland, and the Isle
of Man, but not Northern Ireland, nor the Channel Islands.   

The implementation uses the Ordnance Survey's high-precision dataset called
OSTN15.  This dataset is freely available for public use, but remains © Crown
copyright, Ordnance Survey and the Ministry of Defence (MOD) 2015. All rights
reserved.

The modules are designed to work with Python 2.7 or better and with Python 3.4 or better.
With Python 2, they are slightly faster than with Python 3, but the functions are,
and the results should be, identical.

# install

    python setup.py install
    python3 setup.py install

# usage

    import osgb

    (lat, lon) = osgb.grid_to_ll(324231, 432525)
    (easting, northing) = osgb.ll_to_grid(52.132341, -2.43256)

    grid_ref = osgb.format_grid(324231, 231423)
    (easting, northing) = osgb.parse_grid("TQ213455")

# contents

    LICENCE.txt
    README.md
    osgb/convert.py
    osgb/gridder.py
    osgb/mapping.py
    osgb/ostn_east_shift_82140
    osgb/ostn_north_shift_-84180
    scripts/bngl
    scripts/make_map_locker
    setup.py
    test/bench_mark.py
    test/grid_test_known_points.txt
    test/test_os_data.py
