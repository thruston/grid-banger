''''

Toby Thurston  2017-10-28

Test known locations convert correctly
'''

from __future__ import division

import osgb


def test_ten_metre_test_with_osgb():
    '''
    the sw corner of OS Explorer sheet 161 (Cobham, Surrey)
    -------------------------------------------------------
    check we are within 10m (easily the limit of my ability to measure on a 1:25000 map)
    Note that here we are using OSGB36 through out, because the LL printed on pre-2015
    OS maps is not based on WGS84.
    '''

    (e, n) = osgb.ll_to_grid(lat=51.3333333333, lon=-0.416666666667, model='OSGB36')
    assert (e, n) == (510290.252, 160605.816)

    gr = osgb.format_grid(510290, 160606)
    assert gr == 'TQ 102 606'


def test_reading_from_landranger():
    ''' Hills above Loch Achall, OS Sheet 20
    '''
    gr = osgb.format_grid(osgb.ll_to_grid(lat=57+55/60, lon=-305/60, model='OSGB36'), form='GPS')
    assert gr == 'NH 17379 96054'


def test_glendessary():
    '''
    # and now a boggy path just north of Glendessary in Lochaber
    # OS Sheet 40 topright corner.  A graticule intersection at
    # 57N 5o20W is marked.  GR measured from the map.
    '''
    assert osgb.ll_to_grid(lat=57, lon=-320/60, model='OSGB36') == (197573.181, 794792.843)


def test_grid_formatting():
    assert osgb.format_grid(osgb.parse_grid('NM975948')) == 'NM 975 948'
    assert osgb.format_grid(osgb.parse_grid('NH073060')) == 'NH 073 060'
    assert osgb.format_grid(osgb.parse_grid('SX700682')) == 'SX 700 682'
    assert osgb.format_grid(osgb.parse_grid('TQ103606')) == 'TQ 103 606'
    assert osgb.format_grid(osgb.parse_grid('HY 554 300')) == 'HY 554 300'
    assert osgb.format_grid(osgb.parse_grid('40/975948')) == 'NM 975 948'


def test_greenwich():
    assert osgb.format_grid(osgb.ll_to_grid(lat=51.5, lon=0, model='OSGB36')) == 'TQ 388 798'
