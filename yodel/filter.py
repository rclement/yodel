"""
This module provides classes for audio signal filtering.
"""

import math


class SinglePole:
    """
    A single pole filter is used to perform low-pass and high-pass filtering.
    Signal attenuation is at a rate of 6 dB per octave.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self):
        """
        Create an inactive single pole filter with a flat frequency response.
        To make the filter active, use one of the provided methods:
        :py:meth:`low_pass` and :py:meth:`high_pass`.
        """
        self.reset()

    def reset(self):
        """
        Create an inactive single pole filter with a flat frequency response.
        To make the filter active, use one of the provided methods.
        """
        self._a0 = 1.0
        self._a1 = 0.0
        self._x1 = 0.0
        self._b1 = 0.0
        self._y1 = 0.0

    def low_pass(self, samplerate, cutoff):
        """
        Make a low-pass filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        """
        self._b1 = math.exp(-2.0 * math.pi * cutoff / samplerate)
        self._a0 = 1.0 - self._b1
        self._a1 = 0.0

    def high_pass(self, samplerate, cutoff):
        """
        Make a high-pass filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        """
        self._b1 = math.exp(-2.0 * math.pi * cutoff / samplerate)
        self._a0 = 0.5 * (1.0 + self._b1)
        self._a1 = - self._a0

    def process_sample(self, x):
        """
        Filter a single sample and return the filtered sample.

        :param x: input sample
        :rtype: filtered sample
        """
        y = self._a0 * x + self._a1 * self._x1 + self._b1 * self._y1
        self._y1 = y
        self._x1 = x
        return y

    def process(self, x, y):
        """
        Filter an input signal. Can be used for in-place filtering.

        :param x: input buffer
        :param y: output buffer
        """
        num_samples = len(x)
        for n in range(0, num_samples):
            y[n] = self.process_sample(x[n])


class Biquad:
    """
    A biquad filter is a 2-poles/2-zeros filter allowing to perform
    various kind of filtering. Signal attenuation is at a rate of 12 dB
    per octave.

    *Reference:*
        "Cookbook formulae for audio EQ biquad filter coefficients",
        Robert Bristow-Johnson
        (http://www.musicdsp.org/files/Audio-EQ-Cookbook.txt)
    """

    def __init__(self):
        """
        Create an inactive biquad filter with a flat frequency response.
        To make the filter active, use one of the provided methods:
        :py:meth:`low_pass`, :py:meth:`high_pass`, :py:meth:`band_pass`,
        :py:meth:`all_pass`, :py:meth:`notch`, :py:meth:`peak`,
        :py:meth:`low_shelf`, :py:meth:`high_shelf` and :py:meth:`custom`.
        """
        self.reset()

    def reset(self):
        """
        Make the filter inactive with a flat frequency response.
        """
        self._a_coeffs = [0.0, 0.0, 0.0]
        self._b_coeffs = [1.0, 0.0, 0.0]
        self._x1 = 0.0
        self._x2 = 0.0
        self._y1 = 0.0
        self._y2 = 0.0

    def low_pass(self, samplerate, cutoff, resonance):
        """
        Make a low-pass filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._compute_constants(samplerate, cutoff, resonance)
        self._a_coeffs[0] = (1.0 + self._alpha)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[0] = ((1.0 - self._cos_w0) / 2.0) / self._a_coeffs[0]
        self._b_coeffs[1] = (1.0 - self._cos_w0) / self._a_coeffs[0]
        self._b_coeffs[2] = ((1.0 - self._cos_w0) / 2.0) / self._a_coeffs[0]

    def high_pass(self, samplerate, cutoff, resonance):
        """
        Make a high-pass filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._compute_constants(samplerate, cutoff, resonance)
        self._a_coeffs[0] = (1.0 + self._alpha)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[0] = ((1.0 + self._cos_w0) / 2.0) / self._a_coeffs[0]
        self._b_coeffs[1] = -(1.0 + self._cos_w0) / self._a_coeffs[0]
        self._b_coeffs[2] = ((1.0 + self._cos_w0) / 2.0) / self._a_coeffs[0]

    def band_pass(self, samplerate, center, resonance):
        """
        Make a band-pass filter.

        :param samplerate: sample-rate in Hz
        :param center: center frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._compute_constants(samplerate, center, resonance)
        self._a_coeffs[0] = (1.0 + self._alpha)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[0] = (self._alpha) / self._a_coeffs[0]
        self._b_coeffs[1] = 0
        self._b_coeffs[2] = (- self._alpha) / self._a_coeffs[0]

    def all_pass(self, samplerate, center, resonance):
        """
        Make an all-pass filter.

        :param samplerate: sample-rate in Hz
        :param center: center frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._compute_constants(samplerate, center, resonance)
        self._a_coeffs[0] = (1.0 + self._alpha)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[0] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._b_coeffs[2] = (1.0 + self._alpha) / self._a_coeffs[0]

    def notch(self, samplerate, center, resonance):
        """
        Make a notch filter.

        :param samplerate: sample-rate in Hz
        :param center: center frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._compute_constants(samplerate, center, resonance)
        self._a_coeffs[0] = (1.0 + self._alpha)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha) / self._a_coeffs[0]
        self._b_coeffs[0] = (1.0) / self._a_coeffs[0]
        self._b_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._b_coeffs[2] = (1.0) / self._a_coeffs[0]

    def peak(self, samplerate, center, resonance, dbgain):
        """
        Make a peak filter.

        :param samplerate: sample-rate in Hz
        :param center: center frequency in Hz
        :param resonance: resonance or Q-factor
        :param dbgain: gain in dB
        """
        self._compute_constants(samplerate, center, resonance, dbgain)
        self._a_coeffs[0] = (1.0 + self._alpha / self._a)
        self._a_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._a_coeffs[2] = (1.0 - self._alpha / self._a) / self._a_coeffs[0]
        self._b_coeffs[0] = (1.0 + self._alpha * self._a) / self._a_coeffs[0]
        self._b_coeffs[1] = (-2.0 * self._cos_w0) / self._a_coeffs[0]
        self._b_coeffs[2] = (1.0 - self._alpha * self._a) / self._a_coeffs[0]

    def low_shelf(self, samplerate, cutoff, resonance, dbgain):
        """
        Make a low-shelf filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        :param dbgain: gain in dB
        """
        self._compute_constants(samplerate, cutoff, resonance, dbgain)
        self._a_coeffs[0] = ((self._a + 1) +
                             (self._a - 1) * self._cos_w0 + self._sqrtAlpha)
        self._a_coeffs[1] = ((-2.0 * ((self._a - 1) +
                                      (self._a + 1) * self._cos_w0)) /
                             self._a_coeffs[0])
        self._a_coeffs[2] = (((self._a + 1) +
                              (self._a - 1) * self._cos_w0 - self._sqrtAlpha) /
                             self._a_coeffs[0])
        self._b_coeffs[0] = ((self._a *
                              ((self._a + 1) -
                               (self._a - 1) * self._cos_w0 +
                               self._sqrtAlpha)) /
                             self._a_coeffs[0])
        self._b_coeffs[1] = ((2.0 * self._a *
                              ((self._a - 1) - (self._a + 1) * self._cos_w0)) /
                             self._a_coeffs[0])
        self._b_coeffs[2] = ((self._a *
                              ((self._a + 1) -
                               (self._a - 1) * self._cos_w0 -
                               self._sqrtAlpha)) /
                             self._a_coeffs[0])

    def high_shelf(self, samplerate, cutoff, resonance, dbgain):
        """
        Make a high-shelf filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        :param dbgain: gain in dB
        """
        self._compute_constants(samplerate, cutoff, resonance, dbgain)
        self._a_coeffs[0] = ((self._a + 1) -
                             (self._a - 1) * self._cos_w0 + self._sqrtAlpha)
        self._a_coeffs[1] = ((2.0 *
                              ((self._a - 1) - (self._a + 1) * self._cos_w0)) /
                             self._a_coeffs[0])
        self._a_coeffs[2] = (((self._a + 1) -
                              (self._a - 1) * self._cos_w0 -
                              self._sqrtAlpha) /
                             self._a_coeffs[0])
        self._b_coeffs[0] = ((self._a *
                              ((self._a + 1) +
                               (self._a - 1) * self._cos_w0 +
                               self._sqrtAlpha)) /
                             self._a_coeffs[0])
        self._b_coeffs[1] = ((-2.0 * self._a *
                              ((self._a - 1) + (self._a + 1) * self._cos_w0)) /
                             self._a_coeffs[0])
        self._b_coeffs[2] = ((self._a *
                              ((self._a + 1) +
                               (self._a - 1) * self._cos_w0 -
                               self._sqrtAlpha)) /
                             self._a_coeffs[0])

    def custom(self, a0, a1, a2, b0, b1, b2):
        """
        Make a custom filter.

        :param a0: a[0] coefficient
        :param a1: a[1] coefficient
        :param a2: a[2] coefficient
        :param b0: b[0] coefficient
        :param b1: b[1] coefficient
        :param b2: b[2] coefficient
        """
        self._a_coeffs[0] = a0
        self._a_coeffs[1] = a1 / a0
        self._a_coeffs[2] = a2 / a0
        self._b_coeffs[0] = b0 / a0
        self._b_coeffs[1] = b1 / a0
        self._b_coeffs[2] = b2 / a0

    def process_sample(self, x):
        """
        Filter a single sample and return the filtered sample.

        :param x: input sample
        :rtype: filtered sample
        """
        curr = x
        y = (self._b_coeffs[0] * x +
             self._b_coeffs[1] * self._x1 +
             self._b_coeffs[2] * self._x2 -
             self._a_coeffs[1] * self._y1 -
             self._a_coeffs[2] * self._y2)
        self._x2 = self._x1
        self._x1 = curr
        self._y2 = self._y1
        self._y1 = y
        return y

    def process(self, x, y):
        """
        Filter an input signal. Can be used for in-place filtering.

        :param x: input buffer
        :param y: output buffer
        """
        num_samples = len(x)
        for n in range(0, num_samples):
            y[n] = self.process_sample(x[n])

    def _compute_constants(self, fs, fc, q, dbgain=0):
        """
        Pre-compute internal mathematical constants
        """
        self._fc = fc
        self._q = q
        self._dbgain = dbgain
        self._fs = fs
        self._a = math.pow(10, (self._dbgain / 40.0))
        self._w0 = 2.0 * math.pi * self._fc / self._fs
        self._cos_w0 = math.cos(self._w0)
        self._sin_w0 = math.sin(self._w0)
        self._alpha = self._sin_w0 / (2.0 * self._q)
        self._sqrtAlpha = 2.0 * math.sqrt(self._a) * self._alpha


