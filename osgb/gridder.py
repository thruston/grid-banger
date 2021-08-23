# coding: utf-8
"""Parse and format OSGB grid reference strings.

This module provides functions to parse and format grid references, and
to tell you which maps include a given reference.
"""
from __future__ import unicode_literals, print_function, division

import ast
import collections
import math
import pkgutil
import re

__all__ = ['format_grid', 'parse_grid', 'sheet_keys']

GRID_SQ_LETTERS = 'VWXYZQRSTULMNOPFGHJKABCDE'
GRID_SIZE = int(math.sqrt(len(GRID_SQ_LETTERS)))
MINOR_GRID_SQ_SIZE = 100000
MAJOR_GRID_SQ_SIZE = GRID_SIZE * MINOR_GRID_SQ_SIZE
MAJOR_GRID_SQ_EASTING_OFFSET = 2 * MAJOR_GRID_SQ_SIZE
MAJOR_GRID_SQ_NORTHING_OFFSET = 1 * MAJOR_GRID_SQ_SIZE
MAX_GRID_SIZE = MINOR_GRID_SQ_SIZE * len(GRID_SQ_LETTERS)


def get_sheet(key):
    '''Fetch a map from the locker
    >>> print(get_sheet("A:1").title)
    Shetland - Yell, Unst and Fetlar

    '''
    try:
        return map_locker[key]
    except KeyError:
        return None


"""Some checks for the maps

>>> 'A' in name_for_map_series
True

>>> all(map_locker[label].series in name_for_map_series for label in map_locker)
True

>>> all(len(map_locker[label].bbox) == 2 for label in map_locker)
True
"""

name_for_map_series = {
    'A': 'OS Landranger',
    'B': 'OS Explorer',
    'C': 'OS One-Inch 7th series',
    'H': 'Harvey British Mountain Maps',
    'J': 'Harvey Superwalker',
}

Sheet = collections.namedtuple("Sheet", "bbox area series number parent title polygon")
map_locker = {}


def _load_maps(series, filename):
    '''Read a maps file into a dict'''
    maps = dict()
    for line in pkgutil.get_data('osgb', filename).decode('utf-8').splitlines():
        sheet, inset, bbox, area, title, polygon = (x.strip() for x in line.split('  ') if x)
        key = '{}:{}'.format(series, sheet)
        if inset == '.':
            parent = ''
        else:
            parent = key
            key += '.' + inset

        if series == 'B':
            number = sheet.strip('NEWS')
        else:
            number = sheet

        maps[key] = Sheet(
            ast.literal_eval(bbox),
            float(area),
            series, number, parent, title,
            ast.literal_eval(polygon)
            )

    return maps


map_locker.update(_load_maps('A', 'maps-landranger.txt'))
map_locker.update(_load_maps('B', 'maps-explorer.txt'))
map_locker.update(_load_maps('C', 'maps-one-inch.txt'))
map_locker.update(_load_maps('H', 'maps-harvey-mountain.txt'))
map_locker.update(_load_maps('J', 'maps-harvey-superwalker.txt'))


class Error(Exception):
    """Parent class for Gridder exceptions"""
    pass


class GridParseError(Error):
    """Parent class for parsing exceptions"""
    pass


class GridFormatError(Error):
    """Parent class for formatting exceptions"""
    pass


class GarbageError(GridParseError):
    """Raised when no grid ref can be deduced from the string given.

    Attributes:
        input

    """
    def __init__(self, spam):
        self.spam = spam

    def __str__(self):
        return "I can't read a grid reference from this -> {}".format(self.spam)


class SheetMismatchError(GridParseError):
    """Raised when grid ref given is not on sheet given

    Attributes:
        sheet
        easting
        northing

    """
    def __init__(self, sheet, easting, northing):
        self.sheet = sheet
        self.easting = easting
        self.northing = northing

    def __str__(self):
        return "Grid point ({}, {})".format(self.easting, self.northing) \
               + " is not on sheet {}".format(self.sheet)


class UndefinedSheetError(GridParseError):
    """Raised when sheet given is not one we know

    Attributes:
        sheet

    """
    def __init__(self, sheet):
        self.sheet = sheet

    def __str__(self):
        return "Sheet {} is not known here.".format(self.sheet)


class FaultyFormError(GridFormatError):
    """Raised when the form given to format_grid is unmatched.

    Attributes:
       form

    """
    def __init__(self, form):
        self.form = form

    def __str__(self):
        return "This form argument was not matched --> form='{}'".format(self.form)


