#! /usr/bin/env python3

import pytest
import osgb

def test_wrong_model():
    with pytest.raises(osgb.convert.UndefinedModelError) as e:
        t = osgb.grid_to_ll(*osgb.parse_grid("NH123433"), 'EDM50')

def test_junk():
    with pytest.raises(osgb.gridder.GarbageError) as e:
        t = osgb.parse_grid("This is not a grid ref")

def test_wrong_sheet():
    with pytest.raises(osgb.gridder.SheetMismatchError) as e:
        t = osgb.parse_grid(195, 789, 234)

def test_bad_sheet():
    with pytest.raises(osgb.gridder.UndefinedSheetError) as e:
        t = osgb.parse_grid(9999, 789, 234)

def test_duff_form():
    with pytest.raises(osgb.gridder.FaultyFormError) as e:
        t = osgb.format_grid(200000, 100000, form="TRD")

def test_too_far():
    with pytest.raises(osgb.gridder.FarFarAwayError) as e:
        gr = osgb.format_grid(14000000, 800234)
