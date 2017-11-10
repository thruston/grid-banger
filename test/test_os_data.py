'''Test osgb module against standard OSGB data points

Toby Thurston -- 28 Oct 2017 
'''

import argparse
import osgb

# pylint: disable=C0103, C0301, C0326

test_input = {
    "TP01": {'ll': (49.92226393730, -6.29977752014), 'grid': (91492.146, 11318.804), 'name': "St Mary's, Scilly"},
    "TP02": {'ll': (49.96006137820, -5.20304609998), 'grid': (170370.718, 11572.405), 'name': "Lizard Point Lighthouse"},
    "TP03": {'ll': (50.43885825610, -4.10864563561), 'grid': (250359.811, 62016.569), 'name': "Plymouth"},
    "TP04": {'ll': (50.57563665000, -1.29782277240), 'grid': (449816.371, 75335.861), 'name': "St Catherine's Point Lighthouse"},
    "TP05": {'ll': (50.93127937910, -1.45051433700), 'grid': (438710.920, 114792.250), 'name': "Former OSHQ"},
    "TP06": {'ll': (51.40078220140, -3.55128349240), 'grid': (292184.870, 168003.465), 'name': "Nash Point Lighthouse"},
    "TP07": {'ll': (51.37447025550, 1.44454730409), 'grid': (639821.835, 169565.858), 'name': "North Foreland Lighthouse"},
    "TP08": {'ll': (51.42754743020, -2.54407618349), 'grid': (362269.991, 169978.690), 'name': "Brislington"},
    "TP09": {'ll': (51.48936564950, -0.11992557180), 'grid': (530624.974, 178388.464), 'name': "Lambeth"},
    "TP10": {'ll': (51.85890896400, -4.30852476960), 'grid': (241124.584, 220332.641), 'name': "Carmarthen"},
    "TP11": {'ll': (51.89436637350, 0.89724327012), 'grid': (599445.590, 225722.826), 'name': "Colchester"},
    "TP12": {'ll': (52.25529381630, -2.15458614387), 'grid': (389544.190, 261912.153), 'name': "Droitwich"},
    "TP13": {'ll': (52.25160951230, -0.91248956970), 'grid': (474335.969, 262047.755), 'name': "Northampton"},
    "TP14": {'ll': (52.75136687170, 0.40153547065), 'grid': (562180.547, 319784.995), 'name': "King's Lynn"},
    "TP15": {'ll': (52.96219109410, -1.19747655922), 'grid': (454002.834, 340834.943), 'name': "Nottingham"},
    "TP16": {'ll': (53.34480280190, -2.64049320810), 'grid': (357455.843, 383290.436), 'name': "STFC, Daresbury"},
    "TP17": {'ll': (53.41628516040, -4.28918069756), 'grid': (247958.971, 393492.909), 'name': "Point Lynas Lighthouse, Anglesey"},
    "TP18": {'ll': (53.41630925420, -4.28917792869), 'grid': (247959.241, 393495.583), 'name': "Point Lynas Lighthouse, Anglesey"},
    "TP19": {'ll': (53.77911025760, -3.04045490691), 'grid': (331534.564, 431920.794), 'name': "Blackpool Airport"},
    "TP20": {'ll': (53.80021519630, -1.66379168242), 'grid': (422242.186, 433818.701), 'name': "Pudsey"},
    "TP21": {'ll': (54.08666318080, -4.63452168212), 'grid': (227778.330, 468847.388), 'name': "Isle of Man airport"},
    "TP22": {'ll': (54.11685144290, -0.07773133187), 'grid': (525745.670, 470703.214), 'name': "Flamborough Head"},
    "TP23": {'ll': (54.32919541010, -4.38849118133), 'grid': (244780.636, 495254.887), 'name': "Ramsey, Isle of Man"},
    "TP24": {'ll': (54.89542340420, -2.93827741149), 'grid': (339921.145, 556034.761), 'name': "Carlisle"},
    "TP25": {'ll': (54.97912273660, -1.61657685184), 'grid': (424639.355, 565012.703), 'name': "Newcastle University"},
    "TP26": {'ll': (55.85399952950, -4.29649016251), 'grid': (256340.925, 664697.269), 'name': "Glasgow"},
    "TP27": {'ll': (55.92478265510, -3.29479219337), 'grid': (319188.434, 670947.534), 'name': "Sighthill, Edinburgh"},
    "TP28": {'ll': (57.00606696050, -5.82836691850), 'grid': (167634.202, 797067.144), 'name': "Mallaig Lifeboat Station"},
    "TP29": {'ll': (57.13902518960, -2.04856030746), 'grid': (397160.491, 805349.736), 'name': "Girdle Ness Lighthouse"},
    "TP30": {'ll': (57.48625000720, -4.21926398555), 'grid': (267056.768, 846176.972), 'name': "Inverness"},
    "TP31": {'ll': (57.81351838410, -8.57854456076), 'grid': (9587.909, 899448.996), 'name': "Hirta, St Kilda"},
    "TP32": {'ll': (58.21262247180, -7.59255560556), 'grid': (71713.132, 938516.404), 'name': "at sea, 7km S of Flannan"},
    "TP33": {'ll': (58.51560361300, -6.26091455533), 'grid': (151968.652, 966483.780), 'name': "Butt of Lewis lighthouse"},
    "TP34": {'ll': (58.58120461280, -3.72631022121), 'grid': (299721.891, 967202.992), 'name': "Dounreay Airfield"},
    "TP35": {'ll': (59.03743871190, -3.21454001115), 'grid': (330398.323, 1017347.016), 'name': "Orkney Mainland"},
    "TP36": {'ll': (59.09335035320, -4.41757674598), 'grid': (261596.778, 1025447.602), 'name': "at sea, 1km NW of Sule Skerry"},
    "TP37": {'ll': (59.09671617400, -5.82799339844), 'grid': (180862.461, 1029604.114), 'name': "at sea, 3km south of Rona"},
    "TP38": {'ll': (59.53470794490, -1.62516966058), 'grid': (421300.525, 1072147.239), 'name': "Fair Isle"},
    "TP39": {'ll': (59.85409913890, -1.27486910356), 'grid': (440725.073, 1107878.448), 'name': "Sumburgh Head"},
    "TP40": {'ll': (60.13308091660, -2.07382822798), 'grid': (395999.668, 1138728.951), 'name': "Foula"},
    }

def get_ll(name):
    '''Format lat/lon neatly for a defined place.'''

    if name not in test_input:
        return 'Undefined place'  

    (lat, lon) = test_input[name]['expected']
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

def saveit(error_list, place, domain, delta):
    if args.verbose:
        print(place, domain, delta, as_mm(delta, domain))

    error_list.append((place, domain, delta))

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    errors = []
    for k in sorted(test_input):
        (lat, lon) = test_input[k]['ll']
        (eee, nnn) = test_input[k]['grid']
        (goteee, gotnnn) = osgb.ll_to_grid(lat, lon)
        (gotlat, gotlon) = osgb.grid_to_ll(eee, nnn)

        differences = "{:.1f} {:.1f} {:.2f} {:.2f}".format(goteee-eee, gotnnn-nnn, as_mm(gotlat-lat, "Latitude"), as_mm(gotlon-lon, "Longitude"))

        print(k, differences, test_input[k]['name'])

