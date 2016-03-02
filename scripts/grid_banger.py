# coding=utf-8

"""
 A class to implement OSGB reformatting and conversion

 OSGB_Grid_Point represents a location on a map in Great Britain 
 The constructor allows grid references in various forms, 
 including OSGB lat/lon and WGS84 lat/lon (and later possibly place names...)

 Toby Thurston -- 15 May 2014 
"""

import math
import re

# Some constants for the maps
LR_sheets = {
    1: (429000, 1179000),
    2: (433000, 1156000),
    3: (414000, 1147000),
    4: (420000, 1107000),
    5: (340000, 1020000),
    6: (321000, 996000),
    7: (315000, 970000),
    8: (117000, 926000),
    9: (212000, 940000),
    10: (252000, 940000),
    11: (292000, 929000),
    12: (300000, 939000),
    13: ( 95000, 903000),
    14: (105000, 886000),
    15: (196000, 900000),
    16: (236000, 900000),
    17: (276000, 900000),
    18: ( 69000, 863000),
    19: (174000, 860000),
    20: (214000, 860000),
    21: (254000, 860000),
    22: ( 57000, 823000),
    23: (113000, 836000),
    24: (150000, 830000),
    25: (190000, 820000),
    26: (230000, 820000),
    27: (270000, 830000),
    28: (310000, 833000),
    29: (345000, 830000),
    30: (377000, 830000),
    31: ( 50000, 783000),
    32: (130000, 800000),
    33: (170000, 790000),
    34: (210000, 780000),
    35: (250000, 790000),
    36: (285000, 793000),
    37: (325000, 793000),
    38: (365000, 790000),
    39: (120000, 770000),
    40: (160000, 760000),
    41: (200000, 750000),
    42: (240000, 750000),
    43: (280000, 760000),
    44: (320000, 760000),
    45: (360000, 760000),
    46: ( 92000, 733000),
    47: (120000, 733000),
    48: (120000, 710000),
    49: (160000, 720000),
    50: (200000, 710000),
    51: (240000, 720000),
    52: (270000, 720000),
    53: (294000, 720000),
    54: (334000, 720000),
    55: (164000, 680000),
    56: (204000, 682000),
    57: (244000, 682000),
    58: (284000, 690000),
    59: (324000, 690000),
    60: (110000, 640000),
    61: (131000, 662000),
    62: (160000, 640000),
    63: (200000, 642000),
    64: (240000, 645000),
    65: (280000, 650000),
    66: (316000, 650000),
    67: (356000, 650000),
    68: (157000, 600000),
    69: (175000, 613000),
    70: (215000, 605000),
    71: (255000, 605000),
    72: (280000, 620000),
    73: (320000, 620000),
    74: (357000, 620000),
    75: (390000, 620000),
    76: (195000, 570000),
    77: (235000, 570000),
    78: (275000, 580000),
    79: (315000, 580000),
    80: (355000, 580000),
    81: (395000, 580000),
    82: (195000, 530000),
    83: (235000, 530000),
    84: (265000, 540000),
    85: (305000, 540000),
    86: (345000, 540000),
    87: (367000, 540000),
    88: (407000, 540000),
    89: (290000, 500000),
    90: (317000, 500000),
    91: (357000, 500000),
    92: (380000, 500000),
    93: (420000, 500000),
    94: (460000, 485000),
    95: (213000, 465000),
    96: (303000, 460000),
    97: (326000, 460000),
    98: (366000, 460000),
    99: (406000, 460000),
    100: (446000, 460000),
    101: (486000, 460000),
    102: (326000, 420000),
    103: (360000, 420000),
    104: (400000, 420000),
    105: (440000, 420000),
    106: (463000, 420000),
    107: (500000, 420000),
    108: (320000, 380000),
    109: (360000, 380000),
    110: (400000, 380000),
    111: (430000, 380000),
    112: (470000, 385000),
    113: (510000, 386000),
    114: (220000, 360000),
    115: (240000, 345000),
    116: (280000, 345000),
    117: (320000, 340000),
    118: (360000, 340000),
    119: (400000, 340000),
    120: (440000, 350000),
    121: (478000, 350000),
    122: (518000, 350000),
    123: (210000, 320000),
    124: (250000, 305000),
    125: (280000, 305000),
    126: (320000, 300000),
    127: (360000, 300000),
    128: (400000, 308000),
    129: (440000, 310000),
    130: (480000, 310000),
    131: (520000, 310000),
    132: (560000, 310000),
    133: (600000, 310000),
    134: (617000, 290000),
    135: (250000, 265000),
    136: (280000, 265000),
    137: (320000, 260000),
    138: (345000, 260000),
    139: (385000, 268000),
    140: (425000, 270000),
    141: (465000, 270000),
    142: (504000, 274000),
    143: (537000, 274000),
    144: (577000, 270000),
    145: (200000, 220000),
    146: (240000, 225000),
    147: (270000, 240000),
    148: (310000, 240000),
    149: (333000, 228000),
    150: (373000, 228000),
    151: (413000, 230000),
    152: (453000, 230000),
    153: (493000, 234000),
    154: (533000, 234000),
    155: (573000, 234000),
    156: (613000, 250000),
    157: (165000, 201000),
    158: (189000, 190000),
    159: (229000, 185000),
    160: (269000, 205000),
    161: (309000, 205000),
    162: (349000, 188000),
    163: (389000, 190000),
    164: (429000, 190000),
    165: (460000, 195000),
    166: (500000, 194000),
    167: (540000, 194000),
    168: (580000, 194000),
    169: (607000, 210000),
    170: (269000, 165000),
    171: (309000, 165000),
    172: (340000, 155000),
    173: (380000, 155000),
    174: (420000, 155000),
    175: (460000, 155000),
    176: (495000, 160000),
    177: (530000, 160000),
    178: (565000, 155000),
    179: (603000, 133000),
    180: (240000, 112000),
    181: (280000, 112000),
    182: (320000, 130000),
    183: (349000, 115000),
    184: (389000, 115000),
    185: (429000, 116000),
    186: (465000, 125000),
    187: (505000, 125000),
    188: (545000, 125000),
    189: (585000, 115000),
    190: (207000, 87000),
    191: (247000, 72000),
    192: (287000, 72000),
    193: (310000, 90000),
    194: (349000, 75000),
    195: (389000, 75000),
    196: (429000, 76000),
    197: (469000, 90000),
    198: (509000, 97000),
    199: (549000, 94000),
    200: (175000, 50000),
    201: (215000, 47000),
    202: (255000, 32000),
    203: (132000, 11000),
    204: (172000, 14000),
}

