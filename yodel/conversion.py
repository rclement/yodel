import math


def lin2db(lin):
    """
    Convert a linear value to the decibel (dB) scale.

    :param lin: linear value
    :rtype: decibel value
    """
    if lin > 1e-5:
        return 20.0 * math.log10(lin)
    else:
        return -100.0


def db2lin(db):
    """
    Convert a decibel (dB) value to the linear scale.

    :param db: decibel value
    :rtype: linear value
    """
    return math.pow(10, db / 20.0)
