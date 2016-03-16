"""Parse and format OSGB grid reference strings

Toby Thurston -- 14 Mar 2016
"""

import re
import sys
import math
from osgb.mapping import map_locker

__all__ = ['format_grid', 'parse_grid', 'sheet_list']

GRID_SQ_LETTERS               = 'VWXYZQRSTULMNOPFGHJKABCDE'
GRID_SIZE                     = int(math.sqrt(len(GRID_SQ_LETTERS)))
MINOR_GRID_SQ_SIZE            = 100000
MAJOR_GRID_SQ_SIZE            = GRID_SIZE * MINOR_GRID_SQ_SIZE
MAJOR_GRID_SQ_EASTING_OFFSET  = 2 * MAJOR_GRID_SQ_SIZE
MAJOR_GRID_SQ_NORTHING_OFFSET = 1 * MAJOR_GRID_SQ_SIZE
MAX_GRID_SIZE                 = MINOR_GRID_SQ_SIZE * len(GRID_SQ_LETTERS)

def sheet_list(easting, northing, series='ABCHJ'):
    """Return a list of map sheets that show the (easting, northing) point given.

    The optional argument "series" controls which maps are included in the 
    list.  The default is to include maps from all defined series.

    >>> sheet_list(438710.908, 114792.248, series='AB')
    ['A:196', 'B:OL22E']

    Currently the series included are:

    A: OS Landranger 1:50000 maps
    B: OS Explorer 1:25000 maps (some of these are designated as `Outdoor Leisure' maps)
    C: OS Seventh Series One-Inch 1:63360 maps
    H: Harvey British Mountain maps - mainly at 1:40000
    J: Harvey Super Walker maps - mainly at 1:25000

    so if you only want Explorer maps use: series='B', and if you
    want only Explorers and Landrangers use: series='AB', and so on. 

    Note that the numbers returned for the Harvey maps have been invented
    for the purposes of this module.  They do not appear on the maps
    themselves; instead the maps have titles.  You can use the numbers
    returned as an index to the maps data to find the appropriate title.

    >>> sheet_list(314159, 271828)
    ['A:136', 'A:148', 'B:200E', 'B:214E', 'C:128']

    >>> sheet_list(651537, 313135, series='A')
    ['A:134']
    """

    sheets = list()
    for (k, m) in map_locker.items():
        if k[0] not in series:
            continue

        if m['bbox'][0][0] <= easting < m['bbox'][1][0]:
            if m['bbox'][0][1] <= northing < m['bbox'][1][1]:
                if 0 != winding_number(easting, northing, m['polygon']):
                    sheets.append(k)

    return sorted(sheets)

# is $pt left of $a--$b?
def is_left(x, y, a, b):
    return ( (b[0] - a[0]) * (y - a[1]) - (x - a[0]) * (b[1] - a[1]) )

# adapted from http://geomalgorithms.com/a03-_inclusion.html
def winding_number(x, y, poly):
    w = 0
    for i in range(len(poly)-1):
        if poly[i][1] <= y:
            if poly[i+1][1] > y and is_left(x, y, poly[i], poly[i+1]) > 0:
                w += 1
        else:
            if poly[i+1][1] <= y and is_left(x, y, poly[i], poly[i+1]) < 0:
                w -= 1
    return w