class StateVariable:
    """
    A state variable filter provides simultaneously low-pass, high-pass,
    band-pass and band-reject filtering. Like the :py:class:`Biquad` filter,
    signal attenuation is at a rate of 12 dB per octave. Nevertheless, the
    filter becomes unstable at higher frequencies (around one sixth of the
    sample-rate).
    """

    def __init__(self):
        """
        Create an inactive state variable filter with a flat frequency
        response. To make the filter active, use the :py:meth:`set` method.
        """
        self.reset()

    def reset(self):
        """
        Make the filter inactive with a flat frequency response.
        """
        self._f = 0
        self._q = 0
        self._x1 = 0
        self._x2 = 0

    def set(self, samplerate, cutoff, resonance):
        """
        Specify the parameters of the filter.

        :param samplerate: sample-rate in Hz
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        """
        self._f = 2.0 * math.sin(math.pi * cutoff / samplerate)
        self._q = 1.0 / resonance

    def process_sample(self, x):
        """
        Filter a single sample and return the filtered samples.

        :param x: input sample
        :rtype: tuple (high-pass, band-pass, low-pass, band-reject)
        """
        hp = x - (self._q * self._x1) - self._x2
        bp = hp * self._f + self._x1
        lp = self._x1 * self._f + self._x2
        br = hp + lp
        self._x1 = bp
        self._x2 = lp
        return (hp, bp, lp, br)

    def process(self, x, hp, bp, lp, br):
        """
        Filter an input signal. Can be used for in-place filtering.

        :param x: input buffer
        :param hp: high-pass filtered output
        :param bp: band-pass filtered output
        :param lp: low-pass filtered output
        :param br: band-reject filtered output
        """
        num_samples = len(x)
        for n in range(0, num_samples):
            (hps, bps, lps, brs) = self.process_sample(x[n])
            hp[n] = hps
            bp[n] = bps
            lp[n] = lps
            br[n] = brs


class ParametricEQ:
    """
    A parametric equalizer provides multi-band equalization of audio signals.
    The center frequency, the resonance and the amplification (in dB) can be
    controlled individually for each frequency band.
    """

    def __init__(self, samplerate, bands):
        """
        Create a parametric equalizer with a given number of frequency bands.

        :param samplerate: sample-rate in Hz
        :param bands: number of bands (at least 2)
        """
        self.samplerate = samplerate

        if bands < 2:
            self.num_bands = 2
        else:
            self.num_bands = bands

        self.filters = []
        self.filters.append(Biquad())
        for i in range(1, self.num_bands-1):
            self.filters.append(Biquad())
        self.filters.append(Biquad())

    def set_band(self, band, center, resonance, dbgain):
        """
        Change the parameters for the selected frequency band.

        :param band: index of the band (from 0 to (total number of bands - 1))
        :param cutoff: cut-off frequency in Hz
        :param resonance: resonance or Q-factor
        :param dbgain: gain in dB
        """
        if band == 0:
            self.filters[band].low_shelf(self.samplerate, center, resonance,
                                         dbgain)
        elif band > 0 and band < (self.num_bands-1):
            self.filters[band].peak(self.samplerate, center, resonance, dbgain)
        elif band == (self.num_bands-1):
            self.filters[band].high_shelf(self.samplerate, center, resonance,
                                          dbgain)

    def process(self, input_signal, output_signal):
        """
        Filter an input signal. Can be used for in-place filtering.

        :param input_signal: input buffer
        :param output_signal: filtered buffer
        """
        self.filters[0].process(input_signal, output_signal)
        for i in range(1, self.num_bands):
            self.filters[i].process(output_signal, output_signal)