class FarFarAwayError(GridFormatError):
    """Raised when grid reference is nowhere near GB.

    Attributes:
       northing
       easting
    """
    def __init__(self, easting, northing):
        self.easting = easting
        self.northing = northing

    def __str__(self):
        return "The spot with coordinates" \
                + " " \
                + "({:g}, {:g})".format(self.easting, self.northing) \
                + " " \
                + "is too far from the OSGB grid"


def _is_left_right_or_on(x, y, a, b):
    '''Is the point (x, y) left of, right of, or on the line from a to b?
    Left: > 0, On: == 0, Right: < 0

    >>> _is_left_right_or_on(0, 0, (42,-4), (42, +4)) > 0
    True
    >>> _is_left_right_or_on(0, 0, (0, 42), (0, -42)) == 0
    True
    >>> _is_left_right_or_on(0, 0, (-42,-4), (-42, +4)) < 0
    True
    '''
    return (b[0] - a[0]) * (y - a[1]) - (x - a[0]) * (b[1] - a[1])


def _winding_number(x, y, poly):
    '''This is adapted from http://geomalgorithms.com/a03-_inclusion.html'''
    w = 0
    for i in range(len(poly)-1):
        if poly[i][1] <= y:
            if poly[i+1][1] > y and _is_left_right_or_on(x, y, poly[i], poly[i+1]) > 0:
                w += 1
        else:
            if poly[i+1][1] <= y and _is_left_right_or_on(x, y, poly[i], poly[i+1]) < 0:
                w -= 1
    return w


def format_grid(easting, northing=None, form='SS EEE NNN'):
    """Formats an (easting, northing) pair into traditional grid reference.

    This routine formats an (easting, northing) pair into a traditional
    grid reference with two letters and two sets of three numbers, like this:
    ``SU 387 147``.

    >>> print(format_grid(438710.908, 114792.248))
    SU 387 147

    If you want the individual components, apply ``split()`` to it.

    >>> print('-'.join(format_grid(438710.908, 114792.248).split()))
    SU-387-147

    and note that the results are strings not integers.  Note also that
    rather than being rounded, the easting and northing are truncated
    (as the OS system demands), so the grid reference refers to the
    lower left corner of the relevant square.  The system is described
    below the legend on all OS Landranger maps.

    The ``format_grid`` routine takes an optional keyword argument
    ``form``, that controls the form of grid reference returned.

    >>> print(format_grid(438710.908, 114792.248, form='SS EEE NNN'))
    SU 387 147
    >>> print(format_grid(438710.908, 114792.248, form='SS EEEEE NNNNN'))
    SU 38710 14792
    >>> print(format_grid(438710.908, 114792.248, form='SS'))
    SU
    >>> print(format_grid(438710.908, 114792.248, form='SSEN'))
    SU31
    >>> print(format_grid(438710.908, 114792.248, form='SSEENN'))
    SU3814
    >>> print(format_grid(438710.908, 114792.248, form='SSEEENNN'))
    SU387147
    >>> print(format_grid(438710.908, 114792.248, form='SSEEEENNNN'))
    SU38711479
    >>> print(format_grid(438710.908, 114792.248, form='SSEEEEENNNNN'))
    SU3871014792
    >>> print(format_grid(438710.908, 114792.248, form='SS EN'))
    SU 31
    >>> print(format_grid(438710.908, 114792.248, form='SS EE NN'))
    SU 38 14
    >>> print(format_grid(438710.908, 114792.248, form='SS EEE NNN'))
    SU 387 147
    >>> print(format_grid(438710.908, 114792.248, form='SS EEEE NNNN'))
    SU 3871 1479
    >>> print(format_grid(400010.908, 114792.248, form='SS EEEEE NNNNN'))
    SU 00010 14792

    You can't leave out the SS, you can't have N before E, and there
    must be the same number of Es and Ns.  Except for the two special
    formats:

    >>> print(format_grid(438710.908, 114792.248, form='TRAD'))
    SU 387 147
    >>> print(format_grid(438710.908, 114792.248, form='GPS'))
    SU 38710 14792

    The format can be given as upper case or lower case or a mixture.

    >>> print(format_grid(438710.908, 114792.248, form='trad'))
    SU 387 147

    but in general the form argument must match ``"SS E* N*"`` (spaces optional)

    >>> format_grid(432800, 250000, form='TT') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    FaultyFormError: This form argument was not matched --> form='TT'

    Here are some more extreme examples:

    >>> print(format_grid(314159, 271828, form='SS'))
    SO
    >>> print(format_grid(0, 0, form='SS'))
    SV
    >>> print(format_grid(432800, 1250000, form='SS'))
    HP

    The arguments can be negative...

    >>> print(format_grid(-5, -5, form='SS'))
    WE

    ...but must not be too far away from the grid:

    >>> format_grid(-1e12, -5) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    FarFarAwayError: The spot with coordinates (-1e+12, -5) is too far from the OSGB grid


    """
    if northing is None:
        (easting, northing) = easting

    e = easting + MAJOR_GRID_SQ_EASTING_OFFSET
    n = northing + MAJOR_GRID_SQ_NORTHING_OFFSET

    if 0 <= e < MAX_GRID_SIZE and 0 <= n < MAX_GRID_SIZE:
        major_index = int(e / MAJOR_GRID_SQ_SIZE) + GRID_SIZE * int(n / MAJOR_GRID_SQ_SIZE)
        e = e % MAJOR_GRID_SQ_SIZE
        n = n % MAJOR_GRID_SQ_SIZE
        minor_index = int(e / MINOR_GRID_SQ_SIZE) + GRID_SIZE * int(n / MINOR_GRID_SQ_SIZE)
        sq = GRID_SQ_LETTERS[major_index] + GRID_SQ_LETTERS[minor_index]

    else:
        raise FarFarAwayError(easting, northing)

    e = int(easting % MINOR_GRID_SQ_SIZE)
    n = int(northing % MINOR_GRID_SQ_SIZE)

    # special cases
    ff = form.upper()
    if ff == 'TRAD':
        ff = 'SS EEE NNN'
    elif ff == 'GPS':
        ff = 'SS EEEEE NNNNN'
    elif ff == 'SS':
        return sq

    m = re.match(r'S{1,2}(\s*)(E{1,5})(\s*)(N{1,5})', ff)
    if m is None:
        raise FaultyFormError(form)

    (space_a, e_spec, space_b, n_spec) = m.group(1, 2, 3, 4)
    e = int(e/10**(5-len(e_spec)))
    n = int(n/10**(5-len(n_spec)))

    return sq \
        + space_a + '{0:0{1}d}'.format(e, len(e_spec)) \
        + space_b + '{0:0{1}d}'.format(n, len(n_spec))


