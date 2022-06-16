The change history for osgb

## 0.0.x - Paul's old versions

## 1.0.0

- New super-accurate conversion routines based on OSTN15
- Preserves legacy interface

### 1.1.0

- Documentation at https://grid-banger.readthedocs.io/en/latest/index.html
- Moved all functions from `mapping` module into `gridder`
- Fixed issue with array.array methods for Python2 v Python3

### 1.2.0

- Changed rounding behaviour for ``osgb.convert.grid_to_ll``

    This is a mildly breaking change, in that the default outputs will have fewer
    decimal places, but it does *not* mean any loss of accuracy.  If your GR is in
    whole metres, your lat/lon will be rounded to 6 decimal places which is about 10cm
    of accuracy.  A new "rounding" keyword arg allows you to have more places if you
    really want them.

- Allow tuple argument to ``sheet_keys``
- Improved error handling in ``parse_grid``
- Added a script to make a GeoJSON file of each series of map outlines
- Added a zero-points script to show "meetings of Myriads"
- Added flag to bngl.py to show lat/lon in degrees-minutes-seconds notation
- Improved test coverage

## 2.0.0 (future plans)

- The next release will drop support for Python2
