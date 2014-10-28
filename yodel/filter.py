"""
This module provides classes for audio signal filtering.
"""

import math
import yodel.delay
import yodel.analysis
import yodel.conversion


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


class Comb:
    """
    A comb filter combines the input signal with a delayed copy of itself.
    Three types are available: feedback, feedforward and allpass.

    *References:*
        "Physical Audio Signal Processing",
        Julius O. Smith
        (https://ccrma.stanford.edu/~jos/pasp/Comb_Filters.html)

        "Introduction to Computer Music",
        Nick Collins
    """

    def __init__(self, samplerate, delay, gain):
        """
        Create a comb filter. By default, it is an allpass but one can select
        another type with :py:meth:`feedback`, :py:meth:`feedforward` and
        :py:meth:`allpass` methods.

        :param samplerate: sample-rate in Hz
        :param delay: delay in ms
        :param gain: gain between -1 and +1
        """
        self.samplerate = samplerate
        self.delayline = yodel.delay.DelayLine(samplerate, 1000, delay)
        self.gain = 0
        self.x1 = 0
        self.y1 = 0
        self.__combfunc = None
        self.allpass(delay, gain)
        self.reset()

    def reset(self):
        """
        Clear the current comb filter state.
        """
        self.delayline.clear()
        self.x1 = 0
        self.y1 = 0

    def feedback(self, delay, gain):
        """
        Make a feedback comb filter.

        :param delay: delay in ms
        :param gain: gain between -1 and + 1
        """
        realdly = (((delay * self.samplerate / 1000.0) - 1.0) *
                   1000.0 / self.samplerate)
        self.set_delay(realdly)
        self.set_gain(gain)
        self.__combfunc = self.__feedback

    def feedforward(self, delay, gain):
        """
        Make a feedforward comb filter.

        :param delay: delay in ms
        :param gain: gain between -1 and + 1
        """
        self.set_delay(delay)
        self.set_gain(gain)
        self.__combfunc = self.__feedforward

    def allpass(self, delay, gain):
        """
        Make a feedforward comb filter.

        :param delay: delay in ms
        :param gain: gain between -1 and + 1
        """
        self.set_delay(delay)
        self.set_gain(gain)
        self.__combfunc = self.__allpass

    def set_delay(self, delay):
        """
        Change the current delay of the comb filter.

        :param delay: delay in ms
        """
        self.delayline.set_delay(delay)

    def set_gain(self, gain):
        """
        Change the current gain of the comb filter.

        :param gain: gain between -1 and + 1
        """
        self.gain = gain

    def __feedback(self, input_sample):
        """
        Feedback comb filtering.

        :param input_sample: input sample
        :return: filtered sample
        """
        return (input_sample +
                self.gain * self.delayline.process_sample(self.y1))

    def __feedforward(self, input_sample):
        """
        Feedforward comb filtering.

        :param input_sample: input sample
        :return: filtered sample
        """
        return (input_sample +
                self.gain * self.delayline.process_sample(input_sample))

    def __allpass(self, input_sample):
        """
        All-pass comb filtering.

        :param input_sample: input sample
        :return: filtered sample
        """
        return (self.gain * input_sample - self.gain * self.y1 + self.x1)

    def process_sample(self, input_sample):
        """
        Filter a single sample.

        :param input_sample: input sample
        :return: filtered sample
        """
        return self.__combfunc(input_sample)

    def process(self, input_signal, output_signal):
        """
        Filter an input signal.

        :param input_signal: input signal
        :param output_signal: filtered signal
        """
        size = len(input_signal)
        for i in range(0, size):
            output_signal[i] = self.process_sample(input_signal[i])
            self.x1 = input_signal[i]
            self.y1 = output_signal[i]