def format_grid(easting, northing=None, form='SS EEE NNN', maps=None):
    """Formats an (easting, northing) pair into traditional grid reference.

    This routine formats an (easting, northing) pair into a traditional
    grid reference with two letters and two sets of three numbers, like this
    `SU 387 147'.  

    >>> format_grid(438710.908, 114792.248)
    'SU 387 147'

    If you want the individual components, apply split() to it.

    >>> format_grid(438710.908, 114792.248).split()
    ['SU', '387', '147']

    The format grid routine takes three optional keyword arguments to control the
    form of grid reference returned.  This should be a hash reference with
    one or more of the keys shown below (with the default values).

    >>> format_grid(438710.908, 114792.248, form='SS EEE NNN')
    'SU 387 147'
    >>> format_grid(438710.908, 114792.248, form='SS EEEEE NNNNN')
    'SU 38710 14792'

    Note that rather than being rounded, the easting and northing are truncated
    (as the OS system demands), so the grid reference refers to the lower left
    corner of the relevant square.  The system is described below the legend on
    all OS Landranger maps.

    An optional keyword argument "form" controls the format of the grid reference.  

    >>> format_grid(438710.908, 114792.248, form='SS')
    'SU'
    >>> format_grid(438710.908, 114792.248, form='SSEN')
    'SU31'
    >>> format_grid(438710.908, 114792.248, form='SSEENN')
    'SU3814'
    >>> format_grid(438710.908, 114792.248, form='SSEEENNN')
    'SU387147'
    >>> format_grid(438710.908, 114792.248, form='SSEEEENNNN')
    'SU38711479'
    >>> format_grid(438710.908, 114792.248, form='SSEEEEENNNNN')
    'SU3871014792'
    >>> format_grid(438710.908, 114792.248, form='SS EN')
    'SU 31'
    >>> format_grid(438710.908, 114792.248, form='SS EE NN')
    'SU 38 14'
    >>> format_grid(438710.908, 114792.248, form='SS EEE NNN')
    'SU 387 147'
    >>> format_grid(438710.908, 114792.248, form='SS EEEE NNNN')
    'SU 3871 1479'
    >>> format_grid(400010.908, 114792.248, form='SS EEEEE NNNNN')
    'SU 00010 14792'

    You can't leave out the SS, you can't have N before E, and there must be
    the same number of Es and Ns.

    There are two other special formats:

    >>> format_grid(438710.908, 114792.248, form='TRAD')
    'SU 387 147'
    >>> format_grid(438710.908, 114792.248, form='GPS')
    'SU 38710 14792'

    The format can be given as upper case or lower case or a mixture.  
    >>> format_grid(438710.908, 114792.248, form='trad')
    'SU 387 147'

    """
    if northing is None:
        (easting, northing) = easting
    
    sq = grid_to_sq(easting,northing)
    if sq is None:
        print("Too far off the grid: easting northing", file=sys.stderr)
        return None

    e = int(easting  % MINOR_GRID_SQ_SIZE)
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
        print("Invalid form: {}".format(form), file=sys.stderr)
        return None

    (space_a, e_spec, space_b, n_spec) = m.group(1,2,3,4)
    e = int(e/10**(5-len(e_spec)))
    n = int(n/10**(5-len(n_spec)))

    return sq + space_a + '{0:0{1}d}'.format(e, len(e_spec)) + space_b + '{0:0{1}d}'.format(n, len(n_spec))

