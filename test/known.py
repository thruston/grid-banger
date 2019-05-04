#! /usr/bin/env python3

import argparse
import osgb


if __name__ == "__main__":

    expected = (52+39/60+27.2531/3600, 1+43/60+4.5177/3600)

    got = osgb.grid_to_ll(651409.903, 313177.270, 'OSGB36')

    print(expected)
    print(got)
    
