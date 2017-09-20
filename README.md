osgb
====

Python routines for working with British OSGB grid references.

The functions in this module convert from OSGB grid references to and from GPS Lat/Lon with high precision.

# install

    python3 setup.py install

# usage

    import osgb

    (lat, lon) = osgb.grid_to_ll(324231, 432525)
    (easting, northing) = osgb.ll_to_grid(52.132341, -2.43256)

    grid_ref = osgb.format_grid(324231, 231423)
    (easting, northing) = osgb.parse_grid("TQ213455")

Toby Thurston -- 09 Jun 2017 


# Contents

    setup.py
    osgb/convert.py
    osgb/gridder.py
    osgb/mapping.data
    osgb/mapping.py
    osgb/ostn02.data
    scripts/bngl
    scripts/make_mapping_data
    test/bench.py
    test/osgb_os_data.py 
