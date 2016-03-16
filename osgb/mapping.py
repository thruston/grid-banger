"""Data for OSGB and other walkers maps in England, Wales, Scotland, and Isle of Man.

Toby Thurston -- 15 Mar 2016 
"""

import pkgutil
maps = eval(pkgutil.get_data("osgb", "mapping.data"))

def sheet_list(easting, northing, series='ABCHJ'):
    """Return a list of map sheets that show the (easting, northing) point given.

    >>> sheet_list(314159, 271828)
    ['A:136', 'A:148', 'B:200E', 'B:214E', 'C:128']

    >>> sheet_list(651537, 313135, series='A')
    ['A:134']
    """

    sheets = list()
    for (k, m) in maps.items():
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
    w = 0;
    for i in range(len(poly)-1):
        if poly[i][1] <= y:
            if poly[i+1][1] > y and is_left(x, y, poly[i], poly[i+1]) > 0:
                w += 1
        else:
            if poly[i+1][1] <= y and is_left(x, y, poly[i], poly[i+1]) < 0:
                w -= 1
    return w

def resolve_grid(sheet, local_easting, local_northing):
    # NB we need the bbox corner so that it is left and below all points on the map
    ll_corner = maps[sheet]['bbox'][0]  

    easting  = ll_corner[0] + (local_easting  - ll_corner[0]) % 100000
    northing = ll_corner[1] + (local_northing - ll_corner[1]) % 100000

    if 0 == winding_number(easting, northing, maps[sheet]['polygon']):
        print("Grid reference is not on sheet {}".format(sheet), file=sys.stderr)
        return None

    return (easting, northing)

def is_known_sheet(sheet):
    """Is "sheet" defined in our data?
    
    >>> is_known_sheet('A:1')
    True

    >>> is_known_sheet('')
    False

    """
    return sheet in maps

if __name__ == "__main__":
    import doctest
    doctest.testmod()
