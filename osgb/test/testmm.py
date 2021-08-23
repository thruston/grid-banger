#! /usr/bin/env python3
from __future__ import print_function, division

import argparse
import osgb


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--diff", type=int)
    parser.add_argument("-a", "--lat", action='store_true')
    args = parser.parse_args()

    d = 10 ** -args.diff if args.diff else 0.1;
    print("{:g} difference in lat+lon makes this difference in metres...".format(d))

    for lat in range(60,49,-1):
        print(lat, end = ':')
        for lon in range(-8, 2):
            (e, n)   = osgb.ll_to_grid(lat, lon)
            (ee, nn) = osgb.ll_to_grid(lat+d, lon+d)
            if args.lat:
                print('{:.3f}'.format(nn-n), end= '  ')
            else:
                print('{:.3f}'.format(ee-e), end= '  ')

        print()
                    

    # Approx answers: 5 places 0.00001 lat = 1m, long < 1m
    #                 8 places 0.00000001 lat = 1mm,  lat < 1mm