def parse_grid(*grid_elements, **kwargs):
    """Parse a grid reference from a range of inputs.

The parse_grid routine extracts a (easting, northing) pair from a
string, or a list of arguments, representing a grid reference.  The pair
returned are in units of metres from the false origin of the grid.

The arguments should be in one of the following three forms

- A single string representing a grid reference

    >>> parse_grid("TA 123 678")
    (512300, 467800)
    >>> parse_grid("TA 12345 67890")
    (512345, 467890)

    The string can also refer to 100km, 10km, 1km, or even 10m squares:

    >>> parse_grid('TA')
    (500000, 400000)
    >>> parse_grid('TA15')
    (510000, 450000)
    >>> parse_grid('TA 12 56')
    (512000, 456000)
    >>> parse_grid('TA 1234 5678')
    (512340, 456780)

    The spaces are optional in all cases:

    >>> parse_grid(" TA 123 678 ")
    (512300, 467800)
    >>> parse_grid(" TA123 678 ")
    (512300, 467800)
    >>> parse_grid(" TA 123678")
    (512300, 467800)
    >>> parse_grid("TA123678")
    (512300, 467800)
    >>> parse_grid("TA1234567890")
    (512345, 467890)

    Here are some more extreme examples:

    >>> parse_grid('SV9055710820') # St Marys lifeboat station
    (90557, 10820)
    >>> parse_grid('HU4795841283') # Lerwick lifeboat station
    (447958, 1141283)
    >>> parse_grid('WE950950') # At sea, off the Scillies
    (-5000, -5000)

    Note in the last one that we are "off" the grid proper.  This lets
    you work with "pseudo-grid-references" like these:

    >>> parse_grid('XD 61191 50692') # St Peter Port the Channel Islands
    (361191, -49308)
    >>> parse_grid('MC 03581 16564') # Rockall
    (-296419, 916564)


- A two or three element list representing a grid reference

    >>> parse_grid('TA', 0, 0)
    (500000, 400000)
    >>> parse_grid('TA', 123, 678)
    (512300, 467800)
    >>> parse_grid('TA', 12345, 67890)
    (512345, 467890)
    >>> parse_grid('TA', '123 678')
    (512300, 467800)
    >>> parse_grid('TA', '12345 67890')
    (512345, 467890)
    >>> parse_grid('TA', '1234567890')
    (512345, 467890)

    Or even just two numbers (primarily included for testing purposes).
    Note that this allows floats, and that the results will come back as
    floats

    >>> parse_grid(314159, 271828)
    (314159.0, 271828.0)
    >>> parse_grid('314159 271828')
    (314159.0, 271828.0)
    >>> parse_grid(231413.123, 802143.456)
    (231413.123, 802143.456)

    If you are processing grid references from some external data source
    beware that if you use a list with bare numbers you may lose any
    leading zeros for grid references close to the SW corner of a grid
    square.  This can lead to some ambiguity.  Either make the numbers
    into strings to preserve the leading digits or supply a keyword
    argument ``figs`` to define how many figures are supposed to be in
    each easting and northing.  Like this:

    >>> parse_grid('TA', 123, 8)
    (512300, 400800)
    >>> parse_grid('TA', 123, 81, figs=5)
    (500123, 400081)

    The default setting of figs is 3, which assumes you are using
    hectometres as in a traditional grid reference. The maximum is 5 and
    the minimum is the length of the longer of easting or northing.

- A string or a list representing a map and a local grid reference,
  corresponding to the following examples:

    >>> parse_grid('176/224711') # Caesar's Camp
    (522400, 171100)
    >>> parse_grid(176, 224, 711)
    (522400, 171100)
    >>> parse_grid('A:164/352194') # Charlbury Station
    (435200, 219400)
    >>> parse_grid('B:OL43E/914701') # map Chesters Bridge
    (391400, 570100)
    >>> parse_grid('B:OL43E 914 701') # map Chesters Bridge
    (391400, 570100)
    >>> parse_grid('B:OL43E', '914701') # map 2-arg Chesters Bridge
    (391400, 570100)
    >>> parse_grid('B:OL43E', 914, 701) # map 3-arg Chesters Bridge
    (391400, 570100)
    >>> parse_grid(164, 513, 62) # Carfax
    (451300, 206200)
    >>> parse_grid('B:119/480103') # map with dual name
    (448000, 110300)
    >>> parse_grid('B:OL3/480103') # map with dual name
    (448000, 110300)
    >>> parse_grid('B:309S.a 26432 34013') # inset on B:309
    (226432, 534013)
    >>> parse_grid('B:368W', 723, 112) # 3-arg, dual name
    (272300, 711200)
    >>> parse_grid('B:OL47W', 723, 112) # 3-arg, dual name
    (272300, 711200)

    or finally just a sheet name;  this will show the SW corner:

    >>> parse_grid('A:82')
    (195000, 530000)

    with the usual rule about assuming you meant Landrangers:

    >>> parse_grid(161)
    (309000, 205000)

    A map sheet with a grid ref that does not actually coincide will
    raise a SheetMismatchError error

    >>> parse_grid('176/924011') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    SheetMismatchError: Grid point (592400, 201100) is not on sheet A:176

    A map sheet that does not exist will raise an UndefinedSheetError error

    >>> parse_grid('B:999/924011') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    UndefinedSheetError: Sheet B:999 is not known here.

If there's no matching input then a GarbageError error is raised.

    >>> parse_grid('Somewhere in London') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    GarbageError: I can't read a grid reference from this -> Somewhere in London

"""

    try:
        figs = int(kwargs['figs'])
    except (KeyError, ValueError):
        figs = 3

    if len(grid_elements) == 3:
        sq, ee, nn = grid_elements
        figs = min(5, max(figs, len(str(ee)), len(str(nn))))
        grid_string = '{0} {1:0{3}d} {2:0{3}d}'.format(sq, int(ee), int(nn), figs)
    else:
        grid_string = ' '.join(str(x).strip() for x in grid_elements)

    # normal case : TQ 123 456 etc
    offsets = _get_grid_square_offsets(grid_string)
    if offsets is not None:
        if len(grid_string) == 2:   # ie must have been just a valid square
            return offsets

        en_tuple = _get_eastings_northings(grid_string)
        if en_tuple is not None:
            return (en_tuple[0]+offsets[0], en_tuple[1]+offsets[1])

    # just a pair of numbers perhaps?
    try:
        grid_elements = tuple(float(x) for x in grid_string.split())
    except ValueError:
        pass
    else:
        if len(grid_elements) == 2:
            return grid_elements

    # probably now a sheet name rather than a SQ number
    # so hand off to the sheet reference parser
    return _get_easting_northing_from_sheet_reference(grid_string)


