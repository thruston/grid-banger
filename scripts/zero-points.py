#! /usr/bin/env python3
'''This script shows all the points with "all zero" grid references
that are on a map sheet.  For background, look at the WP entry for
"Beast Cliff", which is point OV 000 000.

The only argument is "series" which defines what map series to use.
The default is A which means "OS Landranger" only.

If you are planning on a visit to any of them, beware that some of them
are in the sea.
'''

import argparse

import osgb

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", default='A', help='Which map series?')
    args = parser.parse_args()

    for n in range(13):
        for e in range(8):
            easting = e * 100000
            northing = n * 100000
            maps = osgb.sheet_keys(easting, northing, series=args.series)
            if maps:
                gr = osgb.format_grid(easting, northing)
                for m in maps:
                    s = osgb.get_sheet(m)
                    main_title = s.title.split('(')[0].strip()
                    print(gr, 'on', m, main_title)
