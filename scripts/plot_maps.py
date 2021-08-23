'''Print a map of the National Grid, optionally with an index of OS maps'''
from __future__ import print_function, division

import argparse
import math
import os
import pkgutil
import subprocess
import sys
import tempfile
import textwrap

import osgb


def does_not_overlap_parent(key):
    "See if an inset overlaps the parent sheet"
    inset = osgb.map_locker[key]
    parent = osgb.map_locker[inset.parent]
    return (inset.bbox[0][0] > parent.bbox[1][0]
            or inset.bbox[1][0] < parent.bbox[0][0]
            or inset.bbox[1][1] < parent.bbox[0][1]
            or inset.bbox[0][1] > parent.bbox[1][1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='plot_maps',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="Toby Thurston -- August 2021",
                                     description=textwrap.dedent('''
    plot_maps - make a nice index sheet for a map series.

    If you have a working TeXLive installation with MetaPost and GhostScript installed,
    you can use it to produce PDF index maps of the various map series included.'''))

    parser.add_argument('--series', type=str, choices='ABCHJ', help='Show map series')
    parser.add_argument('--paper', type=str.upper, choices=('A0', 'A1', 'A2', 'A3', 'A4'),
                        default='A3', help='Output paper size')
    parser.add_argument('--pdf', type=str, help="Write to this file")
    parser.add_argument('--towns', action='store_true', help="Show some town names")
    parser.add_argument('--tests', action='store_true', help="Show the OSGB test locations")
    parser.add_argument('--error', action='store_true', help="Show an indication of the round trip error")
    parser.add_argument('--nogrid', action='store_true', help="Don't show the grid")
    parser.add_argument('--nograt', action='store_true', help="Don't show the latitude / longitude graticule")
    parser.add_argument('--nocoast', action='store_true', help="Don't show the coast lines")
    parser.add_argument('--nomp', action='store_true', help="Don't try to run MP")
    args = parser.parse_args()

    # Where shall we put the output?
    if args.pdf:
        pdffile = args.pdf
    else:
        if args.series:
            pdffile = "Index_for_map_series_{}.pdf".format(args.series)
        else:
            pdffile = "National_grid.pdf"

    # Set the scale according to the chosen paper size
    scale = {'A4': 1680, 'A3': 1189, 'A2': 840, 'A1': 597, 'A0': 420}[args.paper]

    # gather all the paths we will need from the map locker polygons
    path_for = dict()  # a list of the actual MP maps
    sides = list()  # a list of keys to path_for
    insets = list()  # another list of (different) keys to path_for
    if args.series:
        for k, sheet in osgb.map_locker.items():
            # Skip maps not wanted
            if k[:1] not in args.series:
                continue

            # make the polygon into an MP path
            path_for[k] = '--'.join('({:.1f}, {:.1f})'.format(x[0]/scale, x[1]/scale)
                                    for x in sheet.polygon[:-1]) + '--cycle'
            # append the key to the appropriate list
            if sheet.parent == '':
                sides.append(k)
            else:
                insets.append(k)

    # MP rgbcolor tuples
    color_for = {
        'A': '(224/255, 36/255, 114/255)',  # Landranger pink
        'B': '(221/255, 61/255, 31/255)',  # Explorer orange
        'C': '(228/255, 0, 28/255)',  # Seventh series red
        'H': '(128/255, 4/255, 36/255)',  # Harvey dark red
        'J': '(128/255, 4/255, 36/255)',  # Harvey dark red
    }

    # open a tempory file for MP
    plotter = tempfile.NamedTemporaryFile(mode='wt', prefix='plot_maps_', suffix='.mp', dir='.', delete=False)

    # Starting making the MP file
    print('prologues := 3; outputtemplate := "%j.eps"; beginfig(1); defaultfont := "phvr8r";', file=plotter)

    # sides and insets will have anything in if we chose one or more series
    for k in sides + insets:
        print("fill {} withcolor (0.98, 0.906, 0.71);".format(path_for[k]), file=plotter)

    if args.error:
        for x in range(70):
            e = x * 10000 + 5000
            for y in range(125):
                n = y * 10000 + 5000
                (ee, nn) = osgb.ll_to_grid(*osgb.grid_to_ll(e, n))
                h = math.sqrt((e-ee)**2+(n-nn)**2)
                if h > 0:
                    print('drawdot ({:.1f}, {:.1f})'.format(e/scale, n/scale), file=plotter)
                    print(' withpen pencircle scaled 4 withcolor {:.2f}[white, red];'.format(h*100), file=plotter)

        print('label.rt("Round trip error (mm)" infont defaultfont scaled 0.6,', file=plotter)
        print('({:.1f}, {:.1f}));'.format(-176500/scale, 1255000/scale), file=plotter)
        for i in range(6):
            e = -120000 - i * 10000
            n = 1245000
            print('drawdot ({:.1f}, {:.1f})'.format(e/scale, n/scale), file=plotter)
            print(' withpen pencircle scaled 4 withcolor {:.2f}[white, red];'.format(i/5), file=plotter)
            print('label.bot("{}" infont defaultfont scaled 0.6,'.format(2*i), file=plotter)
            print('({:.1f}, {:.1f}));'.format(e/scale, n/scale-2), file=plotter)

    if not args.nograt:
        print("drawoptions(withpen pencircle scaled 0.4);", file=plotter)
        for lon in range(-10, 3):
            points = []
            for decilat in range(496, 613):
                e, n = osgb.ll_to_grid(decilat/10, lon)
                points.append('({:.1f}, {:.1f})'.format(e/scale, n/scale))

            print('draw ' + '--'.join(points) + ' withcolor .7[.5 green, white];', file=plotter)
            print('label.bot("{}" & char 176, {}) withcolor .4 green;'.format(lon, points[0]), file=plotter)

        for lat in range(50, 62):
            points = []
            for decilon in range(-102, 23):
                e, n = osgb.ll_to_grid(lat, decilon/10)
                points.append('({:.1f}, {:.1f})'.format(e/scale, n/scale))

            print('draw ' + '--'.join(points) + ' withcolor .7[.5 green, white];', file=plotter)
            print('label.lft("{}" & char 176, {}) withcolor .4 green;'.format(lat, points[0]), file=plotter)

    if not args.nogrid:
        print('drawoptions(withcolor .7 white);', file=plotter)
        print('z0=({:g}, {:g});'.format(700000/scale, 1250000/scale), file=plotter)
        print('label.llft("0", origin) withcolor .5 white;', file=plotter)

        for i in range(8):
            e = i*100000
            print('t:={:g};draw (t, 0) -- (t, y0);'.format(e/scale), file=plotter)
            if i > 0:
                print('label.bot("{:d}", (t, 0)) withcolor .5 white;'.format(i*100), file=plotter)
            for j in range(13):
                n = j*100000
                if i == 0:
                    print('t:={:g};draw (0, t) -- (x0, t);'.format(n/scale), file=plotter)
                    if j > 0:
                        print('label.lft("{:d}", (0, t)) withcolor .5 white;'.format(j*100), file=plotter)

                if i < 7 and j < 12:
                    sq = osgb.format_grid(e, n, form='SS')
                    print('label("{}" infont "phvr8r" scaled {},'.format(sq, 3600/scale), file=plotter)
                    print('({:.1f}, {:.1f})) withcolor 3/4;'.format((e+50000)/scale, (n+50000)/scale), file=plotter)
        # add HP as well
        print('label("HP" infont "phvr8r" scaled {},'.format(3600/scale), file=plotter)
        print('({:.1f}, {:.1f})) withcolor 3/4;'.format((450000)/scale, (1250000)/scale), file=plotter)

    if not args.nocoast:
        coast_shapes = pkgutil.get_data('osgb', 'gb_coastline.shapes')
        if coast_shapes:
            print("drawoptions(withpen pencircle scaled 0.2 withcolor (0, 172/255, 226/255));", file=plotter)
            poly_path = list()
            for line in coast_shapes.split(b'\n'):
                if line.startswith(b'#'):
                    print('draw ' + '--'.join(poly_path) + ';', file=plotter)
                    del poly_path[:]
                elif line:
                    try:
                        (lon, lat) = (float(x) for x in line.split())
                    except ValueError:
                        print('????', line)
                    (e, n) = osgb.ll_to_grid(lat, lon)
                    poly_path.append('({:.1f}, {:.1f})'.format(e/scale, n/scale))

            assert not poly_path

    if args.towns:
        towns = {
            'Aberdeen': (392500, 806500),
            'Birmingham': (409500, 287500),
            'Bristol': (360500, 175500),
            'Cambridge': (546500, 258500),
            'Canterbury': (614500, 157500),
            'Cardiff': (318500, 176500),
            'Carlisle': (339500, 555500),
            'Edinburgh': (327500, 673500),
            'Glasgow': (259500, 665500),
            'Inverness': (266500, 845500),
            'Leeds': (430500, 434500),
            'Liverpool': (337500, 391500),
            'London': (531500, 181500),
            'Manchester': (383500, 398500),
            'Newcastle': (425500, 564500),
            'Oxford': (451500, 206500),
            'Plymouth': (247500, 56500),
            'Portsmouth': (465500, 101500),
            'Salisbury': (414500, 130500),
            'Sheffield': (435500, 387500),
            'Worcester': (385500, 255500),
        }

        print("drawoptions(withcolor .7 white);defaultscale := 1/2;", file=plotter)
        for t in towns:
            e, n = towns[t]
            print('dotlabel.top("{}", ({:.1f}, {:.1f}));'.format(t, e/scale, n/scale), file=plotter)

    if args.tests:
        points = {
            'TP01': (91492.146, 11318.803, "St Mary's, Scilly"),
            'TP02': (170370.718, 11572.405, "Lizard Point Lighthouse"),
            'TP03': (250359.811, 62016.569, "Plymouth"),
            'TP04': (449816.371, 75335.861, "St Catherine's Point Lighthouse"),
            'TP05': (438710.92, 114792.25, "Former OSHQ"),
            'TP06': (292184.87, 168003.465, "Nash Point Lighthouse"),
            'TP07': (639821.835, 169565.858, "North Foreland Lighthouse"),
            'TP08': (362269.991, 169978.69, "Brislington"),
            'TP09': (530624.974, 178388.464, "Lambeth"),
            'TP10': (241124.584, 220332.641, "Carmarthen"),
            'TP11': (599445.59, 225722.826, "Colchester"),
            'TP12': (389544.19, 261912.153, "Droitwich"),
            'TP13': (474335.969, 262047.755, "Northampton"),
            'TP14': (562180.547, 319784.995, "King's Lynn"),
            'TP15': (454002.834, 340834.943, "Nottingham"),
            'TP16': (357455.843, 383290.436, "STFC, Daresbury"),
            'TP17': (247958.971, 393492.909, "Point Lynas Lighthouse, Anglesey"),
            'TP18': (247959.241, 393495.583, "Point Lynas Lighthouse, Anglesey"),
            'TP19': (331534.564, 431920.794, "Blackpool Airport"),
            'TP20': (422242.186, 433818.701, "Pudsey"),
            'TP21': (227778.33, 468847.388, "Isle of Man airport"),
            'TP22': (525745.67, 470703.214, "Flamborough Head"),
            'TP23': (244780.636, 495254.887, "Ramsey, Isle of Man"),
            'TP24': (339921.145, 556034.761, "Carlisle"),
            'TP25': (424639.355, 565012.703, "Newcastle University"),
            'TP26': (256340.925, 664697.269, "Glasgow"),
            'TP27': (319188.434, 670947.534, "Sighthill, Edinburgh"),
            'TP28': (167634.202, 797067.144, "Mallaig Lifeboat Station"),
            'TP29': (397160.491, 805349.736, "Girdle Ness Lighthouse"),
            'TP30': (267056.768, 846176.972, "Inverness"),
            'TP31': (9587.909, 899448.986, "Hirta, St Kilda"),
            'TP32': (71713.132, 938516.4, "at sea, 7km S of Flannan"),
            'TP33': (151968.652, 966483.779, "Butt of Lewis lighthouse"),
            'TP34': (299721.891, 967202.992, "Dounreay Airfield"),
            'TP35': (330398.323, 1017347.016, "Orkney Mainland"),
            'TP36': (261596.778, 1025447.602, "at sea, 1km NW of Sule Skerry"),
            'TP37': (180862.461, 1029604.114, "at sea, 3km south of Rona"),
            'TP38': (421300.525, 1072147.239, "Fair Isle"),
            'TP39': (440725.073, 1107878.448, "Sumburgh Head"),
            'TP40': (395999.668, 1138728.951, "Foula"),
        }

        print("drawoptions(withcolor .5[red, white]);", file=plotter)
        for t in points:
            e, n, name = points[t]
            print("draw unitsquare shifted -(1/2, 1/2) rotated 45 scaled 3", file=plotter)
            print("shifted ({:.1f}, {:.1f});".format(e/scale, n/scale), file=plotter)

    if args.series and sides:  # sides will be empty if none of the maps matched series_wanted

        print("drawoptions(withpen pencircle scaled 0.2);defaultscale:={:.2f};".format(666/scale), file=plotter)

        for k in sides:
            series = k[:1]
            map_color = color_for[series] if series in color_for else 'black'
            print("draw {} withcolor {};".format(path_for[k], map_color), file=plotter)

            sheet = osgb.map_locker[k]
            x = (sheet.bbox[0][0] + sheet.bbox[1][0]) / 2 / scale
            y = (sheet.bbox[0][1] + sheet.bbox[1][1]) / 2 / scale

            if sheet.number.startswith('OL'):
                map_color = '(.5, .5, 1)'
                y += 3 

            print('label("{}", ({}, {})) withcolor .76[white, {}];'.format(sheet.number, x, y, map_color), file=plotter)

        print('path p, q;', file=plotter)
        for k in insets:
            series = k[:1]
            map_color = color_for[series] if series in color_for else 'black'
            print("p:={};".format(path_for[k]), file=plotter)
            parent_key = osgb.map_locker[k].parent
            if does_not_overlap_parent(k):
                print('q:={};'.format(path_for[parent_key]), file=plotter)
                print("draw center p -- center q cutbefore p cutafter q", file=plotter)
                print("dashed evenly scaled 1/3 withcolor {};".format(map_color), file=plotter)
            print("draw p withcolor {};".format(map_color), file=plotter)

        y = 1300000/scale
        for s in args.series:
            color = color_for[s] if s in color_for else 'black'
            title = 'label.rt("{} sheet index" infont defaultfont scaled {:.1f}, (0, {:.1f})) withcolor {};'.format(
                    osgb.name_for_map_series[s], 2000/scale, y, color)
            print(title, file=plotter)
            y -= 24

        # add sheet names for Harvey maps
        if args.series in 'HJ':
            print("defaultscale:={:.1f};".format(2000/scale), file=plotter)
            x = 510000/scale
            y = 515000/scale
            print('fill unitsquare xscaled {:.1f}'.format(200000/scale), file=plotter)
            print('yscaled {:.1f}'.format((12000*len(sides)+4000)/scale), file=plotter)
            print('shifted ({:.1f}, {:.1f}) withcolor background;'.format(x-5, y-3), file=plotter)
            for k in sorted(sides, reverse=True):
                sheet = osgb.map_locker[k]
                print('draw "{} {}"'.format(sheet['number'], sheet['title']), file=plotter)
                print('infont defaultfont shifted ({:.1f}, {:.1f});'.format(x, y), file=plotter)
                y += 12000/scale

    # Add a margin
    print('z1 = center currentpicture;', file=plotter)
    print('setbounds currentpicture to bbox currentpicture shifted -z1 scaled 1.05 shifted z1;', file=plotter)

    # Finish the MP input and close the file
    print("endfig;end.", file=plotter)
    plotter.close()

    # Now deal with MP (unless asked not to)
    if not args.nomp:
        try:
            subprocess.check_call(['mpost', plotter.name])
        except subprocess.CalledProcessError as e:
            print('Metapost failed', file=sys.stderr)
            raise e

        epsfile = plotter.name[:-2] + 'eps'
        logfile = plotter.name[:-2] + 'log'

        try:
            subprocess.check_call(['epstopdf', "-o={}".format(pdffile), epsfile])
        except subprocess.CalledProcessError as e:
            print('epdtopdf failed', file=sys.stderr)
            raise e
        try:
            os.unlink(epsfile)
        except OSError as e:
            print("Failed to delete temporary file: {}".format(epsfile), file=sys.stderr)
            raise e

        try:
            os.unlink(logfile)
        except OSError as e:
            print("Failed to delete temporary file: {}".format(logfile), file=sys.stderr)
            raise e

        try:
            os.unlink(plotter.name)
        except OSError as e:
            print('Failed to delete MP file', file=sys.stderr)
            raise e

        print("Created " + pdffile)
    else:
        print("MP source written to " + plotter.name)
