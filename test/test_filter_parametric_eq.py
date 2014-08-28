import unittest
import math
import random
import yodel.filter
import yodel.analysis
import yodel.conversion
import yodel.complex


def impulse_response(bq, size):
    impulse = [0] * size
    impulse[0] = 1
    response = [0] * size
    bq.process(impulse, response)
    return response


def frequency_response(response):
    size = len(response)
    freq_response_real = [0] * size
    freq_response_imag = [0] * size
    fft = yodel.analysis.FFT(size)
    fft.forward(response, freq_response_real, freq_response_imag)
    return freq_response_real, freq_response_imag


def amplitude_response(spec_real, spec_imag, db=True):
    size = len(spec_real)
    amp = [0] * size
    for i in range(0, size):
        amp[i] = yodel.complex.modulus(spec_real[i], spec_imag[i])
        if db:
            amp[i] = yodel.conversion.lin2db(amp[i])
    return amp


class TestParametricEQFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.bands = 7
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.signal = [0] * self.block_size
        self.filtered = [0] * self.block_size
        self.flt = yodel.filter.ParametricEQ(self.sample_rate, self.bands)

    def tearDown(self):
        pass

    def reset_eq(self):
        for i in range(0, self.bands):
            self.flt.set_band(i, 0, 1.0/math.sqrt(2.0), 0)

    def common_check_flat_response(self):
        self.flt.process(self.signal, self.filtered)
        for i in range(0, self.block_size):
            self.assertAlmostEqual(self.signal[i], self.filtered[i])

    def test_flat_zero(self):
        self.reset_eq()
        self.common_check_flat_response()

    def test_flat_dirac(self):
        self.reset_eq()
        self.signal[0] = 1
        self.common_check_flat_response()

    def test_flat_sine(self):
        self.reset_eq()
        self.signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.common_check_flat_response()


class TestParametricEQFilterNoBands(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.bands = 0
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.signal = [0] * self.block_size
        self.filtered = [0] * self.block_size
        self.flt = yodel.filter.ParametricEQ(self.sample_rate, self.bands)

    def tearDown(self):
        pass

    def reset_eq(self):
        for i in range(0, self.bands):
            self.flt.set_band(i, 0, 1.0/math.sqrt(2.0), 0)

    def common_check_flat_response(self):
        self.flt.process(self.signal, self.filtered)
        for i in range(0, self.block_size):
            self.assertAlmostEqual(self.signal[i], self.filtered[i])

    def test_flat_sine(self):
        self.reset_eq()
        self.signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.common_check_flat_response()


if __name__ == '__main__':
    unittest.main()
