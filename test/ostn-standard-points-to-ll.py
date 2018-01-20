#! /usr/bin/env python3
from __future__ import print_function, division

import argparse
import csv
import math
import osgb

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose")
    args = parser.parse_args()

    test_input = dict()
    expected_output = dict()
    results = dict()

    with open('test/OSTN15_OSGM15_TestInput_OSGBtoETRS.txt') as input:
        reader = csv.DictReader(input)
        for r in reader:
            test_input[r['PointID']] = (float(r['OSGB36 Eastings']), float(r['OSGB36 Northing']))

    with open('test/OSTN15_OSGM15_TestOutput_OSGBtoETRS.txt') as output:
        reader = csv.DictReader(output)
        for r in reader:
            if r['Iteration No./RESULT'] == 'RESULT':
                expected_output[r['PointID']] = (float(r['ETRSEast/Lat']), float(r['ETRSNorth/Long']))
            
    for k in sorted(test_input):
        (lat, lon) = osgb.grid_to_ll(*test_input[k])
        one_lat_in_mm = 111132954 - 559822 * math.cos(2*math.radians(lat)) + 1175 * math.cos(4*math.radians(lat))
        one_lon_in_mm = 1000*(3.141592653589793/180)*(6378137*math.cos(math.radians(lat)))/math.sqrt(1-0.006694380004260827*math.sin(lat)**2)

        delta_lat = lat-expected_output[k][0]
        delta_lon = lon-expected_output[k][1]

        delta_lat_mm = delta_lat * one_lat_in_mm
        delta_lon_mm = delta_lon * one_lon_in_mm

        try:
            assert(abs(delta_lat_mm) < 0.014);
        except AssertionError:
            print(k, delta_lat_mm)
        try:
            assert(abs(delta_lon_mm) < 0.007);
        except AssertionError:
            print(k, delta_lon_mm)