def parse_grid(*grid_elements, figs=3):
    """Parse a grid reference from a range of inputs.

    The parse_grid routine extracts a (easting, northing) pair from a
    string, or a list of arguments, representing a grid reference.  The pair
    returned are in units of metres from the false origin of the grid.

    The arguments should be in one of the following three forms

    •   A single string representing a grid reference

        >>> parse_grid("TA 123 678")
        (512300, 467800)

        >>> parse_grid("TA 12345 67890")
        (512345, 467890)

        You can also refer to 100km, 10km, 1km, or even 10m squares:

        >>> parse_grid('TA')
        (500000, 400000)

        >>> parse_grid('TA15')
        (510000, 450000)

        >>> parse_grid('TA 12 56')
        (512000, 456000)

        >>> parse_grid('TA 1234 5678')
        (512340, 456780)

        The spaces are optional in all cases.

        >>> parse_grid("TA123678")
        (512300, 467800)

        >>> parse_grid("TA1234567890")
        (512345, 467890)

        Here are some more extreme examples:

        St Marys lifeboat station
        >>> parse_grid('SV9055710820')
        (90557, 10820)

        Lerwick lifeboat station
        >>> parse_grid('HU4795841283')
        (447958, 1141283)

        At sea, off the Scillies
        >>> parse_grid('WE950950')
        (-5000, -5000)

        Note in the last one that we are "off" the grid proper.  This lets you work
        with "pseudo-grid-references" like these:
        
        St Peter Port the Channel Islands
        >>> parse_grid('XD 61191 50692')
        (361191, -49308)
        
        Rockall 
        >>> parse_grid('MC 03581 16564')
        (-296419, 916564)


     •  A two or three element list representing a grid reference

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

        Or even just two numbers (primarily included for testing purposes)
        >>> parse_grid(314159, 271828)
        (314159.0, 271828.0)

        If you are processing grid references from some external data source
        beware that if you use a list with bare numbers you may lose any leading
        zeros for grid references close to the SW corner of a grid square.  This
        can lead to some ambiguity.  Either make the numbers into strings to
        preserve the leading digits or supply a hash of options as a fourth
        argument with the `figs' option to define how many figures are supposed
        to be in each easting and northing.  Like this:

        >>> parse_grid('TA', 123, 8)
        (512300, 400800)
        >>> parse_grid('TA', 123, 81, figs=5)
        (500123, 400081)

        The default setting of figs is 3, which assumes you are using
        hectometres as in a traditional grid reference. The maximum is 5
        and the minimum is the length of the longer of easting or northing.

    •   A string or a list representing a map and a local grid reference, 
        corresponding to the following examples:

        Caesar's Camp
        >>> parse_grid('176/224711')
        (522400, 171100)

        Charlbury Station
        >>> parse_grid('A:164/352194')
        (435200, 219400)

        map Chesters Bridge
        >>> parse_grid('B:OL43E/914701')
        (391400, 570100)

        map Chesters Bridge
        >>> parse_grid('B:OL43E 914 701')
        (391400, 570100)

        map 2-arg Chesters Bridge
        >>> parse_grid('B:OL43E','914701')
        (391400, 570100)

        map 3-arg Chesters Bridge
        >>> parse_grid('B:OL43E',914,701)
        (391400, 570100)

        Carfax
        >>> parse_grid(164,513,62)
        (451300, 206200)

        map with dual name
        >>> parse_grid('B:119/OL3/480103')
        (448000, 110300)

        inset on B:309
        >>> parse_grid('B:309S.a 26432 34013')
        (226432, 534013)

        3-arg, dual name
        >>> parse_grid('B:368/OL47W', 723, 112)
        (272300, 711200)

    """

    easting = 0
    northing = 0

    if len(grid_elements) == 3:
        sq, ee, nn = grid_elements
        figs = min(5,max(figs, len(str(ee)), len(str(nn))))
        s = '{0} {1:0{3}d} {2:0{3}d}'.format(sq, int(ee), int(nn), figs)
    else:
        s = ' '.join(str(x) for x in grid_elements)

    # normal case : TQ 123 456 etc
    offsets = get_grid_square_offsets(s)
    if offsets is not None:
        if len(s) == 2:
            return offsets

        (e, n) = get_eastings_northings(s[2:])
        return (e+offsets[0], n+offsets[1])

    # sheet id instead of grid sq
    m = re.match(r'([A-Z0-9:./]+)\D+(\d+\D*\d+)', s, re.IGNORECASE)
    if m is not None:

        sheet, numbers = m.group(1,2)

        # allow Landranger sheets with no prefix
        if 'A:' + sheet in map_locker:
            sheet = 'A:' + sheet

        if sheet in map_locker:
            map = map_locker[sheet] 
            ll_corner = map['bbox'][0]  
            (e, n) = get_eastings_northings(numbers)
            easting  = ll_corner[0] + (e - ll_corner[0]) % MINOR_GRID_SQ_SIZE
            northing = ll_corner[1] + (n - ll_corner[1]) % MINOR_GRID_SQ_SIZE
            if 0 == winding_number(easting, northing, map['polygon']):
                print("Grid reference is not on sheet {}".format(sheet), file=sys.stderr)
                print("bbox: {}".format(' '.join(str(x) for x in map['bbox'])), file=sys.stderr)
                return None

            return (easting, northing)

    # just a pair of numbers
    try:
        (easting, northing) = s.split()
        if is_number(easting) and is_number(northing):
            return (float(easting), float(northing))
    except ValueError:
        pass

    print('{} does not look like a grid reference to me'.format(s), file=sys.stderr)
    return None

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def grid_to_sq(e, n):
    """Return major grid square identifier for (e, n) pair

    >>> grid_to_sq(314159, 271828)
    'SO'
    >>> grid_to_sq(0, 0)
    'SV'
    >>> grid_to_sq(432800,1250000)
    'HP'
    >>> grid_to_sq(-5,-5)
    'WE'

    """
    
    e += MAJOR_GRID_SQ_EASTING_OFFSET
    n += MAJOR_GRID_SQ_NORTHING_OFFSET

    if 0 <= e <  MAX_GRID_SIZE and 0 <= n < MAX_GRID_SIZE:
        major_index = int(e/MAJOR_GRID_SQ_SIZE) + GRID_SIZE * int(n/MAJOR_GRID_SQ_SIZE)
        e = e % MAJOR_GRID_SQ_SIZE
        n = n % MAJOR_GRID_SQ_SIZE
        minor_index = int(e/MINOR_GRID_SQ_SIZE) + GRID_SIZE * int(n/MINOR_GRID_SQ_SIZE)
        return GRID_SQ_LETTERS[major_index] + GRID_SQ_LETTERS[minor_index]

    return None

def get_grid_square_offsets(sq):
    """Get (e,n) for ll corner of a grid square

    >>> get_grid_square_offsets('SV')
    (0, 0)

    >>> get_grid_square_offsets('TQ 345 452')
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
        MAJOR_GRID_SQ_SIZE * X - MAJOR_GRID_SQ_EASTING_OFFSET  + MINOR_GRID_SQ_SIZE * x,
        MAJOR_GRID_SQ_SIZE * Y - MAJOR_GRID_SQ_NORTHING_OFFSET + MINOR_GRID_SQ_SIZE * y
    )

def get_eastings_northings(s):
    """Extract easting and northing from GR string.

    >>> get_eastings_northings(' 12345 67890')
    (12345, 67890)
    >>> get_eastings_northings(' 234 567')
    (23400, 56700)
    """
    numbers = ''.join(x for x in s if x.isdigit())
    figs = len(numbers)
    if figs not in [2,4,6,8,10]:
        return None

    figs = int(figs/2)
    e = int(numbers[0:figs])*10**(5-figs)
    n = int(numbers[figs: ])*10**(5-figs)
    return (e, n)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
