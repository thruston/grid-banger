"""Conversion between latitude/longitude coordinates and OSGB grid
references.

This module provides the core routines that implement the OS conversion
formulae.

"""
from __future__ import print_function, division, unicode_literals

import array
import math
import pkgutil
import sys

__all__ = ['grid_to_ll', 'll_to_grid']

# The ellipsoid models for projection to and from the grid
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

# OSTN data
# Arrays of bytes are handled one way in Python3...
if sys.version_info > (3, 0):
    OSTN_EE_SHIFTS = array.array('H')
    try:
        OSTN_EE_SHIFTS.frombytes(pkgutil.get_data("osgb", "ostn_east_shift_82140"))
    except TypeError:
        print("Failed to load OSTN eastings from file", file=sys.stderr)
        raise

    OSTN_NN_SHIFTS = array.array('H')
    try:
        OSTN_NN_SHIFTS.frombytes(pkgutil.get_data("osgb", "ostn_north_shift_-84180"))
    except TypeError:
        print("Failed to load OSTN northings from file", file=sys.stderr)
        raise

# ... and another in Python2
else:
    OSTN_EE_SHIFTS = array.array(b'H')
    try:
        OSTN_EE_SHIFTS.fromstring(pkgutil.get_data("osgb", "ostn_east_shift_82140"))
    except TypeError:
        print("Failed to load OSTN eastings from file", file=sys.stderr)
        raise

    OSTN_NN_SHIFTS = array.array(b'H')
    try:
        OSTN_NN_SHIFTS.fromstring(pkgutil.get_data("osgb", "ostn_north_shift_-84180"))
    except TypeError:
        print("Failed to load OSTN northings from file", file=sys.stderr)
        raise

OSTN_EE_BASE = 82140
OSTN_NN_BASE = -84180


class Error(Exception):
    """Parent class for exceptions in this module"""
    pass


class UndefinedModelError(Error):
    """Raised when the model given is undefined

    Attributes:
        spam - the name of the unknown model

    """
    def __init__(self, spam):
        self.spam = spam

    def __str__(self):
        return "{}".format(self.spam)