LR_sheet_size = 40000
Great_sq_size = 500000
Small_sq_size = 100000
Grid_sq_letters = 'VWXYZQRSTULMNOPFGHJKABCDE'
Trad_grid_pat = re.compile(r'([{0}][{0}])\s?(\d{{3}})\s?(\d{{3}})'.format(Grid_sq_letters))
Long_grid_pat = re.compile(r'([{0}][{0}])\s?(\d{{5}})\s?(\d{{5}})'.format(Grid_sq_letters))

# useful routines

def _parse_grid_sq(sq):
    '''Return easting and northing from a grid SQ pair.

    >>> _parse_grid_sq('SV')
    (0, 0)
    >>> _parse_grid_sq('TQ')
    (500000, 100000)
    >>> _parse_grid_sq('NH')
    (200000, 800000)
    '''

    i = Grid_sq_letters.index(sq[0])
    easting  = Great_sq_size * (i%5-2)
    northing = Great_sq_size * (i//5-1)

    i = Grid_sq_letters.index(sq[1])
    easting  += Small_sq_size * (i%5)
    northing += Small_sq_size * (i//5)

    return (easting, northing)


def _lr_to_full_grid(corner, point):
    '''Make [east|north]ing of corner + [east|north]ing on map into metres-from-Newlyn.'''

    metres_from_corner = point - (corner % Small_sq_size)
    if (metres_from_corner < 0):
        metres_from_corner += Small_sq_size

    if 0 < metres_from_corner < LR_sheet_size:
        return corner+metres_from_corner
    else:
        raise RuntimeError('Grid reference is not on sheet')

def _ll_to_grid(lat,lon):
    '''Transform lat/lon to easting/northing assuming OSGB geoids.

    This should work with readings from OS maps.  For GoogleEarth or your GPS
    transform the lat/lon from WGS84 to OSGB36/Airy first.
    >>> '{0:.6f} {1:.6f}'.format(*_ll_to_grid(49,-2))
    '400000.000000 -100000.000000'
    >>> '{0:.6f} {1:.6f}'.format(*_ll_to_grid(52,-2))
    '400000.000000 233553.731342'
    '''

    # OSGB36 / Airy parms
    OSGB_MAJOR_AXIS  = 6377563.396
    OSGB_MINOR_AXIS  = 6356256.910
    # constants for OSGB mercator projection
    ORIGIN_LONGITUDE   = -2
    ORIGIN_LATITUDE    = 49 
    ORIGIN_EASTING     =  400000
    ORIGIN_NORTHING    = -100000
    CONVERGENCE_FACTOR = 0.9996012717

    (a,b) = (OSGB_MAJOR_AXIS,OSGB_MINOR_AXIS)
    n = (a-b)/(a+b)
    
    sin_lat = math.sin(math.radians(lat))
    cos_lat = math.cos(math.radians(lat))
    sin_lon = math.sin(math.radians(lon))
    cos_lon = math.cos(math.radians(lon))
    tan_lat = sin_lat / cos_lat
    tan2_lat = tan_lat * tan_lat
    tan4_lat = tan2_lat * tan2_lat

    ecc = math.sqrt(1 - (sin_lat-sin_lat*b/a)*(sin_lat+sin_lat*b/a))
    nu   = CONVERGENCE_FACTOR * a / ecc
    rho  = CONVERGENCE_FACTOR * b**2 / a * ecc**3
    eta2 = nu/rho - 1

    phi_plus  = math.radians(lat + ORIGIN_LATITUDE)
    phi_minus = math.radians(lat - ORIGIN_LATITUDE)

    M = CONVERGENCE_FACTOR * b * ( (1 + n * (1 + 5/4*n*(1 + n)))*phi_minus
         - 3*n*(1+n*(1+7/8*n))  * math.sin(  phi_minus) * math.cos(  phi_plus)
         + (15/8*n * (n*(1+n))) * math.sin(2*phi_minus) * math.cos(2*phi_plus)
         - 35/24*n**3           * math.sin(3*phi_minus) * math.cos(3*phi_plus)
           )

    I   = nu/2   * sin_lat * cos_lat
    II  = nu/24  * sin_lat * cos_lat**3 * (5 - tan2_lat + 9*eta2)
    III = nu/720 * sin_lat * cos_lat**5 * (61 - 58*tan2_lat + tan4_lat)

    IV  = nu*cos_lat
    V   = nu/6   * cos_lat**3 * (nu/rho - tan2_lat)
    VI  = nu/120 * cos_lat**5 * (5 - 18*tan2_lat + tan4_lat + 14*eta2 - 58*tan2_lat*eta2)

    lam = math.radians(lon - ORIGIN_LONGITUDE)
    north = ORIGIN_NORTHING + M +  I*lam**2 + II*lam**4 + III*lam**6
    east  = ORIGIN_EASTING      + IV*lam    +  V*lam**3 +  VI*lam**5
    return (east, north)

def _shift_ll_from_wgs84(lat,lon,elevation=0):

    # parameters for OSGB36 (negative because it is target)
    target_da = -573.604
    target_df = -0.119600236/10000
    target_dx = -375
    target_dy = +111
    target_dz = -431

    # parameters for WGS84
    reference_major_axis = 6378137.000
    reference_flattening = 1 / 298.257223563

    return _transform(lat, lon, elevation,
                      reference_major_axis, reference_flattening,
                      target_da, target_df,
                      target_dx, target_dy, target_dz)

def _shift_ll_into_WGS84(lat,lon,elevation=0):

    # parameters for OSGB36 (positive because it is source)
    target_da = +573.604
    target_df = +0.119600236/10000
    target_dx = +375
    target_dy = -111
    target_dz = +431

    # parameters for WGS84
    reference_major_axis = 6378137.000 - target_da
    reference_flattening = (1 / 298.257223563) - target_df

    return _transform(lat, lon, elevation,
                      reference_major_axis, reference_flattening,
                      target_da, target_df,
                      target_dx, target_dy, target_dz)

def _transform(lat, lon, elev, from_a, from_f, da, df, dx, dy, dz):

    sin_lat = math.sin(math.radians(lat))
    cos_lat = math.cos(math.radians(lat))
    sin_lon = math.sin(math.radians(lon))
    cos_lon = math.cos(math.radians(lon))

    b_a      = 1 - from_f
    e_sq     = from_f * (2-from_f)
    ecc      = 1 - e_sq*sin_lat*sin_lat
    secc     = math.sqrt(ecc)

    rn       = from_a / secc
    rm       = from_a * (1-e_sq) / (ecc*secc)

    d_lat = math.degrees( ( - dx*sin_lat*cos_lon
              - dy*sin_lat*sin_lon
              + dz*cos_lat
              + da*(rn*e_sq*sin_lat*cos_lat)/from_a
              + df*(rm/b_a + rn*b_a)*sin_lat*cos_lat
            ) / (rm + elev) )


    d_lon = math.degrees( ( - dx*sin_lon + dy*cos_lon) / ((rn+elev)*cos_lat) )

    d_elev = ( dx*cos_lat*cos_lon
             + dy*cos_lat*sin_lon
             + dz*sin_lat
             - da*from_a/rn
             + df*b_a*rn*sin_lat*sin_lat )

    (new_lat, new_lon, new_elev) = ( lat + d_lat, lon + d_lon, elev + d_elev)

    return (new_lat, new_lon, new_elev)


class lazy_property:
    def __init__(self, function):
        self.function = function
        self.__doc__  = function.__doc__

    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        else:
            value = self.function(instance)
            setattr(instance, self.function.__name__, value)
            return value


class OSGB_Grid_Point:
    '''A point on the British Ordnance Survey National Grid.'''

    near_enough = 100

    def __init__(self, *args, **keys):
        '''Create a point on the grid.

        Arguments: single grid ref string: TQ182675, 'SW 23144 23124', optional spaces
                   easting, northing (absolute meters from GRP)
                   sq,    grid (eeennn or eeeeennnnn)
                   sheet, grid (eeennn)
                   sheet (alone implies SW corner of it)

                   keys e, n, sq, grid, and sheet

                   if any keys are given, ignore any other args

        >>> OSGB_Grid_Point(100000,200000)
        OSGB_Grid_Point(e=100000,n=200000)
        >>> OSGB_Grid_Point(e=100000,n=200000)
        OSGB_Grid_Point(e=100000,n=200000)
        >>> print(OSGB_Grid_Point(sheet=176))
        495000 160000
        >>> p = OSGB_Grid_Point(sheet=25,grid='958212')
        >>> print('{}'.format(p))
        195800 821200
        >>> print('{:gps}'.format(p))
        NG 95800 21200
        >>> print('GR: {:trad}'.format(p))
        GR: NG 958 212
        >>> q = OSGB_Grid_Point(sq='NH', grid='106208')
        >>> print('{:gps}'.format(q))
        NH 10600 20800
        >>> r = OSGB_Grid_Point('TQ183698')
        >>> print('{:trad}'.format(r))
        TQ 183 698
        >>> s = OSGB_Grid_Point(sq='NH', grid='0961220897')
        >>> print('{0:trad} on {1}'.format(s, ', '.join(str(x) for x in s.sheets)))
        NH 096 208 on 25, 33
        >>> t = OSGB_Grid_Point(399994.6,419998.2)
        >>> print('{:trad}'.format(t))
        SD 999 199
        >>> t.sheets
        ['109']

        Read some from the map (top right corner of Landranger 43)
        >>> t = OSGB_Grid_Point(lat=57.0833333333, lon=-3.33333333333, geoid='OSGB36')
        >>> print('{:gps}'.format(t))
        NO 19195 99917

        Chobham in Surrey (using degrees + minutes)
        >>> t = OSGB_Grid_Point(lat=51+20/60, lon=-25/60, geoid='OSGB36'  )
        >>> print('{:trad}'.format(t))
        TQ 102 606

        >>> t = OSGB_Grid_Point(lat=51.41546, lon=-0.30036, elev=5 )
        >>> print('{:trad}'.format(t))
        TQ 182 698

        '''

        self.e = None
        self.n = None
        self.label = ''

        if len(keys) == 1 and 'sheet' in keys and keys['sheet'] in LR_sheets:
            self.e = LR_sheets[keys['sheet']][0]
            self.n = LR_sheets[keys['sheet']][1]

        elif len(keys) == 2 and 'e' in keys and 'n' in keys:
            self.e = int(keys['e'])
            self.n = int(keys['n'])

        elif len(keys) == 2 and 'sq' in keys and 'grid' in keys \
                            and keys['grid'].isdigit() \
                            and len(keys['grid']) == 6:

            offset = _parse_grid_sq(keys['sq'])
            self.e = offset[0] + int('{0}00'.format(keys['grid'][:3]))
            self.n = offset[1] + int('{0}00'.format(keys['grid'][3:]))

        elif len(keys) == 2 and 'sq' in keys and 'grid' in keys \
                            and keys['grid'].isdigit() \
                            and len(keys['grid']) == 10:

            offset = _parse_grid_sq(keys['sq'])
            self.e = offset[0] + int(keys['grid'][:5])
            self.n = offset[1] + int(keys['grid'][5:])

        elif len(keys) == 2 and 'sheet' in keys and 'grid' in keys \
                            and keys['sheet'] in LR_sheets \
                            and keys['grid'].isdigit() \
                            and len(keys['grid']) == 6:

            corner = LR_sheets[keys['sheet']]
            self.e = _lr_to_full_grid(corner[0], int('{0}00'.format(keys['grid'][:3])))
            self.n = _lr_to_full_grid(corner[1], int('{0}00'.format(keys['grid'][3:])))

        elif len(keys) > 1 and 'lat' in keys and 'lon' in keys:
            lat, lon = keys['lat'], keys['lon']
            if 'geoid' in keys and keys['geoid'] == 'OSGB36': 
                pass 
            else: # assume WGS84 if not specified
                if 'elev' in keys:
                    elev = keys['elev'] 
                else:
                    elev = 0
                
                lat, lon, elev = _shift_ll_from_wgs84(lat,lon,elev)

            self.e,self.n = _ll_to_grid(lat,lon)

        elif len(keys) == 1 and 'grid' in keys and Trad_grid_pat.match(keys['grid']):
            m = Trad_grid_pat.match(keys['grid'])
            offset = _parse_grid_sq(m.group(1))
            self.e = offset[0] + int('{0}00'.format(m.group(2)))
            self.n = offset[1] + int('{0}00'.format(m.group(3)))

        elif len(keys) == 1 and 'grid' in keys and Long_grid_pat.match(keys['grid']):
            m = Long_grid_pat.match(keys['grid'])
            offset = _parse_grid_sq(m.group(1))
            self.e = offset[0] + int(m.group(2))
            self.n = offset[1] + int(m.group(3))

        elif len(args) == 1 and Trad_grid_pat.match(args[0]):
            m = Trad_grid_pat.match(args[0])
            offset = _parse_grid_sq(m.group(1))
            self.e = offset[0] + int('{0}00'.format(m.group(2)))
            self.n = offset[1] + int('{0}00'.format(m.group(3)))

        elif len(args) == 1 and Long_grid_pat.match(args[0]):
            m = Long_grid_pat.match(args[0])
            offset = _parse_grid_sq(m.group(1))
            self.e = offset[0] + int(m.group(2))
            self.n = offset[1] + int(m.group(3))

        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self.e = args[0]
            self.n = args[1]

        else:
            raise RuntimeError('Cannot parse: {0}'.format(keys))

    def __str__(self):
        return '{0.e} {0.n}'.format(self)

    def __repr__(self):
        return '{0.__class__.__name__}(e={0.e},n={0.n})'.format(self)

    def __format__(self, code):
        if code == 'gps':
            return '{0.grid_square} {0.easting} {0.northing}'.format(self)
        elif code == 'trad':
            return '{0.grid_square} {0.short_easting} {0.short_northing}'.format(self)
        else:
            return '{0.e:.0f} {0.n:.0f}'.format(self)

    def __sub__(self, other):
        '''Subtraction returns the distance between two points (in metres).

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> b = OSGB_Grid_Point('TQ 183 698')
        >>> int(b-a)
        275358
        '''
        return math.hypot(self.e-other.e, self.n-other.n)

    def __eq__(self, other):
        '''Returns True if this object point near enough to the other one.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> b = OSGB_Grid_Point('TQ 183 698')
        >>> c = OSGB_Grid_Point(518331, 169843)
        >>> a==b
        False
        >>> a!=b
        True
        >>> b==c
        True
        '''
        return (self-other) <= OSGB_Grid_Point.near_enough

    def __ne__(self, other):
        '''Returns True is this object is not near enough to the other one.'''
        return (self-other) > OSGB_Grid_Point.near_enough

    @lazy_property
    def sheets(self):
        '''Returns a (possibly empty) list of Landranger sheet names that contain the point.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.sheets[0]
        '109'
        >>> isinstance(a.sheets[0], str)
        True
        '''

        sheets = []
        for sheet_number, corner in LR_sheets.items():
            e_delta = self.e - corner[0]
            n_delta = self.n - corner[1]
            if 0 <= e_delta < LR_sheet_size and 0 <= n_delta < LR_sheet_size:
                sheets.append(str(sheet_number))
        return sheets

    @lazy_property
    def grid_square(self):
        '''The grid square letters for a given point.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.grid_square
        'SD'

        '''
        e = int(self.e)
        n = int(self.n)

        great_letter = Grid_sq_letters[5*(n//Great_sq_size)+(e//Great_sq_size)+7]  # 7=5+2 so 0=>S

        e %= Great_sq_size
        n %= Great_sq_size

        small_letter = Grid_sq_letters[5*(n//Small_sq_size)+(e//Small_sq_size)]

        return great_letter+small_letter

    @lazy_property
    def easting(self):
        '''The easting for a given point as a string.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.easting
        '97200'

        '''
        return '{:05.0f}'.format(self.e % Small_sq_size)

    @lazy_property
    def northing(self):
        '''The northing for a given point as a string.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.northing
        '17100'

        '''
        return '{:05.0f}'.format(self.n % Small_sq_size)

    @lazy_property
    def short_easting(self):
        '''The hectometre easting for a given point as a string.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.short_easting
        '972'

        '''
        return self.easting[:3]

    @lazy_property
    def short_northing(self):
        '''The hectometre northing for a given point as a string.

        >>> a = OSGB_Grid_Point('SD 972 171')
        >>> a.short_northing
        '171'

        '''
        return self.northing[:3]

if __name__ == '__main__':
    import doctest
    doctest.testmod()

