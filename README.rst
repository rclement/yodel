Description
===========

|Build Status| |Coverage Status| |ReadTheDocs Status| |PyPI|

`Yodel <http://www.romainclement.com/yodel>`__ (*the Swiss Army knife
for your sound*) is an easy-to-use Python package for digital audio
signal processing, analysis and synthesis. It is meant to provide a
comprehensive set of tools to manipulate audio signals. It can be used
for prototyping as well as developing audio applications in Python.

Features
========

-  Analysis:

   -  Discrete Fourier Transform
   -  Fast Fourier Transform
   -  Windowing: Hamming, Hanning, Blackman

-  Filtering:

   -  Single Pole: low-pass, high-pass
   -  Biquad: low-pass, high-pass, band-pass, all-pass, notch, peak,
      low-shelf, high-shelf
   -  State Variable: low-pass, high-pass, band-pass, band-reject
   -  Parametric Equalizer
   -  Comb: feedforward, feedback, all-pass
   -  Convolution: standard, fast
   -  Windowed Sinc: low-pass, high-pass, band-pass, band-reject
   -  Custom

-  Delay:

   -  Time-varying delayline

Installation
============

Simply run: ``pip install yodel``

Documentation
=============

The complete API documentation can be found at
`ReadTheDocs <http://yodel.readthedocs.org/en/latest/>`__. For code
examples, check out the ``demo`` folder inside the project repository.

Contact
=======

Any questions or comments about Yodel? Let me know at
contact@romainclement.com.

Changelog
=========

Version 0.3.0
-------------

-  New delay module with time-varying delayline
-  New filters: Comb, Convolution, FastConvolution, Custom, Windowed
   Sinc

Version 0.2.0
-------------

-  Fix flat frequency response for biquad filter
-  Renaming 'AnalysisWindow' class to 'Window' in analysis module
-  Better documentation (include classes constructors)
-  New filters: single pole, state variable, parametric equalizer

Version 0.1.2
-------------

-  More complete README
-  Fix Python package long description (use README.rst)
-  ReadTheDocs integration
-  Integrate extra folders in distribution (test, demo, docs)

Version 0.1.1
-------------

-  Renaming the project to Yodel
-  Better packaging for PyPI

Version 0.1.0
-------------

-  First release of Damn!
-  Signal analysis module:

   -  Discrete Fourier Transform
   -  Fast Fourier Transform
   -  Analysis windows (Hanning, Hamming, Blackman)

-  Filtering module:

   -  Biquad filter

-  Utility modules for complex numbers and conversions

License
=======

The MIT License (MIT)

Copyright (c) 2014 Romain Clement

.. |Build Status| image:: https://travis-ci.org/rclement/yodel.svg?branch=develop
   :target: https://travis-ci.org/rclement/yodel
.. |Coverage Status| image:: https://coveralls.io/repos/rclement/yodel/badge.png?branch=develop
   :target: https://coveralls.io/r/rclement/yodel?branch=develop
.. |ReadTheDocs Status| image:: https://readthedocs.org/projects/yodel/badge/?version=latest
   :target: https://readthedocs.org/projects/yodel
.. |PyPI| image:: http://img.shields.io/pypi/dm/yodel.svg
   :target: https://pypi.python.org/pypi/yodel
