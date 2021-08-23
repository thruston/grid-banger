#! /usr/bin/env python3

"""Convert coordinates.

Toby Thurston -- 04 Jul 2021
"""
# allow free variable names and the occasional trailing whitespace character
# pylint: disable=C0103, C0303
from __future__ import print_function, division

import argparse
import random
import re
import webbrowser

import osgb


def get_likely_lon_lat(possible_number):
    "Is this supposed to be a lat or lon coordinate?"
    try:
        actual_number = float(possible_number)
    except ValueError:
        return None

    if -20 < actual_number < 70:  # Useful Lat is between 49 and 65, useful Lon between -9 and 2
        return actual_number  # and it's OK to return 0 - see below

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert coordinates to and from OSGB grid refs and lat/lon.")
    parser.add_argument("--random", action="store_true", help="Pick a place at random")
    parser.add_argument("--show", action='store_true', help="Show this place on Streetview.co.uk")
    parser.add_argument("grid_or_ll_element", type=str, nargs='*', default=['SP', '101', '203'],
                        help="A grid reference string or lat/lon pair.")
    args = parser.parse_args()

    if args.random:
        map = random.choice(list(S for S in osgb.map_locker.values() if S.series == 'A'))
        e = random.randint(map.bbox[0][0], map.bbox[1][0])
        n = random.randint(map.bbox[0][1], map.bbox[1][1])
        agenda = osgb.format_grid(e, n)

    else:
        agenda = ' '.join(args.grid_or_ll_element)
        alphabet = ' 1234567890-.+/:ABCDEFGHJKLMNOPQRSTUVWXYZabcdef'  # there is no I in this
        agenda = agenda.replace(',', ' ')  # treat commas as spaces
        agenda = ''.join(x for x in agenda if x in alphabet)  # and remove unwanted characters

    m = re.match(r'([456]\d) ([012345]?\d) ([012345]?\d) N (\d) ([012345]?\d) ([012345]?\d) ([EW])', agenda)
    if m is not None:
        (ha, ma, sa, hb, mb, sb, hemi) = m.groups()
        latlon = [int(ha) + int(ma) / 60 + int(sa) / 3600, (int(hb) + int(mb) / 60 + int(sb) / 3600)]
        if hemi == 'W':
            latlon[1] = -latlon[1]
    else:
        latlon = list(get_likely_lon_lat(x) for x in agenda.split())

    # if the arguments consists of just two likely looking numbers...
    # You can't just say "all(floats)" because 0 is a valid Longitude
    if len(latlon) == 2 and all(x is not None for x in latlon):
        (lon, lat) = sorted(latlon)  # Lon is always less than Lat in OSGB
        (e, n) = osgb.ll_to_grid(lat, lon)
        (olat, olon) = (lat, lon)
        (oe, on) = osgb.ll_to_grid(lat, lon, 'OSGB36')

    else:
        print('>>', agenda)
        (e, n) = osgb.parse_grid(agenda)
        (lat, lon) = osgb.grid_to_ll(e, n)
        (oe, on) = (e, n)
        (olat, olon) = osgb.grid_to_ll(e, n, 'OSGB36')

    try:
        grid = osgb.format_grid(e, n)
        maps = osgb.sheet_keys(e, n)
    except osgb.gridder.Error:
        grid = '??'
        maps = None

    if maps:
        map_string = 'on sheets {}'.format(', '.join(maps))
    else:
        map_string = '(not covered by any OSGB map)'

    print('WGS84  {:.8f} {:.7f}'.format(lat, lon), end=' ')
    print('== {:.3f} {:.3f}'.format(e, n), end=' ')
    print('== {} {}'.format(grid, map_string))

    try:
        grid = osgb.format_grid(oe, on)
        maps = osgb.sheet_keys(oe, on)
    except osgb.gridder.Error:
        grid = '??'
        maps = None

    if maps:
        map_string = 'on sheets {}'.format(', '.join(maps))
    else:
        map_string = '(not covered by any OSGB map)'

    print('OSGB36 {:.8f} {:.7f}'.format(olat, olon), end=' ')
    print('== {:.3f} {:.3f}'.format(oe, on), end=' ')
    print('== {} {}'.format(grid, map_string))

    if args.show:
        url = 'http://www.streetmap.co.uk/map.srf?x={:06d}&y={:06d}&z=3'.format(int(e), int(n))
        webbrowser.open(url)
