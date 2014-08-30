"""
This module provides utility functions for various math conversions.
"""

import math


def lin2db(linval):
    """
    Convert a linear value to the decibel (dB) scale.

    :param linval: linear value
    :rtype: decibel value
    """
    if linval > 1e-5:
        return 20.0 * math.log10(linval)
    else:
        return -100.0


def db2lin(dbval):
    """
    Convert a decibel (dB) value to the linear scale.

    :param dbval: decibel value
    :rtype: linear value
    """
    return math.pow(10, dbval / 20.0)
