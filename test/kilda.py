#! /usr/bin/env python3

import argparse
import osgb
import math


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--putsomethinghere")
    args = parser.parse_args()

    print('''
prologues := 3;
outputtemplate := "%j%c.eps";
beginfig(1);
''')

    
    for n in range(1200500, 500, -10000):
        for e in range(500, 700000, 10000):
            lat, lon = osgb.grid_to_ll(e, n)
            ee, nn = osgb.ll_to_grid(lat, lon)
            de = ee-e
            dn = nn-n
            hh = math.sqrt(de*de + dn*dn)

            #print('{:.3f}'.format(hh*100), end=' ')
            if hh > 0:
                print('drawdot ({}, {}) withpen pencircle scaled 4 withcolor {}[white, red];'.format(e/1000, n/1000, hh*100))
        print()


    for lat in range(50, 61):
        print('draw')
        for lon in range(-9, 2):
            (e, n) = osgb.ll_to_grid(lat, lon)
            print('({}, {})..'.format(e/1000, n/1000))
            print('%', lat, lon, e, n)
        (e, n) = osgb.ll_to_grid(lat, 2)
        print('({}, {});'.format(e/1000, n/1000))
    
    for lon in range(-8, 3):
        print('draw')
        for lat in range(50, 61):
            (e, n) = osgb.ll_to_grid(lat, lon)
            print('({}, {})..'.format(e/1000, n/1000))
            print('%', lat, lon, e, n)
        (e, n) = osgb.ll_to_grid(61, lon)
        print('({}, {});'.format(e/1000, n/1000))


    print('endfig; end.')