class Convolution:
    """
    The convolution filter performs FIR filtering using a provided impulse
    response signal.

    *Warning:*
        It should not be used in practice for computational reasons,
        and should only be used for testing purposes. Instead, prefer
        using the :py:class:`FastConvolution`.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, framesize, impulse_response):
        """
        Create a convolution filter.

        :param framesize: framesize of input buffers to be filtered
        :param impulse_response: the impulse response signal to used
        """
        self.framesize = framesize
        self.impulse_response = impulse_response
        self.irsize = len(impulse_response)
        self.convsize = self.framesize + self.irsize - 1
        self.olapsize = self.convsize - self.framesize
        self.conv = [0] * self.convsize
        self.olap = [0] * self.olapsize

    def process(self, input_signal, output_signal):
        """
        Filter an input signal with the impulse response.
        The length of the input signal must be the one defined at filter
        creation.

        The filtered output signal will be of the same length. The 'tail' of
        the convolution will be added to the beginning of the next filtered
        signal.

        To obtain the 'tail' of the convolution without filtering another
        signal, simply process an input signal filled with zeros.

        :param input_signal: input signal to be filtered
        :param output_signal: filtered signal
        """
        for i in range(0, self.convsize):
            self.conv[i] = 0

        for i in range(0, self.framesize):
            for j in range(0, self.irsize):
                self.conv[i + j] += input_signal[i] * self.impulse_response[j]

        if self.olapsize <= self.framesize:
            for i in range(0, self.olapsize):
                output_signal[i] = self.conv[i] + self.olap[i]

            for i in range(self.olapsize, self.framesize):
                output_signal[i] = self.conv[i]

            for i in range(self.framesize, self.convsize):
                self.olap[i - self.framesize] = self.conv[i]
        else:
            for i in range(0, self.framesize):
                output_signal[i] = self.conv[i] + self.olap[i]

            for i in range(self.framesize, self.olapsize):
                self.olap[i - self.framesize] = self.olap[i] + self.conv[i]

            for i in range(self.olapsize, self.convsize):
                self.olap[i - self.framesize] = self.conv[i]


class FastConvolution:
    """
    The fast convolution filter performs FIR filtering using a provided impulse
    response signal.

    This filter uses a faster algorithm than standard :py:class:`Convolution`,
    based on the :py:class:`yodel.analysis.FFT`.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, framesize, impulse_response):
        """
        Create a fast convolution filter.

        :param framesize: framesize of input buffers to be filtered
        :param impulse_response: the impulse response signal to used
        """
        self.framesize = framesize
        self.irsize = len(impulse_response)
        self.convsize = self.framesize + self.irsize - 1
        self.fftsize = 1 << int(math.ceil(math.log(self.convsize, 2)))
        self.olapsize = self.convsize - self.framesize

        self.ir = [0] * self.fftsize
        self.ir_real = [0] * self.fftsize
        self.ir_imag = [0] * self.fftsize
        self.signal = [0] * self.fftsize
        self.signal_real = [0] * self.fftsize
        self.signal_imag = [0] * self.fftsize
        self.olap = [0] * self.olapsize

        for i in range(0, self.irsize):
            self.ir[i] = impulse_response[i]

        self.fft = yodel.analysis.FFT(self.fftsize)
        self.fft.forward(self.ir, self.ir_real, self.ir_imag)

    def process(self, input_signal, output_signal):
        """
        Filter an input signal with the impulse response.
        The length of the input signal must be the one defined at filter
        creation.

        The filtered output signal will be of the same length. The 'tail' of
        the convolution will be added to the beginning of the next filtered
        signal.

        To obtain the 'tail' of the convolution without filtering another
        signal, simply process an input signal filled with zeros.

        :param input_signal: input signal to be filtered
        :param output_signal: filtered signal
        """
        for i in range(0, self.framesize):
            self.signal[i] = input_signal[i]

        for i in range(self.framesize, self.fftsize):
            self.signal[i] = 0

        self.fft.forward(self.signal, self.signal_real, self.signal_imag)

        for i in range(0, int((self.fftsize/2)+1)):
            temp = (self.signal_real[i] * self.ir_real[i] -
                    self.signal_imag[i] * self.ir_imag[i])
            self.signal_imag[i] = (self.signal_real[i] * self.ir_imag[i] +
                                   self.signal_imag[i] * self.ir_real[i])
            self.signal_real[i] = temp

        self.fft.inverse(self.signal_real, self.signal_imag, self.signal)

        if self.olapsize <= self.framesize:
            for i in range(0, self.olapsize):
                output_signal[i] = self.signal[i] + self.olap[i]

            for i in range(self.olapsize, self.framesize):
                output_signal[i] = self.signal[i]

            for i in range(self.framesize, self.convsize):
                self.olap[i - self.framesize] = self.signal[i]
        else:
            for i in range(0, self.framesize):
                output_signal[i] = self.signal[i] + self.olap[i]

            for i in range(self.framesize, self.olapsize):
                self.olap[i - self.framesize] = self.olap[i] + self.signal[i]

            for i in range(self.olapsize, self.convsize):
                self.olap[i - self.framesize] = self.signal[i]


