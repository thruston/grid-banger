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

test_input = dict()
expected_output = dict()
results = dict()

with open('osgb/test/OSTN15_OSGM15_TestInput_OSGBtoETRS.txt') as test_input_data:
    reader = csv.DictReader(test_input_data)
    for r in reader:
        test_input[r['PointID']] = (float(r['OSGB36 Eastings']), float(r['OSGB36 Northing']))

with open('osgb/test/OSTN15_OSGM15_TestOutput_OSGBtoETRS.txt') as test_output_data:
    reader = csv.DictReader(test_output_data)
    for r in reader:
        if r['Iteration No./RESULT'] != 'RESULT':
            continue
        expected_output[r['PointID']] = (float(r['ETRSEast/Lat']), float(r['ETRSNorth/Long']))


def test_all(chatty=False):
    acceptable_error_mm = 0.02
    for k in sorted(test_input):
        (lat, lon) = osgb.grid_to_ll(test_input[k], rounding=10)
        phi = math.radians(lat)
        one_lat_in_mm = 111132954 - 559822 * math.cos(2 * phi) + 1175 * math.cos(4 * phi)
        one_lon_in_mm = 111319490.79327355 * math.cos(phi) / math.sqrt(1 - 0.006694380004260827 * math.sin(phi) ** 2)

        delta_lat = lat-expected_output[k][0]
        delta_lon = lon-expected_output[k][1]

        delta_lat_mm = delta_lat * one_lat_in_mm
        delta_lon_mm = delta_lon * one_lon_in_mm

        if chatty:
            print('Test point {}  dLat: {:+.3f} mm  dLon: {:+.3f} mm'.format(k, delta_lat_mm, delta_lon_mm))

        assert abs(delta_lat_mm) < acceptable_error_mm
        assert abs(delta_lon_mm) < acceptable_error_mm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    test_all(args.verbose)
