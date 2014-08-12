import unittest
import array
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


def amplitude_response(spec_real, spec_imag, db = False):
    size = len(spec_real)
    amp = [0] * size
    for i in range(0, size):
        amp[i] = yodel.complex.modulus(spec_real[i], spec_imag[i])
        if db:
            amp[i] = yodel.conversion.lin2db(amp[i])
    return amp


class TestLowPassFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.lpf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.fc = fc
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
        self.common_test_cutoff(int(self.sample_rate/2.0)-1000)


class TestHighPassFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.hpf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.fc = fc
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
        self.common_test_cutoff(int(self.sample_rate/2.0)-1000)


class TestBandPassFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.bpf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.fc = fc
        self.bpf.band_pass(self.sample_rate, self.fc, self.q)
        self._impulse_response = impulse_response(self.bpf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False)

        fc_approx = 0
        prev = self._amplitude_response[0]
        for i in range(1, int(self.block_size/2)-1):
            curr = self._amplitude_response[i]
            after = self._amplitude_response[i+1]
            if curr >= prev and curr >= after:
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
        self.common_test_cutoff(int(self.sample_rate/2.0)-1000)


class TestNotchFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.nf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff(self, fc):
        self.fc = fc
        self.nf.notch(self.sample_rate, self.fc, self.q)
        self._impulse_response = impulse_response(self.nf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, False)

        fc_approx = 0
        prev = self._amplitude_response[0]
        for i in range(1, int(self.block_size/2)-1):
            curr = self._amplitude_response[i]
            after = self._amplitude_response[i+1]
            if curr <= prev and curr <= after:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def test_cutoff_frequency(self):
        self.common_test_cutoff(100)
        self.common_test_cutoff(1000)
        self.common_test_cutoff(10000)
        self.common_test_cutoff(20000)
        self.common_test_cutoff(int(self.sample_rate/2.0)-1000)


class TestPeakFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.dbgain = 0
        self.pf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff_gain(self, fc, gain):
        self.fc = fc
        self.dbgain = gain
        self.pf.peak(self.sample_rate, self.fc, self.q, self.dbgain)
        self._impulse_response = impulse_response(self.pf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, True)

        fc_approx = 0
        gain_approx = 0
        prev = self._amplitude_response[0]

        if (self.dbgain >= 0) :
            for i in range(1, int(self.block_size/2)-1):
                curr = self._amplitude_response[i]
                after = self._amplitude_response[i+1]
                if curr >= prev and curr >= after:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    gain_approx = curr
                    break
                else:
                    prev = curr
        else:
            for i in range(1, int(self.block_size/2)-1):
                curr = self._amplitude_response[i]
                after = self._amplitude_response[i+1]
                if curr <= prev and curr <= after:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    gain_approx = curr
                    break
                else:
                    prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)
        self.assertAlmostEqual(self.dbgain, gain_approx, delta=1)

    def test_cutoff_frequency(self):
        self.common_test_cutoff_gain(200, 5)
        self.common_test_cutoff_gain(300, -5)
        self.common_test_cutoff_gain(500, 20)
        self.common_test_cutoff_gain(8000, -19)
        self.common_test_cutoff_gain(1000, 2.5)
        self.common_test_cutoff_gain(10000, -4.8)
        self.common_test_cutoff_gain(20000, 10)
        self.common_test_cutoff_gain(int(self.sample_rate/2.0)-1000, -0.5)


class TestLowShelfFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.dbgain = 0
        self.lsf= yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff_gain_q(self, fc, gain, q):
        self.fc = fc
        self.dbgain = gain
        self.q = q
        self.lsf.low_shelf(self.sample_rate, self.fc, self.q, self.dbgain)
        self._impulse_response = impulse_response(self.lsf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, True)

        fc_approx = 0
        gain_approx = self._amplitude_response[0]
        prev = self._amplitude_response[0]

        if (self.dbgain >= 0) :
            for i in range(1, int(self.block_size/2)):
                curr = self._amplitude_response[i]
                if curr <= 0 and prev > 0:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    break
                else:
                    prev = curr
        else:
            for i in range(1, int(self.block_size/2)):
                curr = self._amplitude_response[i]
                if curr >= 0 and prev < 0:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    break
                else:
                    prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)
        self.assertAlmostEqual(self.dbgain, gain_approx, delta=1)

    def test_cutoff_frequency(self):
        self.common_test_cutoff_gain_q(500, 2, 10)
        self.common_test_cutoff_gain_q(600, 5, 10)
        self.common_test_cutoff_gain_q(1700, -3, 10)
        self.common_test_cutoff_gain_q(5000, -1.5, 10)


class TestHighShelfFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.dbgain = 0
        self.hsf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_cutoff_gain_q(self, fc, gain, q):
        self.fc = fc
        self.dbgain = gain
        self.q = q
        self.hsf.high_shelf(self.sample_rate, self.fc, self.q, self.dbgain)
        self._impulse_response = impulse_response(self.hsf, self.block_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        self._amplitude_response = amplitude_response(self._freq_response_real, self._freq_response_imag, True)

        fc_approx = 0
        gain_approx = self._amplitude_response[int(self.block_size/2)-1]
        prev = self._amplitude_response[0]

        if (self.dbgain >= 0) :
            for i in range(1, int(self.block_size/2)):
                curr = self._amplitude_response[i]
                if curr >= 0 and prev < 0:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    break
                else:
                    prev = curr
        else:
            for i in range(1, int(self.block_size/2)):
                curr = self._amplitude_response[i]
                if curr <= 0 and prev > 0:
                    fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                    break
                else:
                    prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)
        self.assertAlmostEqual(self.dbgain, gain_approx, delta=1)

    def test_cutoff_frequency(self):
        self.common_test_cutoff_gain_q(500, 2, 10)
        self.common_test_cutoff_gain_q(600, 5, 10)
        self.common_test_cutoff_gain_q(1700, -3, 10)
        self.common_test_cutoff_gain_q(5000, -1.5, 10)


class TestCustomFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.fc = 100
        self.q = 1
        self.dbgain = 0
        self.cf = yodel.filter.Biquad()
        self.input_signal = [0] * self.block_size
        self.output_signal = [0] * self.block_size
        self.input_signal[0] = 1

    def tearDown(self):
        pass

    def common_test_custom_coefficients(self, a, b):
        self.cf.custom(a[0], a[1], a[2], b[0], b[1], b[2])
        self.assertAlmostEqual(a[0],      self.cf._a_coeffs[0], delta=0.001)
        self.assertAlmostEqual(a[1]/a[0], self.cf._a_coeffs[1], delta=0.001)
        self.assertAlmostEqual(a[2]/a[0], self.cf._a_coeffs[2], delta=0.001)
        self.assertAlmostEqual(b[0]/a[0], self.cf._b_coeffs[0], delta=0.001)
        self.assertAlmostEqual(b[1]/a[0], self.cf._b_coeffs[1], delta=0.001)
        self.assertAlmostEqual(b[2]/a[0], self.cf._b_coeffs[2], delta=0.001)

    def test_custom_coefficients(self):
        self.common_test_custom_coefficients([0.72, 1.1, 2.09], [0.0, 0.01, 12])


if __name__ == '__main__':
    unittest.main()

