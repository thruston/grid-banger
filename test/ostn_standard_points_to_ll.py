#! /usr/bin/env python3
"""Test routine for OSGB conversions.

Check that we can transform OSGB test grid refs into the given OSGB lat/lons
with an error of less that 0.02 mm

Toby Thurston -- 22 Jan 2018 
"""
from __future__ import print_function, division

import argparse
import csv
import math
import osgb

# pylint: disable=C0103

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    test_input = dict()
    expected_output = dict()
    results = dict()

    with open('test/OSTN15_OSGM15_TestInput_OSGBtoETRS.txt') as test_input_data:
        reader = csv.DictReader(test_input_data)
        for r in reader:
            test_input[r['PointID']] = (float(r['OSGB36 Eastings']), float(r['OSGB36 Northing']))

    with open('test/OSTN15_OSGM15_TestOutput_OSGBtoETRS.txt') as test_output_data:
        reader = csv.DictReader(test_output_data)
        for r in reader:
            if r['Iteration No./RESULT'] != 'RESULT':
                continue
            expected_output[r['PointID']] = (float(r['ETRSEast/Lat']), float(r['ETRSNorth/Long']))

    acceptable_error_mm = 0.02

    for k in sorted(test_input):
        (lat, lon) = osgb.grid_to_ll(*test_input[k])
        phi = math.radians(lat)
        one_lat_in_mm = 111132954 - 559822 * math.cos(2 * phi) + 1175 * math.cos(4 * phi)
        one_lon_in_mm = 1000 * (3.141592653589793 / 180) * (6378137 * math.cos(phi)) / math.sqrt(1 - 0.006694380004260827 * math.sin(phi) ** 2)

        delta_lat = lat-expected_output[k][0]
        delta_lon = lon-expected_output[k][1]

        delta_lat_mm = delta_lat * one_lat_in_mm
        delta_lon_mm = delta_lon * one_lon_in_mm

        if args.verbose:
            print('Test point {}  dLat: {:+.3f} mm  dLon: {:+.3f} mm'.format(k, delta_lat_mm, delta_lon_mm))

        try:
            assert abs(delta_lat_mm) < acceptable_error_mm
        except AssertionError:
            print(k, delta_lat_mm)

        try:
            assert abs(delta_lon_mm) < acceptable_error_mm
        except AssertionError:
            print(k, delta_lon_mm)
