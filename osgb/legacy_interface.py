# Compatibility with old osgb interface
import osgb


def lonlat_to_osgb(lon, lat, digits=3, formatted=True, model='OSGB36'):
    """Convert a longitude and latitude to Ordnance Survey grid reference.

    :Parameters:
        lon
            Longitude, assumed to be in OSGB36 degrees
            (unless you set model='WGS84').

        lat
            Latitude, ditto.

        digits
            The number of digits to use for each direction in the final grid reference. Default 3.

        formatted
            Should the OSGB reference be nicely formatted (with whitespace)? Default true.

        model
            'OSGB36' or 'WGS84', default 'OSGB36'

    :Returns:
        A string giving a formatted OSGB reference.

    For example::

        >>> print(lonlat_to_osgb(1.088978, 52.129892))
        TM 114 525
        >>> print(lonlat_to_osgb(1.088978, 52.129892, formatted=False))
        TM114525
        >>> print(lonlat_to_osgb(1.088978, 52.129892, 5))
        TM 11400 52500

    In the re-implemented version you can reverse arguments if you want to...

    >>> print(lonlat_to_osgb(52.129892, 1.088978, 5))
    TM 11400 52500


    """
    east, north = osgb.ll_to_grid(lat, lon, model=model)

    if formatted:
        format_spec = ' '.join(['SS', 'E' * digits, 'N' * digits])
    else:
        format_spec = ''.join(['SS', 'E' * digits, 'N' * digits])

    return osgb.format_grid(east, north, form=format_spec)


def osgb_to_lonlat(osgb_str, model='OSGB36'):
    """
    Convert an Ordinance Survey reference to a longitude and latitude.

    :Parameters:
            osgb_str
                    An Ordnance Survey grid reference in "letter-number" format.
                    Case and spaces are cleaned up by this function, and resolution
                    automatically detected, so that so that ``TM114 525``, ``TM114525``,
                    and ``TM 11400 52500`` are all recognised and identical.

            model
                    'OSGB36' or 'WGS84'.  Default 'OSGB36'.

    :Returns:
            The longitude and latitude of the grid reference, according to the chosen model.

    For example::

            # just outside Ipswich, about 1.088975 52.129892
            >>> osgb_to_lonlat('TM114 525')
            (1.088975, 52.129892)

            # accepts poor formating
            >>> osgb_to_lonlat(' TM 114525 ')
            (1.088975, 52.129892)

            # accepts higher resolution
            >>> osgb_to_lonlat('TM1140052500')
            (1.088975, 52.129892)

    """
    return tuple(reversed(osgb.grid_to_ll(osgb.parse_grid(osgb_str), model=model)))
