#! /usr/bin/env python3
"""Test routine for OSGB conversions.

Check that we can transform OSGB test lat/longs into the given OSGB grid refs
which are rounded to the nearest mm, so should match exactly.

Toby Thurston -- 23 Jan 2018
"""
from __future__ import print_function, division

import argparse
import csv
import osgb
import pytest

# pylint: disable=C0103

test_input = dict()
expected_output = dict()
with open('test/OSTN15_OSGM15_TestInput_ETRStoOSGB.txt') as test_input_file:
    reader = csv.DictReader(test_input_file)
    for r in reader:
        test_input[r['PointID']] = (float(r['ETRS89 Latitude']), float(r['ETRS Longitude']))

with open('test/OSTN15_OSGM15_TestOutput_ETRStoOSGB.txt') as test_output_file:
    reader = csv.DictReader(test_output_file)
    for r in reader:
        expected_output[r['PointID']] = (float(r['OSGBEast']), float(r['OSGBNorth']))

def test_all(chatty=False):
    for k in sorted(test_input):
        gr = osgb.ll_to_grid(*test_input[k])
        if chatty:
            print("Exp:", expected_output[k])
            print("Got:", gr)
            print()
        assert gr == expected_output[k]
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    test_all(args.verbose)


