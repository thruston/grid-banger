#! /usr/bin/env python3

import pytest
import osgb

def test_too_far():
    with pytest.raises(osgb.gridder.FarFarAwayError) as e:
        gr = osgb.format_grid(14000000, 800234)
        
# convert.py:class UndefinedModelError(Error):
# gridder.py:class Error(Exception):
# gridder.py:    """Parent class for Gridder exceptions"""
# gridder.py:class GridParseError(Error):
# gridder.py:    """Parent class for parsing exceptions"""
# gridder.py:class GridFormatError(Error):
# gridder.py:    """Parent class for formatting exceptions"""
# gridder.py:class GarbageError(GridParseError):
# gridder.py:class SheetMismatchError(GridParseError):
# gridder.py:class UndefinedSheetError(GridParseError):
# gridder.py:class FaultyFormError(GridFormatError):
# gridder.py:class FarFarAwayError(GridFormatError):
