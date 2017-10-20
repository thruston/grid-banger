osgb
====

Python routines for working with grid references as defined by the Ordnance
Survey of Great Britain (OSGB).

Toby Thurston -- 08 Oct 2017 

The functions in this module convert from OSGB grid references to and from GPS
Lat/Lon with using OSGB formulae and the OSTN02 data set.  Conversions are
accurate to approximately +/- 1mm.  The scope of OSGB is limited to the same
coverage as the Ordnance Survey maps:  England, Wales, Scotland, and the Isle
of Man, but not Northern Ireland, nor the Channel Islands.   

The implementation uses the Ordnance Survey's high-precision dataset called
OSTN02.  This dataset is freely available for public use, but remains © Crown
copyright, Ordnance Survey and the Ministry of Defence (MOD) 2002. All rights
reserved.

# install

    python3 setup.py install

# usage

    import osgb

    (lat, lon) = osgb.grid_to_ll(324231, 432525)
    (easting, northing) = osgb.ll_to_grid(52.132341, -2.43256)

    grid_ref = osgb.format_grid(324231, 231423)
    (easting, northing) = osgb.parse_grid("TQ213455")

# contents

    setup.py
    osgb/convert.py
    osgb/gridder.py
    osgb/mapping.data
    osgb/mapping.py
    osgb/ostn02.data
    scripts/bngl
    scripts/make_mapping_data
    test/bench_mark.py
    test/osgb_os_data.py 



