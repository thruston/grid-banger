"""Conversion between latitude/longitude and OSGB grid references.

Toby Thurston -- 13 Mar 2016 

"""

import pkgutil
import math

__all__ = ['grid_to_ll', 'll_to_grid']

# The ellipsoid model for project to and from the grid
ellipsoid_models = {
    'WGS84'  : ( 6378137.000, 6356752.31424518, 298.257223563,  0.006694379990141316996137233540 ),
    'OSGB36' : ( 6377563.396, 6356256.909,      299.3249612665, 0.0066705400741492318211148938735613129751683486352306 ), 
}

# The defining constants for the OSGB grid
ORIGIN_LAMBDA = -2 / 57.29577951308232087679815481410517
ORIGIN_PHI    = 49 / 57.29577951308232087679815481410517
ORIGIN_EASTING      =  400000.0
ORIGIN_NORTHING     = -100000.0
CONVERGENCE_FACTOR  = 0.9996012717

ostn_data = pkgutil.get_data("osgb", "ostn02.data").split(b'\n')

def grid_to_ll(easting, northing, model='WGS84'):
    """Convert OSGB (easting, northing) to latitude and longitude.

    Input: an (easting, northing) pair in metres from the false point of origin of the grid.

    Output: a (latitude, longitude) pair in degrees, postive East/North negative West/South

    An optional argument 'model' defines the graticule model to use.  The default is WGS84,
    the standard model used for the GPS network and for references given on Google Earth
    or Wikipedia, etc.  The only other valid value is 'OSGB36' which is the traditional model 
    used in the UK before GPS.  Latitude and longitude marked around the edges of OS Landranger maps
    are given in the OSGB36 model.

    Glendessary
    >>> '{:g} {:g}'.format(*grid_to_ll(197575,794790))
    '56.9997 -5.33448'

    Scorriton
    >>> '{:g} {:g}'.format(*grid_to_ll(269995,68361,model='OSGB36'))
    '50.5 -3.83333'

    Cranbourne Chase
    >>> '{:g} {:g}'.format(*grid_to_ll(400000,122350,model='OSGB36'))
    '51 -2'

    Hoy
    >>> '{:g} {:g}'.format(*grid_to_ll(323223,1004000,model='OSGB36'))
    '58.9168 -3.33333'

    Glen Achcall
    >>> '{:g} {:g}'.format(*grid_to_ll(217380,896060,model='OSGB36'))
    '57.9167 -5.08333'
    
    Keyword arguments for Glen Achcall
    >>> '{:g} {:g}'.format(*grid_to_ll(easting=217380, northing=896060,model='OSGB36'))
    '57.9167 -5.08333'

    """

    (os_lat, os_lon) = reverse_project_onto_ellipsoid(easting, northing, 'OSGB36')

    # if we want OS map LL we are done
    if model == 'OSGB36':
        return (os_lat, os_lon)

    # If we want WGS84 LL, we must adjust to pseudo grid if we can
    shifts = find_OSTN02_shifts_at(easting,northing)
    if shifts is not None:
        in_ostn02_polygon = True
        x = easting - shifts[0]
        y = northing - shifts[1]
        last_shifts = shifts[:]
        for i in range(20): 
            shifts = find_OSTN02_shifts_at(x,y)
            
            if shifts is None:
                # we have been shifted off the edge
                in_ostn02_polygon = False
                break
                
            x = easting - shifts[0]
            y = northing - shifts[1]
            if abs(shifts[0] - last_shifts[0]) < 0.0001 and abs(shifts[1] - last_shifts[1]) < 0.0001:
                break

            last_shifts = shifts[:]
        
        if in_ostn02_polygon:
            return reverse_project_onto_ellipsoid(easting-shifts[0], northing-shifts[1], 'WGS84')
        
    # If we get here, we must use the Helmert approx
    return shift_ll_from_osgb36_to_wgs84(os_lat, os_lon)


