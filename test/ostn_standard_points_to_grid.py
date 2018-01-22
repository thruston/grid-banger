#! /usr/bin/env python3

import argparse
import csv
import osgb


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose")
    args = parser.parse_args()

    test_input = dict()
    expected_output = dict()
    with open('test/OSTN15_OSGM15_TestInput_ETRStoOSGB.txt') as input:
        reader = csv.DictReader(input)
        for r in reader:
            test_input[r['PointID']] = (float(r['ETRS89 Latitude']), float(r['ETRS Longitude']))

    with open('test/OSTN15_OSGM15_TestOutput_ETRStoOSGB.txt') as output:
        reader = csv.DictReader(output)
        for r in reader:
            expected_output[r['PointID']] = (float(r['OSGBEast']), float(r['OSGBNorth']))

    for k in sorted(test_input):
        assert( osgb.ll_to_grid(*test_input[k]) == expected_output[k]) 



# OSTN15_OSGM15_TestInput_OSGBtoETRS.txt
# OSTN15_OSGM15_TestOutput_ETRStoOSGB.txt
# OSTN15_OSGM15_TestOutput_OSGBtoETRS.txt
