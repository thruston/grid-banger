#! /usr/bin/env python3

import argparse
import math

import osgb


def scaled(n):
    return round(n/300)

def mpair(x, y):
    return f'({scaled(x)},{scaled(y)})'

def make_path(lop):
    out = []
    for p in lop[:-1]:
        out.append(mpair(*p))

    return '--'.join(out) + '--cycle'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a GR and a map series, print a useful map")
    parser.add_argument("gridref", nargs='+')
    parser.add_argument("--series", default="A")

    args = parser.parse_args()

    e, n = osgb.parse_grid(' '.join(args.gridref))
    maps = osgb.sheet_keys(e, n, args.series)
    radius = 5000  # 5km round the point
    for t in range(8):
        maps.extend(osgb.sheet_keys(e + radius * math.cos(0.78539816 * t), n + radius * math.sin(0.78539816 * t), args.series))

    print('''prologues := 3; outputtemplate := "%j.%{outputformat}"; defaultfont:="phvr8r"; beginfig(1);''')

    for k in set(maps):
        m = osgb.get_sheet(k)
        print(f'draw {make_path(m.polygon)};')
        print(f'pair p; p = 1/2[{mpair(*m.bbox[0])},{mpair(*m.bbox[1])}];')
        if 'OL' in k:
            print('p := p shifted 12 up;')
        print(f'label("{k}", p);')

    print(f'''dotlabel.lrt("{' '.join(args.gridref)}" infont defaultfont scaled 0.8, {mpair(e,n)}) withcolor .67 blue;''')

    print('endfig;end.')


