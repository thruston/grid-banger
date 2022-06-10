The change history for osgb

### 0.0.x - Paul's old versions

### 1.0.0

- New super-accurate conversion routines based on OSTN15
- Preserves legacy interface 

### 1.1.0

- Documentation at https://grid-banger.readthedocs.io/en/latest/index.html
- Moved all functions from `mapping` module into `gridder`
- Fixed issue with array.array methods for Python2 v Python3

### 1.2.0

- WIP lat/lon order, Geojson output

- Changed rounding behaviour for ``osgb.convert.grid_to_ll``

    This is a mildly breaking change, in that the default outputs will have fewer
    decimal places, but it does *not* mean any loss of accuracy.  If your GR is in
    whole metres, your lat/lon will be rounded to 6 decimal places which is about 10cm
    of accuracy.  A new "rounding" keyword arg allows you to have more places if you
    really want them.

- Added a zero-points script to show "meetings of Myriads"
- Added flag to bngl.py to show lat/lon in degrees-minutes-seconds notation
