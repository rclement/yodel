Description
===========

[![Build Status](https://travis-ci.org/rclement/yodel.svg?branch=develop)](https://travis-ci.org/rclement/yodel)
[![Coverage Status](https://coveralls.io/repos/rclement/yodel/badge.png?branch=develop)](https://coveralls.io/r/rclement/yodel?branch=develop)
[![ReadTheDocs Status](https://readthedocs.org/projects/yodel/badge/?version=latest)](https://readthedocs.org/projects/yodel)
[![PyPI](http://img.shields.io/pypi/dm/yodel.svg)](https://pypi.python.org/pypi/yodel)

[Yodel](http://www.romainclement.com/yodel) (_the Swiss Army knife for your sound_) is an easy-to-use Python package
for digital audio signal processing, analysis and synthesis.
It is meant to provide a comprehensive set of tools to manipulate audio signals.
It can be used for prototyping as well as developing audio applications in Python.

Features
========

* Analysis:

    * Discrete Fourier Transform
    * Fast Fourier Transform
    * Windowing: Hamming, Hanning, Blackman

* Filtering:

    * Single Pole: low-pass, high-pass
    * Biquad: low-pass, high-pass, band-pass, all-pass, notch, peak, low-shelf, high-shelf
    * State Variable: low-pass, high-pass, band-pass, band-reject
    * Parametric Equalizer
    * Comb: feedforward, feedback, all-pass
    * Convolution: standard, fast
    * Windowed Sinc: low-pass, high-pass, band-pass, band-reject
    * Custom

* Delay:

    * Time-varying delayline

Installation
============

Simply run: `pip install yodel`

Documentation
=============

The complete API documentation can be found at [ReadTheDocs](http://yodel.readthedocs.org/en/latest/).
For code examples, check out the `demo` folder inside the project repository.

Contact
=======

Any questions or comments about Yodel? Let me know at [contact@romainclement.com](mailto:contact@romainclement.com).

License
=======

The MIT License (MIT)

Copyright (c) 2014 Romain Clement