def ll_to_grid(lat, lon, model='WGS84'):
    """Convert (latitude, longitude) to an OSGB grid (easting, northing) pair.

    Input 

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(51.5,-2.1))
    '393154.801 177900.605'

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(51.3,0))
    '539524.823 157551.911'

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(lat=51.3,lon=0))
    '539524.823 157551.911'

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(0,51.3))
    '539524.823 157551.911'

    >>> ll_to_grid(49, -2, model="OSGB36")
    (400000.0, -100000.0)

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(52, -2, model="OSGB36"))
    '400000.000 233553.731'

    >>> '{:.3f} {:.3f}'.format(*ll_to_grid(56+55/60, -5.25, model="OSGB36"))
    '202190.386 785279.519'

    Far west
    >>> '{:.0f} {:.0f}'.format(*ll_to_grid(51.3, -10))
    '-157250 186110'

    Far North
    >>> '{:.0f} {:.0f}'.format(*ll_to_grid(61.3, 0))
    '507242 1270342'

    In sea north-west of Coll
    >>> '{:.0f} {:.0f}'.format(*ll_to_grid(56.75, -7))
    '94471 773206'


    """

    if lat < lon:
        (lat, lon) = (lon, lat)

    if model not in ellipsoid_models:
        raise KeyError("No definition for model:".format(model))

    easting, northing = project_onto_grid(lat, lon, model)

    if model == 'WGS84':
        shifts = find_OSTN02_shifts_at(easting, northing)
        if shifts is not None:
            easting += shifts[0]
            northing += shifts[1]
        else:
            (osgb_lat, osgb_lon) = shift_ll_from_wgs84_to_osgb36(lat, lon)
            (easting, northing)  = project_onto_grid(osgb_lat, osgb_lon, 'OSGB36')

    return (easting, northing)

