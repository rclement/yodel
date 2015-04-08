# Yodel Change Log

## [Unreleased][unreleased]
### Fixed
- Fix biquad filter normalized coefficients


## [0.3.0] - 2014-10-28
### Added
- New delay module with time-varying delayline
- New filters: Comb, Convolution, FastConvolution, Custom, Windowed Sinc


## [0.2.0] - 2014-08-30
### Added
- New filters: single pole, state variable, parametric equalizer
- Better documentation (include classes constructors)

### Changed
- Renaming 'AnalysisWindow' class to 'Window' in analysis module

### Fixed
- Fix flat frequency response for biquad filter


## [0.1.2] - 2014-08-13
### Added
- ReadTheDocs integration
- Integrate extra folders in distribution (test, demo, docs)

### Changed
- More complete README

### Fixed
- Fix Python package long description (use README.rst)


## [0.1.1] - 2014-08-12
### Changed
- Renaming the project to Yodel

### Fixed
- Better packaging for PyPI


## [0.1.0] - 2014-08-10
### Added
- First release of Damn!
- Signal analysis module:
    - Discrete Fourier Transform
    - Fast Fourier Transform
    - Analysis windows (Hanning, Hamming, Blackman)
- Filtering module:
    - Biquad filter
- Utility modules for complex numbers and conversions


[unreleased]: https://github.com/rclement/yodel/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/rclement/yodel/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rclement/yodel/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/rclement/yodel/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/rclement/yodel/compare/v0.1.0...v0.1.1

