import unittest
import math
import yodel.analysis


class TestAnalysisWindow(unittest.TestCase):

    def setUp(self):
        self.block_size = 512
        self.win = yodel.analysis.Window(self.block_size)

    def tearDown(self):
        pass

    def test_rectangular_window(self):
        self.win.rectangular(self.block_size)

        for i in range(0, self.block_size):
            self.assertEqual(self.win.signal[i], 1.0)

        self.input_signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.output_signal = [0] * self.block_size
        self.win.process(self.input_signal, self.output_signal)

        for i in range(0, self.block_size):
            self.assertEqual(self.input_signal[i], self.output_signal[i])

    def test_hanning_window(self):
        self.win.hanning(self.block_size)

        self.assertEqual(self.win.signal[0], 0.0)
        self.assertEqual(self.win.signal[self.block_size - 1], 0.0)

        for i in range(0, int(self.block_size / 2)):
            self.assertAlmostEqual(self.win.signal[i], self.win.signal[self.block_size - 1 - i])

        self.input_signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.output_signal = [0] * self.block_size
        self.win.process(self.input_signal, self.output_signal)

        self.assertEqual(self.output_signal[0], 0.0)
        self.assertEqual(self.output_signal[self.block_size - 1], 0.0)

    def test_hamming_window(self):
        self.win.hamming(self.block_size)

        self.assertAlmostEqual(self.win.signal[0], 0.08)
        self.assertAlmostEqual(self.win.signal[self.block_size - 1], 0.08)

        for i in range(0, int(self.block_size / 2)):
            self.assertAlmostEqual(self.win.signal[i], self.win.signal[self.block_size - 1 - i])

        self.input_signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.output_signal = [0] * self.block_size
        self.win.process(self.input_signal, self.output_signal)

        self.assertAlmostEqual(self.output_signal[0], self.input_signal[0] * 0.08)
        self.assertAlmostEqual(self.output_signal[self.block_size - 1], self.input_signal[self.block_size - 1] * 0.08)

    def test_blackman_window(self):
        self.win.blackman(self.block_size)

        self.assertAlmostEqual(self.win.signal[0], 0.006879)
        self.assertAlmostEqual(self.win.signal[self.block_size - 1], 0.006879)

        for i in range(0, int(self.block_size / 2)):
            self.assertAlmostEqual(self.win.signal[i], self.win.signal[self.block_size - 1 - i])

        self.input_signal = [math.sin(2.0 * math.pi * 100.0 * i / 48000.0) for i in range(0, self.block_size)]
        self.output_signal = [0] * self.block_size
        self.win.process(self.input_signal, self.output_signal)
        
        self.assertAlmostEqual(self.output_signal[0], self.input_signal[0] * 0.006879)
        self.assertAlmostEqual(self.output_signal[self.block_size - 1], self.input_signal[self.block_size - 1] * 0.006879)


if __name__ == '__main__':
    unittest.main()

