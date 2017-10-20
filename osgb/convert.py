"""Conversion between latitude/longitude and OSGB grid references.

Toby Thurston -- 08 Oct 2017 

"""
# pylint: disable=C0103, C0301
from __future__ import print_function, unicode_literals, division

import math
import pkgutil
import struct

__all__ = ['grid_to_ll', 'll_to_grid']

# The ellipsoid model for project to and from the grid
ELLIPSOID_MODELS = {
    'WGS84': (6378137.000, 6356752.31424518, 0.0016792203863836474, 0.006694379990141316996137233540),
    'OSGB36': (6377563.396, 6356256.909, 0.0016732203289875152, 0.006670540074149231821114893873561),
}


# The defining constants for the OSGB grid
ORIGIN_LAMBDA = -2 / 57.29577951308232087679815481410517
ORIGIN_PHI = 49 / 57.29577951308232087679815481410517
ORIGIN_EASTING = 400000.0
ORIGIN_NORTHING = -100000.0
CONVERGENCE_FACTOR = 0.9996012717

OSTN_DATA = pkgutil.get_data("osgb", "ostn02.data").split(b'\n')
ostn_cache = dict()

class ConvertFailure(Exception):
    """Parent class for Convert exceptions"""
    pass

class UndefinedModel(ConvertFailure):
    """Raised when the model given is undefined

    Attributes:
        spam

    """
    def __init__(self, spam):
        self.spam = spam
        super(UndefinedModel, self).__init__()

    def __str__(self):
        return "{}".format(self.spam)

def grid_to_ll(easting, northing, model='WGS84'):
    """Convert OSGB (easting, northing) to latitude and longitude.

    Input: an (easting, northing) pair in metres from the false point of origin of the grid.

    Output: a (latitude, longitude) pair in degrees, postive East/North negative West/South

    An optional argument 'model' defines the graticule model to use.  The default is WGS84,
    the standard model used for the GPS network and for references given on Google Earth
    or Wikipedia, etc.  The only other valid value is 'OSGB36' which is the traditional model
    used in the UK before GPS.  Latitude and longitude marked around the edges of OS Landranger maps
    are given in the OSGB36 model.

    Grid references rounded to whole metres will give lat/lon that are accurate to about 5 decimal places.
    0.00001 of a degree of latitude is about 70cm in the UK, 0.00001 of a degree of longitude is about 1m.

    Glendessary
    >>> lat, lon = grid_to_ll(197575, 794790, model='OSGB36')
    >>> (round(lat, 5), round(lon, 5))
    (56.99998, -5.3333)

    Scorriton
    >>> lat, lon = grid_to_ll(269995, 68361, model='OSGB36')
    >>> (round(lat, 5), round(lon, 5))
    (50.5, -3.83333)

    But Grid references in millimetres (and in the first case on the central meridian) will
    give results accurate to 8 decimal places.

    Cranbourne Chase
    >>> lat, lon = grid_to_ll(400000, 122350.044, model='OSGB36')
    >>> (round(lat, 8), round(lon, 8))
    (51.0, -2.0)

    Example from OSGB
    >>> lat, lon = grid_to_ll(651409.903, 313177.27, model='OSGB36')
    >>> (round(lat, 8), round(lon, 8))
    (52.6575703, 1.71792158)

    None the less, the routines will produce lots more decimal places, so
    that you can choose what rounding you want.

    Hoy
    >>> grid_to_ll(323223, 1004000, model='OSGB36')
    (58.91680150461385, -3.3333320035568224)

    Glen Achcall
    >>> grid_to_ll(217380, 896060, model='OSGB36')
    (57.91671633292687, -5.083330213971718)

    Keyword arguments for Glen Achcall
    >>> grid_to_ll(easting=217380, northing=896060, model='OSGB36')
    (57.91671633292687, -5.083330213971718)

    """

    (os_lat, os_lon) = _reverse_project_onto_ellipsoid(easting, northing, 'OSGB36')

    # if we want OS map LL we are done
    if model == 'OSGB36':
        return (os_lat, os_lon)

    # If we want WGS84 LL, we must adjust to pseudo grid if we can
    shifts = find_OSTN02_shifts_at(easting, northing)
    if shifts is not None:
        in_ostn02_polygon = True
        x = easting - shifts[0]
        y = northing - shifts[1]
        last_shifts = shifts[:]
        for _ in range(20):
            shifts = find_OSTN02_shifts_at(x, y)

            if shifts is None:
                # we have been shifted off the edge
                in_ostn02_polygon = False
                break

            x = easting - shifts[0]
            y = northing - shifts[1]
            if abs(shifts[0] - last_shifts[0]) < 0.0001:
                if abs(shifts[1] - last_shifts[1]) < 0.0001:
                    break

            last_shifts = shifts[:]

        if in_ostn02_polygon:
            return _reverse_project_onto_ellipsoid(x, y, 'WGS84')

    # If we get here, we must use the Helmert approx
    return shift_ll_from_osgb36_to_wgs84(os_lat, os_lon)


def ll_to_grid(lat, lon, model='WGS84', rounding=-1):
    """Convert a (latitude, longitude) pair to an OSGB grid (easting, northing) pair.

    Output: a tuple containing (easting, northing) in metres from the grid origin.

    Input: The arguments should be supplied as real numbers representing
    decimal degrees, like this

    >>> ll_to_grid(51.5, -2.1)
    (393154.801, 177900.605)

    Following the normal convention, positive arguments mean North or
    East, negative South or West.

    If you have data with degrees, minutes and seconds, you can convert them
    to decimals like this:

    >>> ll_to_grid(51+25/60, 0-5/60-2/3600)
    (533338.144, 170369.235)

    If you have trouble remembering the order of the arguments, or the
    returned values, note that latitude comes before longitude in the
    alphabet too, as easting comes before northing.

    However since reasonable latitudes for the OSGB are in the range 49 to 61,
    and reasonable longitudes in the range -9 to +2, ll_to_grid accepts
    argument in either order.  If your longitude is larger than your latitude,
    then the values of the arguments will be silently swapped:

    >>> ll_to_grid(-2.1, 51.5)
    (393154.801, 177900.605)

    But you can always give the arguments as named keywords if you prefer:

    >>> ll_to_grid(lon=-2.1, lat=51.5)
    (393154.801, 177900.605)

    The easting and northing will be returned as the distance in metres from
    the `false point of origin' of the British Grid (which is a point some
    way to the south-west of the Scilly Isles).

    If the coordinates you supply are in the area covered by the OSTN02
    transformation data, then the results will be rounded to 3 decimal
    places, which corresponds to the nearest millimetre.  If they are
    outside the coverage (which normally means more than a few km off shore)
    then the conversion is automagically done using a Helmert transformation
    instead of the OSTN02 data.  The results will be rounded to the nearest
    metre in this case, although you probably should not rely on the results
    being more accurate than about 5m.

    A point in the sea, to the north-west of Coll
    >>> ll_to_grid(56.75, -7)
    (94471.0, 773206.0)

    Somewhere in London
    >>> ll_to_grid(51.3, 0)
    (539524.823, 157551.911)

    Far north
    >>> ll_to_grid(61.3, 0)
    (507242.0, 1270342.0)

    Examples from docs
    >>> ll_to_grid(51.5, -2.1)
    (393154.801, 177900.605)

    >>> ll_to_grid(52 + 39/60 + 27.2531/3600, 1 + 43/60 + 4.5177/3600, model='OSGB36')
    (651409.903, 313177.27)

    The numbers returned may be negative if your latitude and longitude are
    far enough south and west, but beware that the transformation is less
    and less accurate or useful the further you get from the British Isles.

    >>> ll_to_grid(51.3, -10)
    (-157250.0, 186110.0)

    If you want the result presented in a more traditional grid reference
    format you should pass the results to osgb.format_grid()

    ll_to_grid() also takes an optional argument that sets the ellipsoid
    model to use.  This defaults to `WGS84', the name of the normal model
    for working with normal GPS coordinates, but if you want to work with
    the traditional latitude and longitude values printed on OS maps then
    you should add an optional model argument

        >>> ll_to_grid(49, -2, model='OSGB36')
        (400000.0, -100000.0)

    If the model is not 'OSGB36' or 'WGS84' you will get an UndefinedModel exception:

        >>> ll_to_grid(49, -2, model='EDM50')
        Traceback (most recent call last):
        ...
        UndefinedModel: EDM50

    Incidentally, the grid coordinates returned by this call are the
    coordinates of the `true point of origin' of the British grid.  You should
    get back an easting of 400000.0 for any point with longitude 2W since this is
    the central meridian used for the OSGB projection.  However you will get a
    slightly different value unless you specify "model='OSGB36'"
    since the WGS84 meridians are not quite the same as OSGB36.

        >>> ll_to_grid(52, -2, model='OSGB36')
        (400000.0, 233553.731)

        >>> ll_to_grid(52, -2, model='WGS84')
        (400096.263, 233505.401)

    You can also control the rounding directly if you need to (but beware that
    adding more decimal places does not make the conversion any more accurate -
    the formulae used are only designed to be accurate to 1mm).

        >>> ll_to_grid(52, -2, rounding=4)
        (400096.2628, 233505.4007)

    """

    if lat < lon:
        (lat, lon) = (lon, lat)

    if model not in ELLIPSOID_MODELS:
        raise UndefinedModel(model)

    easting, northing = _project_onto_grid(lat, lon, model)

    if model == 'WGS84':
        shifts = find_OSTN02_shifts_at(easting, northing)
        if shifts is not None:
            easting += shifts[0]
            northing += shifts[1]
            if rounding < 0:
                rounding = 3
        else:
            (osgb_lat, osgb_lon) = shift_ll_from_wgs84_to_osgb36(lat, lon)
            (easting, northing) = _project_onto_grid(osgb_lat, osgb_lon, 'OSGB36')
            if rounding < 0:
                rounding = 0

    if rounding < 0:
        rounding = 3

    return (round(easting, rounding), round(northing, rounding))

def _project_onto_grid(lat, lon, model):
    '''Project spherical coordinates (lat, lon) onto a flat grid.

    This is the core bit of arithmetic, following the OSGB reference implementation.
    The strange variable names (I, II, III, etc) follow those used in the OSGB
    notes.  We are essentially using a Taylor polynomial expansion, and the
    accurancy of this projection is limited by the number of terms included.
    The design point appears to be approximately 1mm of error, but this is
    never precisely defined in the OSGB notes.

    This routine is not meant to be called by the user.  Use ll_to_grid() instead.

    >>> _project_onto_grid(52, -2, 'OSGB36')
    (400000.0, 233553.73133031745)

    '''

    phi = lat / 57.29577951308232087679815481410517
    cp = math.cos(phi)
    sp = math.sin(phi)
    tp = sp/cp # cos phi cannot be zero in GB

    a, b, n, e2 = ELLIPSOID_MODELS[model]

    p_plus = phi + ORIGIN_PHI
    p_minus = phi - ORIGIN_PHI

    I = b * CONVERGENCE_FACTOR * (
        (1 + n * (1 + 5/4*n * (1 + n))) * p_minus
        - 3*n * (1 + n * (1 + 7/8*n)) * math.sin(p_minus) * math.cos(p_plus)
        + (15/8*n * (n * (1 + n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
        - 35/24*n**3 * math.sin(3*p_minus) * math.cos(3*p_plus)
    )

    nu = a * CONVERGENCE_FACTOR / math.sqrt(1 - e2 * sp * sp)
    eta2 = (1 - e2 * sp * sp) / (1 - e2) - 1

    II = nu/2  * sp * cp
    III = nu/24 * sp * cp**3 * (5 - tp * tp + 9*eta2)
    IIIA = nu/720 * sp * cp**5 * (61 - (58 + tp * tp) * tp * tp)

    IV = nu*cp
    V = nu/6 * cp**3 * (eta2 + 1 - tp * tp)
    VI = nu/120 * cp**5 * (5 + (-18 + tp * tp) * tp * tp + 14 * eta2 - 58 * tp * tp * eta2)

    dl = lon / 57.29577951308232087679815481410517 - ORIGIN_LAMBDA
    north = ORIGIN_NORTHING + I + (II + (III + IIIA * dl * dl) * dl * dl) * dl * dl
    east = ORIGIN_EASTING + (IV + (V + VI * dl * dl) * dl * dl) * dl

    # return them with easting first
    return (east, north)

def _reverse_project_onto_ellipsoid(easting, northing, model):
    '''Un-project from the grid plane back on to the globe.

    This is the core arithmetic for the reverse projection.  Don't
    use this directly.  Use grid_to_ll instead.

    The strange variable names follow (roughly) the OSGB formulae.
    The accuracy is limited by the number of terms in the final expansions,
    and the speed by the fact that this has to be an iterative process.

    >>> _reverse_project_onto_ellipsoid(400000.0, 233553.731330343, 'OSGB36')
    (52.0, -2.0)

    '''

    a, b, n, e2 = ELLIPSOID_MODELS[model]

    af = a * CONVERGENCE_FACTOR

    dn = northing - ORIGIN_NORTHING
    de = easting - ORIGIN_EASTING

    phi = ORIGIN_PHI + dn/af

    while True:
        p_plus = phi + ORIGIN_PHI
        p_minus = phi - ORIGIN_PHI
        M = b * CONVERGENCE_FACTOR * (
            (1 + n * (1 + 5/4*n*(1 + n)))*p_minus
            - 3*n*(1+n*(1+7/8*n))  * math.sin(p_minus) * math.cos(p_plus)
            + (15/8*n * (n*(1+n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
            - 35/24*n**3           * math.sin(3*p_minus) * math.cos(3*p_plus)
        )
        if abs(dn-M) < 0.00001: # HUNDREDTH_MM
            break
        phi = phi + (dn-M)/af

    cp = math.cos(phi)
    sp = math.sin(phi)
    tp = sp/cp # math.cos phi cannot be zero in GB

    splat = 1 - e2 * sp * sp
    sqrtsplat = math.sqrt(splat)
    nu = af / sqrtsplat
    rho = af * (1 - e2) / (splat*sqrtsplat)
    eta2 = nu/rho - 1

    VII = tp / (2 * rho * nu)
    VIII = tp / (24 * rho * nu**3) * (5 + 3 * tp * tp + eta2 - 9 * tp * tp * eta2)
    IX = tp / (720 * rho * nu**5) * (61 + (90 + 45 * tp * tp) * tp * tp)

    secp = 1/cp

    X = secp / nu
    XI = secp / (6 * nu**3) * (nu/rho + 2 * tp * tp)
    XII = secp / (120 * nu**5) * (5 + (28 + 24 * tp * tp) * tp * tp)
    XIIA = secp / (5040 * nu**7) * (61 + (662 + (1320 + 720 * tp * tp) * tp * tp) * tp * tp)

    phi = phi + (-VII + (VIII - IX * de * de) * de * de) * de * de
    lam = ORIGIN_LAMBDA + (X + (-XI + (XII - XIIA * de * de) * de * de) * de * de) * de

    # now put into degrees & return
    return (phi * 57.29577951308232087679815481410517,
            lam * 57.29577951308232087679815481410517)

def get_ostn_pair(x, y):
    """Get the shifts for (x, y) and (x+1, y) from the OSTN02 array.

    >>> get_ostn_pair(80, 1)
    [91.902, -81.569, 91.916, -81.563]

    >>> get_ostn_pair(331, 431)
    [95.383, -72.19, 95.405, -72.196]
    """
    leading_zeros = int(OSTN_DATA[y][0:3])

    if x < leading_zeros:
        return None

    index = 3 + 6*(x-leading_zeros)
    if index + 12 > len(OSTN_DATA[y]):
        return None

    shifts = [86, -82, 86, -82]
    for i in range(4):
        a, b, c = struct.unpack('BBB', OSTN_DATA[y][index+3*i : index+3*i+3])
        s = (a<<10) + (b<<5) + c - 50736
        if s == 0:
            return None
        shifts[i] += s/1000

    return shifts

def find_OSTN02_shifts_at(easting, northing):
    """Get the OSTN02 shifts at a pseudo grid reference.

    >>> print("{:.5f} {:.5f}".format(*find_OSTN02_shifts_at(331439.160, 431992.943)))
    95.39242 -72.15156

    """

    if easting < 0:
        return None

    if northing < 0:
        return None

    e_index = int(easting/1000)
    n_index = int(northing/1000)

    if n_index >= len(OSTN_DATA):
        return None

    lo_key = e_index + n_index * 701

    if lo_key not in ostn_cache:
        ostn_cache[lo_key] = get_ostn_pair(e_index, n_index)

    lo_shifts = ostn_cache[lo_key]
    if lo_shifts is None:
        return None

    hi_key = lo_key + 701

    if hi_key not in ostn_cache:
        ostn_cache[hi_key] = get_ostn_pair(e_index, n_index+1)

    hi_shifts = ostn_cache[hi_key]
    if hi_shifts is None:
        return None

    t = easting/1000 - e_index # offset within square
    u = northing/1000 - n_index

    f0 = (1-t) * (1-u)
    f1 = t * (1-u)
    f2 = (1-t) * u
    f3 = t * u

    return (
        f0*lo_shifts[0] + f1*lo_shifts[2] + f2*hi_shifts[0] + f3*hi_shifts[2],
        f0*lo_shifts[1] + f1*lo_shifts[3] + f2*hi_shifts[1] + f3*hi_shifts[3]
    )

def llh_to_cartesian(lat, lon, H, model):
    '''Approximate conversion from spherical to plane coordinates.

    Used as part of the Helmert transformation used outside the OSTN02 area.

    >>> (x, y, z) =  llh_to_cartesian(53, -3, 10, 'OSGB36')
    >>> cartesian_to_llh(x, y, z, 'OSGB36')
    (53.0, -3.0, 9.999999999068677)

    >>> (x, y, z) =  llh_to_cartesian(52, 1, 30, 'WGS84')
    >>> cartesian_to_llh(x, y, z, 'WGS84')
    (52.0, 1.0, 29.999999999068677)

    '''
    a, _, _, e2 = ELLIPSOID_MODELS[model]

    phi = lat / 57.29577951308232087679815481410517
    sp = math.sin(phi)
    cp = math.cos(phi)

    lam = lon / 57.29577951308232087679815481410517
    sl = math.sin(lam)
    cl = math.cos(lam)

    nu = a / math.sqrt(1 - e2 * sp * sp)

    return (
        (nu+H) * cp * cl,
        (nu+H) * cp * sl,
        ((1-e2)*nu+H)*sp
    )

def cartesian_to_llh(x, y, z, model):
    '''Approximate conversion from plane to spherical coordinates.

    Used as part of the Helmert transformation used outside the OSTN02 area.
    '''

    a, _, _, e2 = ELLIPSOID_MODELS[model]

    p = math.sqrt(x*x+y*y)
    lam = math.atan2(y, x)
    phi = math.atan2(z, p*(1-e2))

    while True:
        sp = math.sin(phi)
        nu = a / math.sqrt(1 - e2*sp*sp)
        oldphi = phi
        phi = math.atan2(z+e2*nu*sp, p)
        if abs(oldphi-phi) < 1E-12:
            break

    return (
        phi * 57.29577951308232087679815481410517,
        lam * 57.29577951308232087679815481410517,
        p/math.cos(phi) - nu
    )

def small_Helmert_transform_for_OSGB(direction, xa, ya, za):
    '''Transform 3d planar coordinates to approximate OSGB36 to WGS84.

    Formulae as supplied by the OSGB.  Designed for +/- 5m accuracy in
    most of OSGB area.

    `direction` indicates the desired transformation: -1 -> WGS84, +1 -> OSGB36

    '''
    tx = direction * -446.448
    ty = direction * +125.157
    tz = direction * -542.060
    sp = direction * 0.0000204894 + 1
    rx = (direction * -0.1502/3600) / 57.29577951308232087679815481410517
    ry = (direction * -0.2470/3600) / 57.29577951308232087679815481410517
    rz = (direction * -0.8421/3600) / 57.29577951308232087679815481410517
    xb = tx + sp*xa - rz*ya + ry*za
    yb = ty + rz*xa + sp*ya - rx*za
    zb = tz - ry*xa + rx*ya + sp*za
    return (xb, yb, zb)

def shift_ll_from_osgb36_to_wgs84(lat, lon):
    '''Approximate conversion of OGSB sperical coordinates to WGS84.

    Used as a last resort by grid_to_ll
    '''
    (xa, ya, za) = llh_to_cartesian(lat, lon, 0, 'OSGB36')
    (xb, yb, zb) = small_Helmert_transform_for_OSGB(-1, xa, ya, za)
    (latx, lonx, _) = cartesian_to_llh(xb, yb, zb, 'WGS84')
    return (latx, lonx)


def shift_ll_from_wgs84_to_osgb36(lat, lon):
    '''Approximate conversion of WGS84 spherical coordinates to OSGB36.

    Used as a last resort by ll_to_grid
    '''
    (xa, ya, za) = llh_to_cartesian(lat, lon, 0, 'WGS84')
    (xb, yb, zb) = small_Helmert_transform_for_OSGB(+1, xa, ya, za)
    (latx, lonx, _) = cartesian_to_llh(xb, yb, zb, 'OSGB36')
    return (latx, lonx)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