class WindowedSinc:
    """
    A windowed sinc filter allows to separate one frequency band from another,
    using :py:meth:`low_pass`, :py:meth:`high_pass`, :py:meth:`band_pass` and
    :py:meth:`band_reject` forms.
    Windowing is done using a Blackman :py:class:`yodel.analysis.Window`.
    The filtering is performed with a :py:class:`FastConvolution` filter.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, samplerate, framesize):
        """
        Create a windowed sinc filter with a flat frequency response.

        :param samplerate: sample-rate in Hz
        :param framesize: framesize of input buffers to be filtered
        """
        self.samplerate = samplerate
        self.framesize = framesize
        self.cutoff = 0
        self.kernelsize = 3
        self.kernel = [0] * self.kernelsize
        self.kernel[0] = 1
        self.win = yodel.analysis.Window(self.kernelsize)
        self.win.blackman(self.kernelsize)
        self.conv = FastConvolution(self.framesize, self.kernel)

    def low_pass(self, cutoff, bandwidth):
        """
        Make a low-pass filter with given cutoff frequency and bandwidth.
        Lowering the bandwidth will increase the size of the kernel filter,
        thus increasing the roll-off rate but also the computation cost.

        :param cutoff: cut-off frequency in Hz
        :param bandwidth: frequency band width in Hz
        """
        self.cutoff = cutoff
        normcutoff = cutoff / self.samplerate
        self.kernelsize = int(4.0 * self.samplerate / bandwidth)
        if (self.kernelsize % 2) == 0:
            self.kernelsize += 1
        self.kernel = [0] * self.kernelsize
        kernelsizeon2 = int((self.kernelsize-1)/2)

        for i in range(0, self.kernelsize):
            if i == kernelsizeon2:
                self.kernel[i] = 2.0 * math.pi * normcutoff
            else:
                tmp = (i - kernelsizeon2)
                self.kernel[i] = (math.sin(2.0 * math.pi * normcutoff * tmp)
                                  / tmp)

        self.win.blackman(self.kernelsize)
        self.win.process(self.kernel, self.kernel)

        norm = 0
        for i in range(0, self.kernelsize):
            norm += self.kernel[i]

        for i in range(0, self.kernelsize):
            self.kernel[i] /= norm

        self.conv = FastConvolution(self.framesize, self.kernel)

    def high_pass(self, cutoff, bandwidth):
        """
        Make a high-pass filter with given cutoff frequency and bandwidth.
        Lowering the bandwidth will increase the size of the kernel filter,
        thus increasing the roll-off rate but also the computation cost.

        :param cutoff: cut-off frequency in Hz
        :param bandwidth: frequency band width in Hz
        """
        self.low_pass(cutoff, bandwidth)

        for i in range(0, self.kernelsize):
            self.kernel[i] *= -1
        self.kernel[int((self.kernelsize-1)/2)] += 1

        self.conv = FastConvolution(self.framesize, self.kernel)

    def band_reject(self, center, bandwidth):
        """
        Make a band-reject filter with given center frequency and bandwidth.
        Lowering the bandwidth will increase the size of the kernel filter,
        thus increasing the roll-off rate but also the computation cost.

        :param center: center frequency in Hz
        :param bandwidth: frequency band width in Hz
        """
        self.low_pass(center - bandwidth/2.0, bandwidth/2.0)

        lowpass = [0] * self.kernelsize
        for i in range(0, self.kernelsize):
            lowpass[i] = self.kernel[i]

        self.high_pass(center + bandwidth/2.0, bandwidth/2.0)

        for i in range(0, self.kernelsize):
            self.kernel[i] += lowpass[i]

        self.conv = FastConvolution(self.framesize, self.kernel)

    def band_pass(self, center, bandwidth):
        """
        Make a band-pass filter with given center frequency and bandwidth.
        Lowering the bandwidth will increase the size of the kernel filter,
        thus increasing the roll-off rate but also the computation cost.

        :param center: center frequency in Hz
        :param bandwidth: frequency band width in Hz
        """
        self.band_reject(center, bandwidth)

        for i in range(0, self.kernelsize):
            self.kernel[i] *= -1
        self.kernel[int((self.kernelsize-1)/2)] += 1

        self.conv = FastConvolution(self.framesize, self.kernel)


class Custom:
    """
    A custom filter allows to design precisely the frequency response of a
    digital filter. The filtering is then performed with a
    :py:class:`FastConvolution` filter.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, samplerate, framesize):
        """
        Create a custom filter with a flat frequency response.
        By default, the filter has a latency of (framesize/2) samples.

        :param samplerate: sample-rate in Hz
        :param framesize: framesize of input buffers to be filtered
        """
        self.samplerate = samplerate
        self.framesize = framesize
        flatresp = [1] * int((framesize/2)+1)
        self.design(flatresp, False)

    def design(self, freqresponse, db=True):
        """
        Create the filter impulse response from the specified frequency
        response.

        The response must represent the desired spectrum, and of
        size (Nfft/2+1). The latency of the filter will be of (Nfft/2) samples.

        The values of the frequency bands can either be specified in linear
        scale (1 being flat) or in dB scale (0 being flat).

        :param freqresponse: desired frequency response
        :param db: True if the frequency response is specified in dB
        """
        self.frsize = len(freqresponse)
        self.fftsize = int((self.frsize-1) * 2)
        self.latency = int(self.fftsize / 2)
        self.fr_real = [0] * self.fftsize
        self.fr_imag = [0] * self.fftsize
        self.ir = [0] * self.fftsize
        self.shifted_ir = [0] * self.fftsize

        for i in range(0, self.frsize):
            if db:
                self.fr_real[i] = yodel.conversion.db2lin(freqresponse[i])
            else:
                self.fr_real[i] = freqresponse[i]

        self.fft = yodel.analysis.FFT(self.fftsize)
        self.fft.inverse(self.fr_real, self.fr_imag, self.ir)

        for i in range(0, self.fftsize):
            index = int(i + self.frsize) % self.fftsize
            self.shifted_ir[index] = self.ir[i]

        self.win = yodel.analysis.Window(self.fftsize)
        self.win.blackman(self.fftsize)
        self.win.process(self.shifted_ir, self.ir)

        self.fir = FastConvolution(self.framesize, self.ir)

    def process(self, input_signal, output_signal):
        """
        Filter an input signal with the custom impulse response.
        The length of the input signal must be the one defined at filter
        creation.

        As with :py:class:`Convolution`, the filtered output signal will be
        of the same length. The 'tail' of the convolution will be added to the
        beginning of the next filtered signal.

        To obtain the 'tail' of the convolution without filtering another
        signal, simply process an input signal filled with zeros.

        :param input_signal: input signal to be filtered
        :param output_signal: filtered signal
        """
        self.fir.process(input_signal, output_signal)
