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


class TestStateVariableFilter(unittest.TestCase):

    def setUp(self):
        self.sample_rate = 48000
        self.block_size = 512
        self.delta = (1.0 / self.block_size) * self.sample_rate
        self.signal = [0] * self.block_size
        self.output_hp = [0] * self.block_size
        self.output_bp = [0] * self.block_size
        self.output_lp = [0] * self.block_size
        self.output_br = [0] * self.block_size
        self.flt = yodel.filter.StateVariable()

    def tearDown(self):
        pass

    def common_check_flat_response(self):
        self.flt.process(self.signal, self.output_hp, self.output_bp, self.output_lp, self.output_br)
        for i in range(0, self.block_size):
            self.assertEqual(self.signal[i], self.output_hp[i])
            self.assertEqual(self.signal[i], self.output_br[i])
            self.assertEqual(0, self.output_bp[i])
            self.assertEqual(0, self.output_lp[i])

    def common_check_hp_response(self):
        hpf_real, hpf_imag = frequency_response(self.output_hp)
        hpf_spec = amplitude_response(hpf_real, hpf_imag)

        fc_approx = 0
        prev = hpf_spec[0]
        for i in range(1, int(self.block_size/2)):
            curr = hpf_spec[i]
            if curr > 0 and prev <= 0:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def common_check_bp_response(self):
        bpf_real, bpf_imag = frequency_response(self.output_bp)
        bpf_spec = amplitude_response(bpf_real, bpf_imag)

        fc_approx = 0
        prev = bpf_spec[0]
        for i in range(1, int(self.block_size/2)-1):
            curr = bpf_spec[i]
            after = bpf_spec[i+1]
            if curr >= prev and curr >= after:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def common_check_lp_response(self):
        lpf_real, lpf_imag = frequency_response(self.output_lp)
        lpf_spec = amplitude_response(lpf_real, lpf_imag)

        fc_approx = 0
        prev = lpf_spec[0]
        for i in range(1, int(self.block_size/2)):
            curr = lpf_spec[i]
            if curr <= 0 and prev > 0:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def common_check_br_response(self):
        brf_real, brf_imag = frequency_response(self.output_br)
        brf_spec = amplitude_response(brf_real, brf_imag)

        fc_approx = 0
        prev = brf_spec[0]
        for i in range(1, int(self.block_size/2)-1):
            curr = brf_spec[i]
            after = brf_spec[i+1]
            if curr <= prev and curr <= after:
                fc_approx = (float(i) / float(self.block_size)) * self.sample_rate
                break
            else:
                prev = curr

        self.assertAlmostEqual(self.fc, fc_approx, delta=self.delta)

    def test_flat_zero(self):
        self.flt.reset()
        self.common_check_flat_response()

    def test_flat_dirac(self):
        self.flt.reset()
        self.signal[0] = 1
        self.common_check_flat_response()

    def test_flat_sine(self):
        self.flt.reset()
        self.signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.common_check_flat_response()

    def common_test_cutoff_frequency(self, fc):
        self.fc = fc
        self.qfactor = 1
        self.signal[0] = 1

        self.flt.set(self.sample_rate, self.fc, self.qfactor)
        self.flt.process(self.signal, self.output_hp, self.output_bp, self.output_lp, self.output_br)

        self.common_check_hp_response()
        self.common_check_bp_response()
        self.common_check_lp_response()
        self.common_check_br_response()

    def test_cutoff_frequency(self):
        self.common_test_cutoff_frequency(200)
        self.common_test_cutoff_frequency(500)