def project_onto_grid(lat, lon, model):
    
    a,b,f,e2 = ellipsoid_models[model]

    n = (a-b)/(a+b)
    af = a * CONVERGENCE_FACTOR

    phi = lat / 57.29577951308232087679815481410517
    lam = lon / 57.29577951308232087679815481410517

    cp = math.cos(phi) 
    sp = math.sin(phi)
    sp2 = sp*sp
    tp  = sp/cp # cos phi cannot be zero in GB
    tp2 = tp*tp 
    tp4 = tp2*tp2

    splat = 1 - e2 * sp2 
    sqrtsplat = math.sqrt(splat)
    nu  = af / sqrtsplat
    rho = af * (1 - e2) / (splat*sqrtsplat)
    eta2 = nu/rho - 1

    p_plus  = phi + ORIGIN_PHI
    p_minus = phi - ORIGIN_PHI
    M = b * CONVERGENCE_FACTOR * (
           (1 + n * (1 + 5/4*n*(1 + n)))*p_minus
         - 3*n*(1+n*(1+7/8*n))  * math.sin(  p_minus) * math.cos(  p_plus)
         + (15/8*n * (n*(1+n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
         - 35/24*n**3           * math.sin(3*p_minus) * math.cos(3*p_plus)
           )

    I    = M + ORIGIN_NORTHING
    II   = nu/2  * sp * cp
    III  = nu/24 * sp * cp**3 * (5-tp2+9*eta2)
    IIIA = nu/720* sp * cp**5 *(61-58*tp2+tp4)

    IV   = nu*cp
    V    = nu/6   * cp**3 * (nu/rho-tp2)
    VI   = nu/120 * cp**5 * (5-18*tp2+tp4+14*eta2-58*tp2*eta2)

    dl = lam - ORIGIN_LAMBDA
    north = I + II*dl**2 + III*dl**4 + IIIA*dl**6
    east = ORIGIN_EASTING + IV*dl + V*dl**3 + VI*dl**5

    return (east, north)

def reverse_project_onto_ellipsoid(easting, northing, model):

    a,b,f,e2 = ellipsoid_models[model]

    n = (a-b)/(a+b)
    af = a * CONVERGENCE_FACTOR

    dn = northing - ORIGIN_NORTHING
    de = easting - ORIGIN_EASTING
    
    phi = ORIGIN_PHI + dn/af

    while True:
        p_plus  = phi + ORIGIN_PHI
        p_minus = phi - ORIGIN_PHI
        M = b * CONVERGENCE_FACTOR * (
               (1 + n * (1 + 5/4*n*(1 + n)))*p_minus
             - 3*n*(1+n*(1+7/8*n))  * math.sin(  p_minus) * math.cos(  p_plus)
             + (15/8*n * (n*(1+n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
             - 35/24*n**3           * math.sin(3*p_minus) * math.cos(3*p_plus)
               )
        if abs(dn-M) < 0.00001: # HUNDREDTH_MM
            break
        phi = phi + (dn-M)/af

    cp = math.cos(phi)
    sp = math.sin(phi)
    sp2 = sp*sp
    tp  = sp/cp; # math.cos phi cannot be zero in GB
    tp2 = tp*tp
    tp4 = tp2*tp2
    tp6 = tp4*tp2

    splat = 1 - e2 * sp2
    sqrtsplat = math.sqrt(splat)
    nu  = af / sqrtsplat
    rho = af * (1 - e2) / (splat*sqrtsplat)
    eta2 = nu/rho - 1

    VII  = tp /   (2*rho*nu)
    VIII = tp /  (24*rho*nu**3) *  (5 +  3*tp2 + eta2 - 9*tp2*eta2)
    IX   = tp / (720*rho*nu**5) * (61 + 90*tp2 + 45*tp4)

    secp = 1/cp

    X    = secp/nu
    XI   = secp/(   6*nu**3)*(nu/rho + 2*tp2)
    XII  = secp/( 120*nu**5)*(      5 + 28*tp2 +   24*tp4)
    XIIA = secp/(5040*nu**7)*(    61 + 662*tp2 + 1320*tp4 + 720*tp6)

    phi = phi - VII*de**2 + VIII*de**4 - IX*de**6
    lam = ORIGIN_LAMBDA + X*de - XI*de**3 + XII*de**5 - XIIA*de**7

    # now put into degrees & return
    return (phi * 57.29577951308232087679815481410517,
            lam * 57.29577951308232087679815481410517)

import struct
def get_ostn_pair(x,y):
    """Get the shifts for (x,y) and (x+1,y) from the OSTN02 array.

    >>> get_ostn_pair(80,1)
    [91.902, -81.569, 91.916, -81.563]

    >>> get_ostn_pair(331,431)
    [95.383, -72.19, 95.405, -72.196]
    """

    leading_zeros = int(ostn_data[y][0:3])

    if x < leading_zeros:
        return None

    index = 3 + 6*(x-leading_zeros)
    if index + 12 > len(ostn_data[y]):
        return None

    shifts = [ 86, -82, 86, -82 ]
    for i in range(4):
        a,b,c = struct.unpack('BBB', ostn_data[y][ index+3*i : index+3*i+3 ])
        s = (a<<10) + (b<<5) + c - 50736
        if s == 0:
            return None
        shifts[i] += s/1000

    return shifts

def find_OSTN02_shifts_at(easting, northing):
    """Get the OSTN02 shifts at a pseudo grid reference.

    >>> "{:.5f} {:.5f}".format(*find_OSTN02_shifts_at(331439.160, 431992.943))
    '95.39242 -72.15156'

    """

    if easting < 0:
        return None

    if northing < 0:
        return None

    e_index = int(easting/1000)
    n_index = int(northing/1000)

    if n_index >= len(ostn_data):
        return None

    lo_shifts = get_ostn_pair(e_index, n_index) 
    if lo_shifts is None:
        return None

    hi_shifts = get_ostn_pair(e_index, n_index+1) 
    if hi_shifts is None:
        return None

    t = easting/1000 - e_index # offset within square
    u = northing/1000 - n_index

    f0 = (1-t)*(1-u)
    f1 =    t *(1-u)
    f2 = (1-t)*   u 
    f3 =    t *   u 

    se = f0*lo_shifts[0] + f1*lo_shifts[2] + f2*hi_shifts[0] + f3*hi_shifts[2]
    sn = f0*lo_shifts[1] + f1*lo_shifts[3] + f2*hi_shifts[1] + f3*hi_shifts[3]

    return (se, sn)

def llh_to_cartesian(lat, lon, H, model):

    a,b,f,ee = ellipsoid_models[model]

    phi = lat / 57.29577951308232087679815481410517
    sp = math.sin(phi)
    cp = math.cos(phi)
    lam = lon / 57.29577951308232087679815481410517
    sl = math.sin(lam)
    cl = math.cos(lam)

    nu = a / math.sqrt(1 - ee*sp*sp)

    x = (nu+H) * cp * cl
    y = (nu+H) * cp * sl
    z = ((1-ee)*nu+H)*sp

    return (x,y,z)


def cartesian_to_llh(x, y, z, model):

    a,b,f,ee = ellipsoid_models[model]

    p = math.sqrt(x*x+y*y)
    lam = math.atan2(y, x)
    phi = math.atan2(z, p*(1-ee))

    while True:
        sp = math.sin(phi)
        nu = a / math.sqrt(1 - ee*sp*sp)
        oldphi = phi
        phi = math.atan2(z+ee*nu*sp, p)
        if abs(oldphi-phi) < 1E-12:
            break
     
    lat = phi * 57.29577951308232087679815481410517
    lon = lam * 57.29577951308232087679815481410517
    H = p/math.cos(phi) - nu
    return (lat, lon, H)

def small_Helmert_transform_for_OSGB(direction, xa, ya, za):
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
    (xa, ya, za) = llh_to_cartesian(lat, lon, 0, 'OSGB36' )
    (xb, yb, zb) = small_Helmert_transform_for_OSGB(-1,xa, ya, za)
    (latx, lonx, junk) = cartesian_to_llh(xb, yb, zb, 'WGS84')
    return (latx, lonx)


def shift_ll_from_wgs84_to_osgb36(lat, lon):
    (xa, ya, za) = llh_to_cartesian(lat, lon, 0, 'WGS84')
    (xb, yb, zb) = small_Helmert_transform_for_OSGB(+1,xa, ya, za)
    (latx, lonx, junk) = cartesian_to_llh(xb, yb, zb, 'OSGB36')
    return (latx, lonx)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
