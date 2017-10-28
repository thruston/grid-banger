'''Test osgb module against standard OSGB data points

Toby Thurston -- 28 Oct 2017 
'''

import argparse
import osgb

# pylint: disable=C0103, C0301, C0326

test_input = {
    "BLAC"           : {"lat" : 53.77911025694444,  "lon" : -3.040454906944444,    "e" :  331534.552,  "n" :  431920.792 },
    "BRIS"           : {"lat" : 51.42754743361111,  "lon" : -2.544076186111111,    "e" :  362269.979,  "n" :  169978.688 },
    "BUT1"           : {"lat" : 58.51560361805556,  "lon" : -6.260914556388889,    "e" :  151968.641,  "n" :  966483.777 },
    "CARL"           : {"lat" : 54.89542340527777,  "lon" : -2.938277414722223,    "e" :  339921.133,  "n" :  556034.759 },
    "CARM"           : {"lat" : 51.8589089675,      "lon" : -4.308524766111111,    "e" :  241124.573,  "n" :  220332.638 },
    "COLC"           : {"lat" : 51.89436637527778,  "lon" : 0.897243275,           "e" :  599445.578,  "n" :  225722.824 },
    "DARE"           : {"lat" : 53.34480280666667,  "lon" : -2.640493207222222,    "e" :  357455.831,  "n" :  383290.434 },
    "DROI"           : {"lat" : 52.25529381638889,  "lon" : -2.154586149444444,    "e" :  389544.178,  "n" :  261912.151 },
    "EDIN"           : {"lat" : 55.9247826525,      "lon" : -3.294792187777777,    "e" :  319188.423,  "n" :  670947.532 },
    "FLA1"           : {"lat" : 54.11685144333333,  "lon" : -0.07773132666666667,  "e" :  525745.658,  "n" :  470703.211 },
    "GIR1"           : {"lat" : 57.13902519305555,  "lon" : -2.048560316111111,    "e" :  397160.479,  "n" :  805349.734 },
    "GLAS"           : {"lat" : 55.85399952972222,  "lon" : -4.296490155555555,    "e" :  256340.914,  "n" :  664697.266 },
    "INVE"           : {"lat" : 57.48625000333333,  "lon" : -4.219263989444444,    "e" :  267056.756,  "n" :  846176.969 },
    "IOMN"           : {"lat" : 54.32919541055556,  "lon" : -4.388491180000001,    "e" :  244780.625,  "n" :  495254.884 },
    "IOMS"           : {"lat" : 54.08666318083333,  "lon" : -4.634521684999999,    "e" :  227778.318,  "n" :  468847.386 },
    "KING"           : {"lat" : 52.75136687444444,  "lon" : 0.4015354769444445,    "e" :  562180.535,  "n" :  319784.993 },
    "LEED"           : {"lat" : 53.80021519916667,  "lon" : -1.663791675833333,    "e" :  422242.174,  "n" :  433818.699 },
    "LIZ1"           : {"lat" : 49.96006138305556,  "lon" : -5.203046100277778,    "e" :  170370.706,  "n" :  11572.404 },
    "LOND"           : {"lat" : 51.48936564611111,  "lon" : -0.1199255641666667,   "e" :  530624.963,  "n" :  178388.461 },
    "LYN1"           : {"lat" : 53.41628515777778,  "lon" : -4.289180693055555,    "e" :  247958.959,  "n" :  393492.906 },
    "LYN2"           : {"lat" : 53.41630925166667,  "lon" : -4.289177926388889,    "e" :  247959.229,  "n" :  393495.580 },
    "MALA"           : {"lat" : 57.00606696527777,  "lon" : -5.828366926388889,    "e" :  167634.190,  "n" :  797067.142 },
    "NAS1"           : {"lat" : 51.40078220388889,  "lon" : -3.551283487222222,    "e" :  292184.858,  "n" :  168003.462 },
    "NEWC"           : {"lat" : 54.97912274,        "lon" : -1.616576845555556,    "e" :  424639.343,  "n" :  565012.700 },
    "NFO1"           : {"lat" : 51.37447025916666,  "lon" : 1.444547306944445,     "e" :  639821.823,  "n" :  169565.856 },
    "NORT"           : {"lat" : 52.25160950916667,  "lon" : -0.91248957,           "e" :  474335.957,  "n" :  262047.752 },
    "NOTT"           : {"lat" : 52.962191095,       "lon" : -1.197476561666667,    "e" :  454002.822,  "n" :  340834.941 },
    "OSHQ"           : {"lat" : 50.9312793775,      "lon" : -1.450514340555556,    "e" :  438710.908,  "n" :  114792.248 },
    "PLYM"           : {"lat" : 50.43885825472222,  "lon" : -4.108645639722222,    "e" :  250359.798,  "n" :  62016.567 },
    "SCP1"           : {"lat" : 50.57563665166667,  "lon" : -1.297822771388889,    "e" :  449816.359,  "n" :  75335.859 },
    "SUM1"           : {"lat" : 59.8540991425,      "lon" : -1.274869112222222,    "e" :  440725.061,  "n" :  1107878.445 },
    "THUR"           : {"lat" : 58.58120461444445,  "lon" : -3.726310213055556,    "e" :  299721.879,  "n" :  967202.990 },
    "SCILLY"         : {"lat" : 49.92226394333333,  "lon" : -6.299777527222222,    "e" :  91492.135,   "n" :  11318.801 },
    "STKILDA"        : {"lat" : 57.81351842166666,  "lon" : -8.578544610277778,    "e" :  9587.897,    "n" :  899448.993 },
    "FLANNAN"        : {"lat" : 58.21262248138889,  "lon" : -7.592555631111111,    "e" :  71713.120,   "n" :  938516.401 },
    "NORTHRONA"      : {"lat" : 59.09671617777778,  "lon" : -5.827993408888888,    "e" :  180862.449,  "n" :  1029604.111 },
    "SULESKERRY"     : {"lat" : 59.09335035083333,  "lon" : -4.417576741666667,    "e" :  261596.767,  "n" :  1025447.599 },
    "FOULA"          : {"lat" : 60.13308092083334,  "lon" : -2.073828223611111,    "e" :  395999.656,  "n" :  1138728.948 },
    "FAIRISLE"       : {"lat" : 59.53470794333333,  "lon" : -1.625169658333333,    "e" :  421300.513,  "n" :  1072147.236 },
    "ORKNEY"         : {"lat" : 59.03743871,        "lon" : -3.214540010555556,    "e" :  330398.311,  "n" :  1017347.013 },
    "ORK_MAIN_ORK"   : {"lat" : 58.71893718305556,  "lon" : -3.073926035277778,    "e" :  337898.195,  "n" :  981746.359 },
    "ORK_MAIN_MAIN"  : {"lat" : 58.72108286444445,  "lon" : -3.137882873055556,    "e" :  334198.101,  "n" :  982046.419 },
    }

