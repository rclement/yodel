import unittest
import yodel.filter


def convolution(signal, ir):
    irsize = len(ir)
    signalsize = len(signal)
    output = [0] * (signalsize + irsize - 1)
    for i in range(0, signalsize):
        for j in range(0, irsize):
            output[i + j] += signal[i] * ir[j]
    return output


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

        self.assertAlmostEqual(self.ir[0] * self.signal[0], self.output[0])
        self.assertAlmostEqual(self.ir[1] * self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertAlmostEqual(self.signal[i - self.ir_length + 1], self.output[i])

    def test_delay_scale_ir(self):
        self.ir_length = 3
        self.ir = [0] * self.ir_length
        self.ir[0] = 0.0
        self.ir[1] = 0.0
        self.ir[2] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)

        self.output = [0] * self.signal_length
        self.fir.process(self.signal, self.output)

        self.assertAlmostEqual(self.ir[0] * self.signal[0], self.output[0])
        self.assertAlmostEqual(self.ir[1] * self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertAlmostEqual(0.5 * self.signal[i - self.ir_length + 1], self.output[i])

    def test_overlapping_echo_ir(self):
        self.ir_length = 3
        self.ir = [0] * self.ir_length
        self.ir[0] = 1.0
        self.ir[1] = 0.0
        self.ir[2] = 0.5

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)
        self.output = [0] * (self.signal_length)
        self.fir.process(self.signal, self.output)

        self.assertAlmostEqual(self.signal[0], self.output[0])
        self.assertAlmostEqual(self.signal[1], self.output[1])
        for i in range(self.ir_length - 1, self.signal_length):
            self.assertAlmostEqual(0.5 * self.signal[i - self.ir_length + 1] + self.signal[i], self.output[i])

        self.output = [0] * (self.signal_length)
        self.fir.process([0]*self.signal_length, self.output)

        self.assertAlmostEqual(0.5 * self.signal[2], self.output[0])
        self.assertAlmostEqual(0.5 * self.signal[3], self.output[1])

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
            self.assertAlmostEqual(self.signal[i], self.output[i])

        self.output = [0] * (self.signal_length)
        self.fir.process([0]*self.signal_length, self.output)

        self.assertAlmostEqual(0, self.output[0])
        for i in range(0, self.signal_length - 1):
            self.assertAlmostEqual(0.5 * self.signal[i], self.output[i+1])

    def test_long_ir_with_short_block(self):
        self.ir = [1, 0, 0.5, 0, 0.25, 0, 0.125, 0, 0.678]
        self.ir_length = len(self.ir)
        self.signal = [1, 1]
        self.signal_length = len(self.signal)
        self.output = [0] * (self.ir_length + self.signal_length - 1)
        outputtmp = [0] * self.signal_length
        refconv = convolution(self.signal, self.ir)

        self.fir = self.create_convolution_filter(self.signal_length, self.ir)
         
        n = int((self.ir_length + self.signal_length - 1) / self.signal_length)
        rem = (self.ir_length + self.signal_length - 1) - (n * self.signal_length)
        
        for i in range(0, n):
            if i == 0:
                self.fir.process(self.signal, outputtmp)
            else:
                self.fir.process([0] * self.signal_length, outputtmp)
            for j in range(0, self.signal_length):
                self.output[i * self.signal_length + j] = outputtmp[j]
        
        self.fir.process([0] * self.signal_length, outputtmp)
        for i in range(0, rem):
            self.output[n * self.signal_length + i] = outputtmp[i]

        for i in range(0, (self.ir_length + self.signal_length - 1)):
            self.assertAlmostEqual(refconv[i], self.output[i]);


class TestConvolutionFilter(unittest.TestCase, CommonConvolutionTest):

    def setUp(self):
        CommonConvolutionTest.setUp(self)

    def tearDown(self):
        CommonConvolutionTest.tearDown(self)

    def create_convolution_filter(self, framesize, ir):
        return yodel.filter.Convolution(framesize, ir)


class TestFastConvolutionFilter(unittest.TestCase, CommonConvolutionTest):

    def setUp(self):
        CommonConvolutionTest.setUp(self)

    def tearDown(self):
        CommonConvolutionTest.tearDown(self)

    def create_convolution_filter(self, framesize, ir):
        return yodel.filter.FastConvolution(framesize, ir)


if __name__ == '__main__':
    unittest.main()
