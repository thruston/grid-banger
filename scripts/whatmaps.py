#! /usr/bin/env python3
"""
Toby Thurston -- 24 Apr 2018 

Take a GPX file (route, track, etc), and find all the maps needed to cover it.

"""
from __future__ import division, print_function

import argparse
import gpxpy
import osgb
import collections

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gpxfile", help="The name of your GPX file")
    parser.add_argument("--series", default="A", help="Which map series? A: Landranger, B: Explorer, C: One-inch, ...")
    parser.add_argument("--name", action="store_true", help="Show name of the series")
    parser.add_argument("--title", action="store_true", help="Show the title of the map")
    parser.add_argument("--coverage", action="store_true", help="Show how many of the points are covered by each map")

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
        maps.extend(osgb.sheet_list(*osgb.ll_to_grid(p.latitude, p.longitude), series=args.series))
            
    c = collections.Counter(maps)
    for map in sorted(c):
        out = list()
        if args.name:
            k, sheet = map.split(':')
            out.append('{} {}'.format(osgb.mapping.name_for_map_series[k], sheet))
        else:
            out.append(map)
        if args.title:
            out.append('"' + osgb.mapping.map_locker[map]['title'] + '"')
        if args.coverage:
            out.append("({}%)".format(int(100*c[map]/len(points))))
        print(' '.join(out))


