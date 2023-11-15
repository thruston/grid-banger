#! /usr/bin/env python3

import osgb


def _calculations(name):
    "Perform calculations to verify constants"
    a, b, n, e = osgb.convert.ELLIPSOID_MODELS[name]
    calculated_n = (a - b) / (a + b)
    calculated_e = 1 - (b * b) / (a * a)

    ok = True
    try:
        assert n == calculated_n
    except AssertionError:
        print(name, 'a and b:', a, b)
        print(name, 'defined n is:', n)
        print(name, 'calculated n:', calculated_n)
        ok = False

    try:
        assert e == calculated_e
    except AssertionError:
        print(name, 'a and b:', a, b)
        print(name, 'defined e is:', e)
        print(name, 'calculated e:', calculated_e)
        ok = False

    return ok


def test_calculations_WGS84():
    assert _calculations('WGS84')


def test_calculations_OSGB36():
    assert _calculations('OSGB36')