def grid_to_ll(easting, northing, model='WGS84'):
    """
    Convert OSGB (easting, northing) to latitude and longitude.

    Input
        an (easting, northing) pair in metres from the false point of
        origin of the grid.

        Note that if you are starting with a tradtional grid reference
        string like ``TQ183506``, you need to parse it into an (easting,
        northing) pair using the :py:func:`parse_grid` function from
        :py:mod:`osgb.gridder` before you can pass it to this function.

    Output
        a (latitude, longitude) pair in degrees; postive East/North,
        negative West/South

    An optional argument 'model' defines the graticule model to use.
    The default is 'WGS84', the standard model used for the GPS network
    and for references given on Google Earth or Wikipedia, etc.  The
    only other valid value is 'OSGB36' which is the traditional model
    used in the UK before GPS.  Latitude and longitude coordinates
    marked around the edges of OS maps published before 2015 are given
    in the OSGB36 model.

    **Accuracy**: Grid references rounded to whole metres will give
    lat/lon that are accurate to about 5 decimal places.  In the UK,
    0.00001 of a degree of latitude is about 70cm, 0.00001 of a degree
    of longitude is about 1m.

    For example:

    >>> # Glendessary, the graticule marker on Sheet 33
    >>> lat, lon = grid_to_ll(197575, 794790, model='OSGB36')
    >>> (round(lat, 5), round(lon, 5))
    (56.99998, -5.3333)

    >>> # Scorriton
    >>> lat, lon = grid_to_ll(269995, 68361, model='OSGB36')
    >>> (round(lat, 5), round(lon, 5))
    (50.5, -3.83333)

    But Grid references in millimetres will give results accurate to 8
    decimal places.

    >>> # Cranbourne Chase, on the central meridian
    >>> lat, lon = grid_to_ll(400000, 122350.044, model='OSGB36')
    >>> (round(lat, 8), round(lon, 8))
    (51.0, -2.0)

    >>> # The example from the OSGB documentation
    >>> lat, lon = grid_to_ll(651409.903, 313177.27, model='OSGB36')
    >>> (round(lat, 8), round(lon, 8))
    (52.6575703, 1.71792158)

    The routines will produce lots more decimal places, so that you can
    choose what rounding you want, although they aren't really
    meaningful beyond nine places, since the conversion routines
    supplied by the OS are only designed to be accurate to about 1mm (8
    places).

    >>> # Hoy (Orkney)
    >>> grid_to_ll(323223, 1004000, model='OSGB36')
    (58.91680150461385, -3.3333320035568224)

    >>> # Glen Achcall
    >>> grid_to_ll(217380, 896060, model='OSGB36')
    (57.91671633292687, -5.083330213971718)

    Finally here is an example of how to use the optional keyword arguments:

    >>> # Keyword arguments for Glen Achcall
    >>> grid_to_ll(easting=217380, northing=896060, model='OSGB36')
    (57.91671633292687, -5.083330213971718)

    Check that outside area works:

    >>> tuple(round(x, 8) for x in grid_to_ll(easting=-100, northing=-100))
    (49.76584553, -7.55843918)

    >>> tuple(round(x, 8) for x in grid_to_ll(easting=1, northing=1))
    (49.76681683, -7.55714701)

    """

    (os_lat, os_lon) = _reverse_project_onto_ellipsoid(easting, northing, 'OSGB36')

    # if we want OS map LL we are done
    if model == 'OSGB36':
        return (os_lat, os_lon)

    # If we want WGS84 LL, we must adjust to pseudo grid if we can
    shifts = _find_OSTN_shifts_at(easting, northing)
    if shifts is not None:
        in_ostn_polygon = True
        x = easting - shifts[0]
        y = northing - shifts[1]
        last_shifts = shifts[:]
        for _ in range(20):
            shifts = _find_OSTN_shifts_at(x, y)

            if shifts is None:
                # we have been shifted off the edge
                in_ostn_polygon = False
                break

            x = easting - shifts[0]
            y = northing - shifts[1]
            if abs(shifts[0] - last_shifts[0]) < 0.0001:
                if abs(shifts[1] - last_shifts[1]) < 0.0001:
                    break

            last_shifts = shifts[:]

        if in_ostn_polygon:
            return _reverse_project_onto_ellipsoid(x, y, 'WGS84')

    # If we get here, we must use the Helmert approx
    return _shift_ll_from_osgb36_to_wgs84(os_lat, os_lon)


def ll_to_grid(lat, lon, model='WGS84', rounding=-1):
    """Convert a (latitude, longitude) pair to an OSGB grid (easting, northing) pair.

    Output
        a tuple containing (easting, northing) in metres from the grid origin.

    Input
         The arguments should be supplied as real numbers representing
         decimal degrees, like this:

        >>> ll_to_grid(51.5, -2.1)
        (393154.813, 177900.607)

        Following the normal convention, positive arguments mean North
        or East, negative South or West.

        If you have data with degrees, minutes and seconds, you can
        convert them to decimals like this:

        >>> ll_to_grid(51+25/60, 0-5/60-2/3600)
        (533338.156, 170369.238)

        >>> ll_to_grid(52 + 39/60 + 27.2531/3600, 1 + 43/60 + 4.5177/3600, model='OSGB36')
        (651409.903, 313177.27)

        But if you are still using python2 then be sure to ``import
        division`` so that you get the correct semantics for division
        when both numerator and denominator are integers.

    If you have trouble remembering the order of the arguments, or the
    returned values, note that latitude comes before longitude in the
    alphabet too, as easting comes before northing.  However since
    reasonable latitudes for the OSGB are in the range 49 to 61, and
    reasonable longitudes in the range -9 to +2, the ``ll_to_grid``
    function accepts argument in either order.  If your longitude is
    larger than your latitude, then the values of the arguments will be
    silently swapped:

    >>> ll_to_grid(-2.1, 51.5)
    (393154.813, 177900.607)

    But you can always give the arguments as named keywords if you prefer:

    >>> ll_to_grid(lon=-2.1, lat=51.5)
    (393154.813, 177900.607)

    The easting and northing will be returned as the distance in metres
    from the 'false point of origin' of the British Grid (which is a
    point some way to the south-west of the Scilly Isles).  If you want
    the result presented in a more traditional grid reference format you
    should pass the results to :py:func:`format_grid` from
    :py:mod:`osgb.gridder`.

    If the coordinates you supply are in the area covered by the OSTN
    transformation data, then the results will be rounded to 3 decimal
    places, which corresponds to the nearest millimetre.  If they are
    outside the coverage then the conversion is automagically done using
    a Helmert transformation instead of the OSTN data.  The results will
    be rounded to the nearest metre in this case, although you probably
    should not rely on the results being more accurate than about 5m.

    >>> # Somewhere in London
    >>> ll_to_grid(51.3, 0)
    (539524.836, 157551.913)

    >>> # Far north
    >>> ll_to_grid(61.3, 0)
    (507242.0, 1270342.0)

    The coverage extends quite a long way off shore.

    >>> # A point in the sea, to the north-west of Coll
    >>> ll_to_grid(56.75, -7)
    (94469.613, 773209.471)

    The numbers returned may be negative if your latitude and longitude
    are far enough south and west, but beware that the transformation is
    less and less accurate or useful the further you get from the
    British Isles.

    >>> ll_to_grid(51.3, -10)
    (-157250.0, 186110.0)

    ``ll_to_grid`` also takes an optional argument that sets the
    ellipsoid model to use.  This defaults to ``WGS84``, the name of the
    normal model for working with normal GPS coordinates, but if you
    want to work with the traditional latitude and longitude values
    printed on OS maps then you should add an optional model argument

    >>> ll_to_grid(49, -2, model='OSGB36')
    (400000.0, -100000.0)


    Incidentally, the grid coordinates returned by this call are the
    coordinates of the 'true point of origin' of the British grid.  You
    should get back an easting of 400000.0 for any point with longitude
    2W since this is the central meridian used for the OSGB projection.
    However you will get a slightly different value unless you specify
    ``model='OSGB36'`` since the WGS84 meridians are not quite the same
    as OSGB36.

        >>> ll_to_grid(52, -2, model='OSGB36')
        (400000.0, 233553.731)

        >>> ll_to_grid(52, -2, model='WGS84')
        (400096.274, 233505.403)

    If the model is not ``OSGB36`` or ``WGS84`` you will get an
    UndefinedModelError exception:

        >>> ll_to_grid(52, -2, model='EDM50') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        UndefinedModelError: EDM50

    You can also control the rounding directly if you need to, but be
    aware that asking for more decimal places does not make the
    conversion any more accurate; the formulae used are only designed to
    be accurate to 1mm.

        >>> ll_to_grid(52, -2, rounding=4)
        (400096.2738, 233505.4033)

    """

    if lat < lon:
        (lat, lon) = (lon, lat)

    if model not in ELLIPSOID_MODELS:
        raise UndefinedModelError(model)

    easting, northing = _project_onto_grid(lat, lon, model)

    default_rounding = 3
    if model == 'WGS84':
        shifts = _find_OSTN_shifts_at(easting, northing)
        if shifts is not None:
            easting += shifts[0]
            northing += shifts[1]
        else:
            (osgb_lat, osgb_lon) = _shift_ll_from_wgs84_to_osgb36(lat, lon)
            (easting, northing) = _project_onto_grid(osgb_lat, osgb_lon, 'OSGB36')
            default_rounding = 0

    if rounding < 0:
        rounding = default_rounding

    return (round(easting, rounding), round(northing, rounding))


