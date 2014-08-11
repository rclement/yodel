import math


def modulus(re, im):
    """
    Compute the modulus of a complex number.

    :param re: real part of the complex number
    :param im: imaginary part of the complex number
    :rtype: modulus of complex number
    """
    return math.sqrt(re * re + im * im)


def phase(re, im):
    """
    Compute the phase of a complex number.

    :param re: real part of the complex number
    :param im: imaginary part of the complex number
    :rtype: phase of complex number
    """
    return math.atan2(im, re)