def _get_easting_northing_from_sheet_reference(possible_map_gr):
    '''Find a grid reference from a sheet number (with optional local GR)'''

    # so lets try to decompose the string version of the input
    ok = re.match(r'^([A-Z]:)?([0-9NEWSOL/]+?)(\.[a-z]+)?(?:[ -/.]([ 0-9]+))?$', possible_map_gr)
    if not ok:
        raise GarbageError(possible_map_gr)

    (prefix, sheet_number, suffix, numbers) = ok.groups()

    if prefix is None:
        sheet = "A:" + sheet_number  # default to Landranger sheets
    else:
        sheet = prefix + sheet_number

    if suffix is not None:
        sheet = sheet + suffix

    s = get_sheet(sheet)

    if s is None:
        raise UndefinedSheetError(sheet)

    easting = s.bbox[0][0]   # start with SW corner
    northing = s.bbox[0][1]

    if numbers is not None:
        (e, n) = _get_eastings_northings(numbers)
        easting = easting + (e - easting) % MINOR_GRID_SQ_SIZE
        northing = northing + (n - northing) % MINOR_GRID_SQ_SIZE
        if _winding_number(easting, northing, s.polygon) == 0:
            raise SheetMismatchError(sheet, easting, northing)

    return (easting, northing)


def _get_grid_square_offsets(sq):
    """Get (e, n) for ll corner of a grid square

    >>> _get_grid_square_offsets('SV')
    (0, 0)

    >>> _get_grid_square_offsets('TQ 345 452')
    (500000, 100000)

    """

    if len(sq) < 2:
        return None

    a = GRID_SQ_LETTERS.find(sq[0].upper())
    if a < 0:
        return None

    b = GRID_SQ_LETTERS.find(sq[1].upper())
    if b < 0:
        return None

    (Y, X) = divmod(a, GRID_SIZE)
    (y, x) = divmod(b, GRID_SIZE)

    return (
        MAJOR_GRID_SQ_SIZE * X - MAJOR_GRID_SQ_EASTING_OFFSET + MINOR_GRID_SQ_SIZE * x,
        MAJOR_GRID_SQ_SIZE * Y - MAJOR_GRID_SQ_NORTHING_OFFSET + MINOR_GRID_SQ_SIZE * y
    )


