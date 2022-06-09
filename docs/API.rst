OSGB function reference
=======================

The OSGB package provides three modules: ``convert``, ``gridder``, and ``legacy_interface``, 
which are documented below.

Each section shows how to call each function, and explains the arguments and outputs.
The documentation shows the long form of each call, with the module names as prefixes to each function, 
like this::

    import osgb
    (e, n) = osgb.gridder.parse_grid("NH231424")
    (lat, lon) = osgb.convert.grid_to_ll(122414, 123412)

But if you can't remember which function is in which module, or you just get tired of 
typing the prefix names, you can optionally omit the module names, thanks to a bit of 
syntactic-sugar magic, so the above snippet should work the same if you put::

    import osgb
    (e, n) = osgb.parse_grid("NH231424")
    (lat, lon) = osgb.grid_to_ll(122414, 123412)

which is a bit neater.  This applies to all the documented functions in this section.


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

The ``map_locker`` is rather larger; it has an entry for each sheet (and
sub-sheet) in the five series.  The keys are the map labels consisting of the
series letter + ``:`` + the sheet number.  The values are `named tuples <https://docs.python.org/3/library/collections.html#collections.namedtuple>`_
with a typename of "Sheet" with data for the map.  Here is an example::

    {
        "A:4" : Sheet(
            bbox = [[420000, 1107000], [460000, 1147000]],
            area = 1600,
            series = 'A',
            number = '4',
            parent = '',
            title = 'Shetland – South Mainland',
            polygon = [[420000,1107000],[460000,1107000],[460000,1147000],[420000,1147000],[420000,1107000]]
        ),
    }

These are the field names:

- `bbox` is a list of two (easting, northing) pairs that give the LL and UR corners of the bounding box of the map.
- `area` is a string giving the area of the sheet in square km.
- `series` is one of the keys from :py:data:`osgb.name_for_map_series` given above.
- `number` is a string giving the sheet number/label
- `parent` is a the key of the parent sheet.  This is only relevant for insets and subsheets. 
  For regular sheets, the parent is set to the empty string.
- `title` a version of the title printed on the front of the map
- `polygon` a list of (easting, northing) pairs that define the boundary of the map.  Note that the last pair should always equal the first pair.

Example::
    
    for m in osgb.map_locker.values():
        print(m.number, m.title)



Legacy interface
----------------

.. automodule:: osgb.legacy_interface
   :members:

