import unittest
import yodel.filter


class CommonConvolutionTest:

    def setUp(self):
        self.signal_length = 4
        self.signal = [0] * self.signal_length
        self.signal[0] = 1.0
        self.signal[1] = 0.5
        self.signal[2] = 0.25
        self.signal[3] = 0.125

    def tearDown(self):
        pass

    def test_identity_ir(self):
        self.ir_length = 1
        self.ir = [0] * self.ir_length
        self.ir[0] = 1

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        for i in range(0, self.signal_length):
            self.assertEqual(self.signal[i], self.output[i])

    def test_reverse_ir(self):
        self.ir_length = 1
        self.ir = [0] * self.ir_length
        self.ir[0] = -1

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        for i in range(0, self.signal_length):
            self.assertEqual(- self.signal[i], self.output[i])

    def test_scale_ir(self):
        self.ir_length = 1
        self.ir = [0] * self.ir_length
        self.ir[0] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        for i in range(0, self.signal_length):
            self.assertEqual(self.ir[0] * self.signal[i], self.output[i])

    def test_delay_ir(self):
        self.ir_length = 3
        self.ir = [0] * self.ir_length
        self.ir[0] = 0.0
        self.ir[1] = 0.0
        self.ir[2] = 1.0

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        self.assertEqual(self.ir[0] * self.signal[0], self.output[0])
        self.assertEqual(self.ir[1] * self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertEqual(self.signal[i - self.ir_length + 1], self.output[i])

    def test_delay_scale_ir(self):
        self.ir_length = 3
        self.ir = [0] * self.ir_length
        self.ir[0] = 0.0
        self.ir[1] = 0.0
        self.ir[2] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        self.assertEqual(self.ir[0] * self.signal[0], self.output[0])
        self.assertEqual(self.ir[1] * self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertEqual(0.5 * self.signal[i - self.ir_length + 1], self.output[i])

    def test_overlapping_echo_ir(self):
        self.ir_length = 3
        self.ir = [0] * self.ir_length
        self.ir[0] = 1.0
        self.ir[1] = 0.0
        self.ir[2] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * (self.signal_length)
        self.fir.process(self.signal, self.output)

        self.assertEqual(self.signal[0], self.output[0])
        self.assertEqual(self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertEqual(0.5 * self.signal[i - self.ir_length + 1] + self.signal[i], self.output[i])

        self.output = [0] * (self.signal_length)
        self.fir.process([0]*self.signal_length, self.output)

        self.assertEqual(0.5 * self.signal[2], self.output[0])
        self.assertEqual(0.5 * self.signal[3], self.output[1])

    def test_non_overlapping_echo_ir(self):
        self.ir_length = 6
        self.ir = [0] * self.ir_length
        self.ir[0] = 1.0
        self.ir[1] = 0.0
        self.ir[2] = 0.0
        self.ir[3] = 0.0
        self.ir[4] = 0.0
        self.ir[5] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * (self.signal_length)
        self.fir.process(self.signal, self.output)

        for i in range(0, self.signal_length):
            self.assertEqual(self.signal[i], self.output[i])

        self.output = [0] * (self.signal_length)
        self.fir.process([0]*self.signal_length, self.output)

        self.assertEqual(0, self.output[0])
        for i in range(0, self.signal_length - 1):
            self.assertEqual(0.5 * self.signal[i], self.output[i+1])


class TestConvolutionFilter(unittest.TestCase, CommonConvolutionTest):

    def setUp(self):
        CommonConvolutionTest.setUp(self)

    def tearDown(self):
        CommonConvolutionTest.tearDown(self)

    def create_convolution_filter(self, framesize, ir):
        return yodel.filter.Convolution(framesize, ir)


if __name__ == '__main__':
    unittest.main()