def _get_eastings_northings(s):
    """Extract easting and northing from GR string.

    >>> _get_eastings_northings(' 12345 67890')
    (12345, 67890)
    >>> _get_eastings_northings(' 234 567')
    (23400, 56700)
    """
    t = re.findall(r'(\d+)', s)
    if len(t) == 2:
        (e, n) = t
    elif len(t) == 1:
        gr = t[0]
        f = len(gr)
        if f in [2, 4, 6, 8, 10]:
            f = int(f/2)
            e, n = (gr[:f], gr[f:])
        else:
            return None
    else:
        return None

    figs = min(5, max(len(e), len(n)))
    return (int(e)*10**(5-figs), int(n)*10**(5-figs))


def sheet_keys(easting, northing, series='ABCHJ'):
    """Return a list of map sheet keys that show the (easting, northing)
    point given.

    The optional argument "series" controls which maps are included in
    the list.  The default is to include maps from all defined series.

    >>> print(' '.join(sheet_keys(438710.908, 114792.248, series='AB')))
    A:196 B:OL22E

    Currently the series included are:

    A:
        OS Landranger 1:50000 maps

    B:
        OS Explorer 1:25000 maps (some of these are designated as "Outdoor Leisure" maps)

    C:
        OS Seventh Series One-Inch 1:63360 maps

    H:
        Harvey British Mountain maps - mainly at 1:40000

    J:
        Harvey Super Walker maps - mainly at 1:25000

    Note that the numbers returned for the Harvey maps have been
    invented for the purposes of this module.  They do not appear on the
    maps themselves; instead the maps have titles.

    You can use the numbers returned as an index to the maps data to
    find the appropriate title.  To get a sheet object use:
    get_sheet(key)

    >>> print(get_sheet(sheet_keys(314159, 271828, series='C')[0]).title)
    Montgomery and Llandrindod Wells

    >>> print(' '.join(sheet_keys(314159, 271828)))
    A:136 A:148 B:200E B:214E C:128

    You can restrict the list to certain series.  So if you only want
    Explorer maps use: series='B', and if you want only Explorers and
    Landrangers use: series='AB', and so on.

    >>> print(''.join(sheet_keys(651537, 313135, series='A')))
    A:134

    If the (easting, northing) pair is not covered by any map sheet
    you'll get an empty list

    >>> sheet_keys(0, 0)
    []

    """

    sheets = list()
    for (k, m) in map_locker.items():
        if k[0] not in series:  # initial letter of key is series letter
            continue

        if m.bbox[0][0] <= easting < m.bbox[1][0]:
            if m.bbox[0][1] <= northing < m.bbox[1][1]:
                if _winding_number(easting, northing, m.polygon) != 0:
                    sheets.append(k)

    return sorted(sheets)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
