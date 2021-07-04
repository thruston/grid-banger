OSGB function reference
=======================

OSGB Convert
------------

.. automodule:: osgb.convert
   :members:

OSGB Gridder
------------

.. automodule:: osgb.gridder
   :members:

Gridder also provides two dictionaries with data about British maps.  If you have
``import osgb`` at the top of your Python script you can refer to the dictionaries
as::

    osgb.name_for_map_series
    osgb.map_locker

The first has just five entries, as follows::

    {
        'A': 'OS Landranger',
        'B': 'OS Explorer',
        'C': 'OS One-Inch 7th series',
        'H': 'Harvey British Mountain Maps',
        'J': 'Harvey Superwalker',
    }

The ``map_locker`` is rather larger; it has an entry for each sheet (and sub-sheet)
in the five series.  The keys are the map labels consisting of the series letter + ``:`` + the sheet number.
The values are named tuples called "Sheet" with data for the map.  Here is an example::

    {
        "A:4" : Sheet(
            bbox = [[420000, 1107000], [460000, 1147000]],
            area = 1600,
            series = 'A',
            number = '4',
            parent = 'A:4',
            title = 'Shetland – South Mainland',
            polygon = [[420000,1107000],[460000,1107000],[460000,1147000],[420000,1147000],[420000,1107000]]
        ),
    }

- `bbox` is a list of two (easting, northing) pairs that give the LL and UR corners of the bounding box of the map.
- `area` is a string giving the area of the sheet in square km.
- `series` is one of the keys from :py:data:`osgb.mapping.name_for_map_series`
- `number` is a string giving the sheet number/label
- `parent` is a the key of the parent sheet.  This is only relevant for insets and subsheets.
- `title` a version of the title printed on the front of the map
- `polygon` a list of (easting, northing) pairs that define the boundary of the map.  Note that the last pair should always equal the first pair.

Example:
    
    for m in osgb.map_locker.values():
        print(m.number, m.title)



Legacy interface
----------------

.. automodule:: osgb.legacy_interface
   :members:

