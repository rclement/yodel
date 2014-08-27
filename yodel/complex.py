"""
This module provides utility functions for complex numbers.
"""

import math


def modulus(real, imag):
    """
    Compute the modulus of a complex number.

    :param real: real part of the complex number
    :param imag: imaginary part of the complex number
    :rtype: modulus of complex number
    """
    return math.sqrt(real * real + imag * imag)


def phase(real, imag):
    """
    Compute the phase of a complex number.

    :param real: real part of the complex number
    :param imag: imaginary part of the complex number
    :rtype: phase of complex number
    """
    return math.atan2(imag, real)