def _compute_M(phi, model):
    '''Compute the first term of the solution given phi.

    Uses the ellipsoid constants (so needs the model name)
    '''
    p_plus = phi + ORIGIN_PHI
    p_minus = phi - ORIGIN_PHI
    _, b, n, _ = ELLIPSOID_MODELS[model]

    return CONVERGENCE_FACTOR * b * (
        (1 + n * (1 + 5/4*n * (1 + n))) * p_minus
        - 3*n * (1 + n * (1 + 7/8*n)) * math.sin(p_minus) * math.cos(p_plus)
        + (15/8*n * (n * (1 + n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
        - 35/24*n**3 * math.sin(3*p_minus) * math.cos(3*p_plus)
    )


def _project_onto_grid(lat, lon, model):
    '''Project spherical coordinates (lat, lon) onto a flat grid.

    This is the core bit of arithmetic, following the OSGB reference
    implementation.  The strange variable names (I, II, III, etc) follow
    those used in the OSGB notes, except that M is used instead of I to
    keep flake8 happy.

    We are essentially using a Taylor polynomial expansion, and the
    accuracy of this projection is limited by the number of terms
    included.  The design point appears to be approximately 1mm of
    error, but this is never precisely defined in the OSGB notes.

    This routine is not meant to be called by the user.  Use
    ll_to_grid() instead.

    >>> _project_onto_grid(52, -2, 'OSGB36')
    (400000.0, 233553.73133031745)

    '''

    phi = lat / 57.29577951308232087679815481410517
    cp = math.cos(phi)
    sp = math.sin(phi)
    tp = sp/cp  # cos phi cannot be zero in GB

    a, _, _, e2 = ELLIPSOID_MODELS[model]

    M = _compute_M(phi, model)

    nu = CONVERGENCE_FACTOR * a / math.sqrt(1 - e2 * sp * sp)
    etasq = (1 - e2 * sp * sp) / (1 - e2) - 1

    II = nu/2 * sp * cp
    III = nu/24 * sp * cp**3 * (5 - tp * tp + 9 * etasq)
    IIIA = nu/720 * sp * cp**5 * (61 + (-58 + tp * tp) * tp * tp)

    IV = nu * cp
    V = nu/6 * cp**3 * (etasq + 1 - tp * tp)
    VI = nu/120 * cp**5 * (5 + (-18 + tp * tp) * tp * tp + 14 * etasq - 58 * tp * tp * etasq)

    dl = lon / 57.29577951308232087679815481410517 - ORIGIN_LAMBDA
    north = ORIGIN_NORTHING + M + (II + (III + IIIA * dl * dl) * dl * dl) * dl * dl
    east = ORIGIN_EASTING + (IV + (V + VI * dl * dl) * dl * dl) * dl

    # return them with easting first
    return (east, north)


def _reverse_project_onto_ellipsoid(easting, northing, model):
    '''Un-project from the grid plane back on to the globe.

    This is the core arithmetic for the reverse projection.  Don't use
    this directly.  Use grid_to_ll instead.

    The strange variable names follow (roughly) the OSGB formulae.  The
    accuracy is limited by the number of terms in the final expansions,
    and the speed by the fact that this has to be an iterative process.

    >>> _reverse_project_onto_ellipsoid(400000.0, 233553.731330343, 'OSGB36')
    (52.0, -2.0)

    >>> (lat, lon) = _reverse_project_onto_ellipsoid(651409.903, 313177.270, 'OSGB36')
    >>> print('{:.8f} {:.8f}'.format(lat, lon))
    52.65757030 1.71792158

    '''

    _, _, _, e2 = ELLIPSOID_MODELS[model]

    af = CONVERGENCE_FACTOR * ELLIPSOID_MODELS[model][0]

    dn = northing - ORIGIN_NORTHING
    de = easting - ORIGIN_EASTING

    phi = ORIGIN_PHI + dn/af

    while True:
        M = _compute_M(phi, model)
        if abs(dn - M) < 0.00001:  # HUNDREDTH_MM
            break
        phi = phi + (dn - M) / af

    cp = math.cos(phi)
    sp = math.sin(phi)
    tp = sp / cp  # math.cos phi cannot be zero in GB

    splat = 1 - e2 * sp * sp
    sqrtsplat = math.sqrt(splat)
    nu = af / sqrtsplat
    rho = af * (1 - e2) / (splat*sqrtsplat)
    etasq = nu / rho - 1

    VII = tp / (2 * rho * nu)
    VIII = (5 + 3 * tp * tp + etasq - 9 * tp * tp * etasq) * tp / (24 * rho * nu**3)
    IX = (61 + (90 + 45 * tp * tp) * tp * tp) * tp / (720 * rho * nu**5)

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


def _find_OSTN_shifts_at(easting, northing):
    '''Get the OSTN shifted at a pseudo grid reference.

    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(331439.160, 431992.943)))
    95.40442 -72.14955

    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(91400.00044, 11399.99932))) # TP01
    92.14556 -81.19532
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(170277.18937, 11652.89486))) # TP02
    93.52863 -80.48986
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(250265.78908, 62095.88359))) # TP03
    94.02192 -79.31459
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(449719.40261, 75415.5941))) # TP04
    96.96839 -79.73310
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(438614.04492, 114871.19188))) # TP05
    96.87508 -78.94188
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(292090.28885, 168081.28118))) # TP06
    94.58115 -77.81618
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(639720.2239, 169645.8238))) # TP07
    101.61110 -79.96580
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(362174.40797, 170056.49988))) # TP08
    95.58303 -77.80988
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(530526.41231, 178467.04377))) # TP09
    98.56169 -78.57977
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(241030.73082, 220409.85756))) # TP10
    93.85318 -77.21656
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(599345.19593, 225801.4851))) # TP11
    100.39407 -78.65910
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(389448.04202, 261989.2714))) # TP12
    96.14798 -77.11840
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(474237.87392, 262125.33306))) # TP13
    98.09508 -77.57806
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(562079.80467, 319862.04179))) # TP14
    100.74233 -77.04679
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(453904.2695, 340910.74271))) # TP15
    98.56450 -75.79971
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(357359.68298, 383364.15112))) # TP16
    96.16002 -73.71512
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(247865.44739, 393566.26455))) # TP17
    93.52361 -73.35555
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(247865.71739, 393568.93846))) # TP18
    93.52361 -73.35546
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(331439.15958, 431992.94355))) # TP19
    95.40442 -72.14955
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(422143.67886, 433891.20633))) # TP20
    98.50714 -72.50533
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(227685.88237, 468918.33093))) # TP21
    92.44763 -70.94293
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(525643.49032, 470775.61009))) # TP22
    102.17968 -72.39609
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(244687.5168, 495324.61116))) # TP23
    93.11920 -69.72416
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(339824.59869, 556102.50434))) # TP24
    96.54631 -67.74334
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(424539.71821, 565080.53254))) # TP25
    99.63679 -67.82954
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(256247.4854, 664760.29198))) # TP26
    93.43960 -63.02298
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(319092.32821, 671010.63051))) # TP27
    96.10579 -63.09651
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(167542.80567, 797124.1528))) # TP28
    91.39633 -57.00880
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(397061.06978, 805408.1455))) # TP29
    99.42122 -58.40950
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(266961.48086, 846233.64636))) # TP30
    95.28714 -56.67436
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(9500.0055, 899499.9915))) # TP31
    87.90350 -50.99550
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(71622.45111, 938567.30194))) # TP32
    90.68089 -50.89794
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(151874.98359, 966535.33103))) # TP33
    93.66841 -51.55103
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(299624.62633, 967256.59533))) # TP34
    97.26467 -53.60333
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(330299.99994, 1017400.00024))) # TP35
    98.32306 -52.98424
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(261499.99975, 1025500.00025))) # TP36
    96.77825 -52.39825
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(180766.8244, 1029654.63912))) # TP37
    95.63660 -50.52512
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(421199.99984, 1072200.0002))) # TP38
    100.52516 -52.76120
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(440623.59268, 1107930.78086))) # TP39
    101.48032 -52.33286
    >>> print("{:.5f} {:.5f}".format(*_find_OSTN_shifts_at(395898.57806, 1138780.34555))) # TP40
    101.08994 -51.39455
    '''

    if not 0 < easting < 700000:
        return None

    if not 0 < northing < 1250000:
        return None

    east_km = int(easting / 1000)
    north_km = int(northing / 1000)

    lle = (OSTN_EE_BASE + OSTN_EE_SHIFTS[east_km + north_km * 701])/1000
    lre = (OSTN_EE_BASE + OSTN_EE_SHIFTS[east_km + north_km * 701 + 1])/1000
    ule = (OSTN_EE_BASE + OSTN_EE_SHIFTS[east_km + north_km * 701 + 701])/1000
    ure = (OSTN_EE_BASE + OSTN_EE_SHIFTS[east_km + north_km * 701 + 702])/1000

    lln = (OSTN_NN_BASE + OSTN_NN_SHIFTS[east_km + north_km * 701])/1000
    lrn = (OSTN_NN_BASE + OSTN_NN_SHIFTS[east_km + north_km * 701 + 1])/1000
    uln = (OSTN_NN_BASE + OSTN_NN_SHIFTS[east_km + north_km * 701 + 701])/1000
    urn = (OSTN_NN_BASE + OSTN_NN_SHIFTS[east_km + north_km * 701 + 702])/1000

    t = (easting / 1000) % 1
    u = (northing / 1000) % 1

    return (
        (1-t) * (1-u) * lle + t * (1-u) * lre + (1-t) * u * ule + t * u * ure,
        (1-t) * (1-u) * lln + t * (1-u) * lrn + (1-t) * u * uln + t * u * urn
    )


def _llh_to_cartesian(lat, lon, H, model):
    '''Approximate conversion from spherical to plane coordinates.

    Used as part of the Helmert transformation used outside the OSTN02
    area.

    >>> _llh_to_cartesian(53, -3, 10, 'OSGB36')
    (3841039.2016489906, -201300.3346975291, 5070178.453880734)

    >>> (x, y, z) =  _llh_to_cartesian(52, 1, 30, 'WGS84')
    >>> tuple(round(x, 8) for x in _cartesian_to_llh(x, y, z, 'WGS84'))
    (52.0, 1.0, 30.0)

    Note that you dont get more that 8 places of precision here.  Hence
    the `round(x, 8)` in the test. But that gives you precision to
    within 1mm which was the design point originally chosen by the OSGB.

    Numbers from the worked example in the OSGB guide

    e2 == 6.6705397616E-03
    nu == 6.3910506260E+06

    >>> t = _llh_to_cartesian(52 + 39/60 + 27.2531/3600, 1 + 43/60 + 4.5177/3600, 24.700, 'OSGB36')
    >>> tuple(round(x, 4) for x in t)
    (3874938.8497, 116218.6238, 5047168.2073)

    Note that here we have rounded to 4 places because these are in
    units of metres rather than degrees.

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


def _cartesian_to_llh(x, y, z, model):
    '''Approximate conversion from plane to spherical coordinates.

    Used as part of the Helmert transformation used outside the OSTN02
    area.

    >>> _cartesian_to_llh(3841039.2016489909, -201300.3346975291, 5070178.453880735, 'OSGB36')
    (53.0, -3.0, 10.0)
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


def _small_Helmert_transform_for_OSGB(direction, xa, ya, za):
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


def _shift_ll_from_osgb36_to_wgs84(lat, lon):
    '''Approximate conversion of OGSB sperical coordinates to WGS84.

    Used as a last resort by grid_to_ll

    >>> _shift_ll_from_osgb36_to_wgs84(52, -2)
    (52.0004248559296, -2.0014104687899463)
    '''
    (xa, ya, za) = _llh_to_cartesian(lat, lon, 0, 'OSGB36')
    (xb, yb, zb) = _small_Helmert_transform_for_OSGB(-1, xa, ya, za)
    (latx, lonx, _) = _cartesian_to_llh(xb, yb, zb, 'WGS84')
    return (latx, lonx)


def _shift_ll_from_wgs84_to_osgb36(lat, lon):
    '''Approximate conversion of WGS84 spherical coordinates to OSGB36.

    Used as a last resort by ll_to_grid
    >>> tuple(round(x, 7) for x in _shift_ll_from_wgs84_to_osgb36(52.0004248559296, -2.0014104687899463))
    (52.0, -2.0)
    '''
    (xa, ya, za) = _llh_to_cartesian(lat, lon, 0, 'WGS84')
    (xb, yb, zb) = _small_Helmert_transform_for_OSGB(+1, xa, ya, za)
    (latx, lonx, _) = _cartesian_to_llh(xb, yb, zb, 'OSGB36')
    return (latx, lonx)
