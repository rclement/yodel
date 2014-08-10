import math
import array


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
        To make the filter active, use one of the provided methods.
        """
        self.reset()

    def reset(self):
        """
        Make the filter inactive with a flat frequency response.
        """
        self._a_coeffs = array.array('f', [0] * 3)
        self._b_coeffs = array.array('f', [0] * 3)
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