def get_ll(name):
    '''Format lat/lon neatly for a defined place.'''

    if name not in test_input:
        return 'Undefined place'

    lat = test_input[name]['lat']
    lon = test_input[name]['lon']
    if lon > 0:
        hemi = 'E'
    elif lon < 0:
        hemi = 'W'
    else:
        hemi = ''

    return '{:.3f}N {:.3f}{}'.format(lat, abs(lon), hemi)

def as_mm(measure, unit):
    '''Apply some guesswork to turn degrees of Lat or Lon into approximate mm lengths.

    >>> as_mm(0, 'Longitude')
    0.0

    >>> as_mm(51.34, 'Latitude')
    5134000000.0

    >>> as_mm(-4, 'Longitude')
    -260000000.0

    >>> as_mm(10, 'Northing')
    10000.0
    '''

    factor_for = {
            'Latitude' : 1e8,
            'Longitude' : 6.5e7,
            'Northing' : 1000,
            'Easting' : 1000,
            }

    if unit in factor_for:
        return float(measure)*factor_for[unit]

    return float(measure)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    errors = []
    for k in sorted(test_input):
        (gote, gotn) = osgb.ll_to_grid(test_input[k]['lat'], test_input[k]['lon'])
        diffe = gote - test_input[k]['e']
        diffn = gotn - test_input[k]['n']

        if abs(diffe) > 0.0005:
            errors.append( (k, "Easting", diffe) )
        if abs(diffn) > 0.0005:
            errors.append( (k, "Northing", diffn) )

        (gotlat, gotlon) = osgb.grid_to_ll(test_input[k]['e'], test_input[k]['n'])
        difflat = gotlat - test_input[k]['lat']
        difflon = gotlon - test_input[k]['lon']

        if abs(difflat) > 0.00000001:
            errors.append( (k, "Latitude", difflat))
        if abs(difflon) > 0.00000001:
            errors.append( (k, "Longitude", difflon))

    tests = len(test_input)
    bad   = len(errors)
    ok    = tests-bad
    assert(ok > 35)

    if args.verbose:
        print('{}/{} standard OS conversions are accurate to within 0.5 mm'.format(ok, tests))
        for e in sorted(errors, key=lambda e:test_input[e[0]]['lon'], reverse=True):
            k, domain, delta = e
            print("At {} ({}) conversion to {} is within {:.2g} mm".format(k, get_ll(k), domain, as_mm(abs(delta), domain)))
