import unittest
import array
import math
import damn.filter
import damn.analysis
import damn.conversion
import damn.complex


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
    fft = damn.analysis.FFT(size)
    fft.forward(response, freq_response_real, freq_response_imag)
    return freq_response_real, freq_response_imag


def amplitude_response(spec_real, spec_imag, db = False):
    size = len(spec_real)
    amp = [0] * size
    for i in range(0, size):
        amp[i] = damn.complex.modulus(spec_real[i], spec_imag[i])
        if db:
            amp[i] = damn.conversion.lin2db(amp[i])
    return amp


class TestLowPassFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.lpf = damn.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.lpf.low_pass(self.sample_rate, self.fc, self.q)
        self._impulse_response = impulse_response(self.lpf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False)

        fc_approx = 0
        prev = self._amplitude_response[0]
        for i in range(1, int(self.block_size/2)):
            curr = self._amplitude_response[i]
            if curr <= 1 and prev > 1:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def test_cutoff_frequency(self):
        self.common_test_cutoff(0)
        self.common_test_cutoff(1)
        self.common_test_cutoff(10)
        self.common_test_cutoff(100)
        self.common_test_cutoff(1000)
        self.common_test_cutoff(10000)
        self.common_test_cutoff(20000)
        self.common_test_cutoff(self.sample_rate/2)


class TestHighPassFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.hpf = damn.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.hpf.high_pass(self.sample_rate, self.fc, self.q)
        self._impulse_response = impulse_response(self.hpf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False)

        fc_approx = 0
        prev = self._amplitude_response[0]
        for i in range(1, int(self.block_size/2)):
            curr = self._amplitude_response[i]
            if curr > 1 and prev <= 1:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def test_cutoff_frequency(self):
        self.common_test_cutoff(0)
        self.common_test_cutoff(1)
        self.common_test_cutoff(10)
        self.common_test_cutoff(100)
        self.common_test_cutoff(1000)
        self.common_test_cutoff(10000)
        self.common_test_cutoff(20000)
        self.common_test_cutoff(self.sample_rate/2)


if __name__ == '__main__':
    unittest.main()

