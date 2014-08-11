import unittest
import array
import math
import yodel.analysis


class CommonFourierTest():

    def setUp(self):
        self.samplerate = 44100
        self.length = 32
        self.lengthspec = self.length
        self.epsilon = 0.00001
        self.signal    = array.array('f', [0.0] * self.length)
        self.real_spec = array.array('f', [0.0] * self.lengthspec)
        self.imag_spec = array.array('f', [0.0] * self.lengthspec)
        self.fourier = self.create_fourier()

    def tearDown(self):
        pass

    def test_forward_dirac(self):
        self.signal[0] = 1.0
        self.fourier.forward(self.signal, self.real_spec, self.imag_spec)

        self.assertEqual(self.real_spec, array.array('f', [1.0] * self.lengthspec))
        self.assertEqual(self.imag_spec, array.array('f', [0.0] * self.lengthspec))

    def test_inverse_dirac(self):
        for i in range(0, self.length):
            self.real_spec[i] = 1.0
            self.imag_spec[i] = 0.0
        self.fourier.inverse(self.real_spec, self.imag_spec, self.signal)

        self.assertAlmostEqual(self.signal[0], 1.0, delta=self.epsilon)
        for i in range(1, self.length):
            self.assertAlmostEqual(self.signal[i], 0.0, delta=self.epsilon)

    def test_forward_inverse_dirac(self):
        self.signal[0] = 1.0
        self.fourier.forward(self.signal, self.real_spec, self.imag_spec)
        self.fourier.inverse(self.real_spec, self.imag_spec, self.signal)

        self.assertAlmostEqual(self.signal[0], 1.0, delta=self.epsilon)
        for i in range(1, self.length):
            self.assertAlmostEqual(self.signal[i], 0.0, delta=self.epsilon)

    def test_forward_inverse_sine(self):
        sine_ref = array.array('f', [0] * self.length);
        for i in range(0, self.length):
            sine_ref[i] = math.sin((2.0 * math.pi * 440.0 / self.samplerate) * i)
            self.signal[i] = sine_ref[i]
        self.fourier.forward(self.signal, self.real_spec, self.imag_spec)
        self.fourier.inverse(self.real_spec, self.imag_spec, self.signal)

        for i in range(0, self.length):
            self.assertAlmostEqual(self.signal[i], sine_ref[i], delta=self.epsilon)


class TestDFT(unittest.TestCase, CommonFourierTest):

    def setUp(self):
        CommonFourierTest.setUp(self)

    def tearDown(self):
        CommonFourierTest.tearDown(self)

    def create_fourier(self):
        return yodel.analysis.DFT(self.length)


class TestFFT(unittest.TestCase, CommonFourierTest):

    def setUp(self):
        CommonFourierTest.setUp(self)

    def tearDown(self):
        CommonFourierTest.tearDown(self)

    def create_fourier(self):
        return yodel.analysis.FFT(self.length)


if __name__ == '__main__':
    unittest.main()
