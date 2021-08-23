#! /usr/bin/env python3
"""
Toby Thurston -- 24 Apr 2018

Take a GPX file (route, track, etc), and find all the maps needed to cover it.

"""
# pylint: disable=C0103
from __future__ import division, print_function

import argparse
import collections

import gpxpy
import osgb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all the maps needed to cover a route or track in the GPX file")
    parser.add_argument("gpxfile", help="The name of your GPX file")
    parser.add_argument("--series", default="A",
                        help="Which map series? A: Landranger, B: Explorer, C: One-inch, ...")
    parser.add_argument("--name", action="store_true", help="Show name of the series")
    parser.add_argument("--title", action="store_true", help="Show the title of the map")
    parser.add_argument("--coverage", action="store_true",
                        help="Show how many of the points are covered by each map")

    args = parser.parse_args()

    with open(args.gpxfile) as g:
        gpx = gpxpy.parse(g)

    points = list()
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(point)

    for point in gpx.waypoints:
        points.append(point)

    for route in gpx.routes:
        for point in route.points:
            points.append(point)

    maps = list()
    for p in points:
        maps.extend(osgb.sheet_keys(*osgb.ll_to_grid(p.latitude, p.longitude), series=args.series))

    c = collections.Counter(maps)
    for map_key in sorted(c):
        out = list()
        if args.name:
            k, sheet = map_key.split(':')
            out.append('{} {}'.format(osgb.name_for_map_series[k], sheet))
        else:
            out.append(map_key)
        if args.title:
            out.append('"' + osgb.map_locker[map_key].title + '"')
        if args.coverage:
            out.append("({}%)".format(int(100*c[map_key]/len(points))))
        print(' '.join(out))
