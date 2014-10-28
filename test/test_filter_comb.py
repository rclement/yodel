import unittest
import math
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


def amplitude_response(spec_real, spec_imag, db=False):
    size = len(spec_real)
    amp = [0] * size
    for i in range(0, size):
        amp[i] = yodel.complex.modulus(spec_real[i], spec_imag[i])
        if db:
            amp[i] = yodel.conversion.lin2db(amp[i])
    return amp


class TestFeedforwardCombFilter(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000.0
        self.block_size = 512
        self.delay = 0.25
        self.gain = 0.5
        self.comb = yodel.filter.Comb(self.samplerate, self.delay, self.gain)
        self.comb.feedforward(self.delay, self.gain)

    def test_frequency_response(self):
        self._impulse_response = impulse_response(self.comb, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False) 

        stephz = self.samplerate / self.block_size
        periodhz = 1000.0 / self.delay

        for i in range(0, int(self.samplerate/2.0), int(periodhz)):
            self.assertAlmostEqual(self._amplitude_response[int(i/stephz)], 1.5, delta=0.1)

        for i in range(int(periodhz/2.0), int(self.samplerate/2.0), int(periodhz)):
            self.assertAlmostEqual(self._amplitude_response[int(i/stephz)], 0.5, delta=0.1)


class TestFeedbackCombFilter(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000.0
        self.block_size = 512
        self.delay = 0.25
        self.gain = 0.5
        self.comb = yodel.filter.Comb(self.samplerate, self.delay, self.gain)
        self.comb.feedback(self.delay, self.gain)

    def test_frequency_response(self):
        self._impulse_response = impulse_response(self.comb, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False) 

        stephz = self.samplerate / self.block_size
        periodhz = 1000.0 / self.delay

        for i in range(0, int(self.samplerate/2.0), int(periodhz)):
            self.assertAlmostEqual(self._amplitude_response[int(i/stephz)], 2.0, delta=0.1)

        for i in range(int(periodhz/2.0), int(self.samplerate/2.0), int(periodhz)):
            self.assertAlmostEqual(self._amplitude_response[int(i/stephz)], 0.66, delta=0.1)


class TestAllpassCombFilter(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000.0
        self.block_size = 512
        self.delay = 0.25
        self.gain = 0.5
        self.comb = yodel.filter.Comb(self.samplerate, self.delay, self.gain)
        self.comb.allpass(self.delay, self.gain)

    def test_frequency_response(self):
        self._impulse_response = impulse_response(self.comb, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False) 

        for i in range(0, self.block_size):
            self.assertAlmostEqual(self._amplitude_response[i], 1.0)


if __name__ == '__main__':
    unittest.main()
