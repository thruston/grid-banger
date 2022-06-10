#! /usr/bin/env python3

import argparse
import collections
import json
import re

import osgb


def inline_coordinates(js):
    "Make all the coordinate lines in-line"
    js = re.sub(r"\[\s*\n\s+(-?\d+\.\d+),\n\s+(\d+\.\d+)\n\s+\],\n\s+", r"[\1,\2],", js)
    js = re.sub(r"\[\s*\n\s+(-?\d+\.\d+),\n\s+(\d+\.\d+)\n\s+\]", r"[\1,\2]", js)
    return js


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--series", default="A", help="Which map series? A: Landranger, B: Explorer, C: One-inch, ...")
    args = parser.parse_args()

    jason = {
        'type': 'FeatureCollection',
        'features': [],
    }

    polygons = collections.defaultdict(list)
    titles = dict()

    # Note that contrary to ISO 6709 GeoJSON wants lon before lat

    for k, m in osgb.map_locker.items():
        if m.series == args.series:
            p = [list(reversed(osgb.grid_to_ll(e, n))) for e, n in m.polygon]
            polygons[m.number].append([p])
            if m.parent == '':
                titles[m.number] = m.title

    # Polygon is an array of linear ring arrays
    # first is the ccw container, second and any subsequent are the clockwise holes
    # for maps there are *no* holes, so all Polygons are an array of one array.

    # Multipolygons are an array of Polygons, we use them for sheets with more than 
    # one sheet

    for k in sorted(polygons):
        p = polygons[k]

        if len(p) > 1:
            geo = {'type': 'MultiPolygon', 'coordinates': p}
        else:
            geo = {'type': 'Polygon', 'coordinates': p[0]}

        jason['features'].append({
            'type': 'Feature',
            'id': k,
            'properties': {
                'series': osgb.name_for_map_series[args.series],
                'sheet': k,
                'title': titles[k]
            },
            'geometry': geo
        })

    print(inline_coordinates(json.dumps(jason, indent=4)))
