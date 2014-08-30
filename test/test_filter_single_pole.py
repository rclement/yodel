import unittest
import math
import random
import yodel.filter
import yodel.analysis
import yodel.conversion
import yodel.complex


class TestLowPassFilter(unittest.TestCase):

    def setUp(self):
        self.flt = yodel.filter.SinglePole()
        pass

    def test_coefficients(self):
        samplerate = 48000
        x = 0.86
        a0 = 1 - x
        a1 = 0.0
        b1 = x
        cutoff = (math.log(x) / (-2.0 * math.pi)) * samplerate
        self.flt.low_pass(samplerate, cutoff)

        self.assertAlmostEqual(a0, self.flt._a0)
        self.assertAlmostEqual(a1, self.flt._a1)
        self.assertAlmostEqual(b1, self.flt._b1)


class TestHighPassFilter(unittest.TestCase):

    def setUp(self):
        self.flt = yodel.filter.SinglePole()
        pass

    def test_coefficients(self):
        samplerate = 48000
        x = 0.86
        a0 = (1.0 + x) / 2.0
        a1 = - (1.0 + x) / 2.0
        b1 = x
        cutoff = (math.log(x) / (-2.0 * math.pi)) * samplerate
        self.flt.high_pass(samplerate, cutoff)

        self.assertAlmostEqual(a0, self.flt._a0)
        self.assertAlmostEqual(a1, self.flt._a1)
        self.assertAlmostEqual(b1, self.flt._b1)


class TestFlatFilter(unittest.TestCase):

    def setUp(self):
        self.block_size = 512
        self.flt = yodel.filter.SinglePole()
        pass

    def common_check_flat_response(self):
        self.flt.process(self.signal, self.output)
        for i in range(0, self.block_size):
            self.assertEqual(self.signal[i], self.output[i])

    def test_zero_signal(self):
        self.signal = [0] * self.block_size
        self.output = [0] * self.block_size
        self.common_check_flat_response()

    def test_dirac_signal(self):
        self.signal = [0] * self.block_size
        self.signal[0] = 1
        self.output = [0] * self.block_size
        self.common_check_flat_response()

    def test_sine_signal(self):
        self.signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.output = [0] * self.block_size
        self.common_check_flat_response()

    def test_random_signal(self):
        self.signal = [random.random() for i in range(0, self.block_size)]
        self.output = [0] * self.block_size
        self.common_check_flat_response()


if __name__ == '__main__':
    unittest.main()

