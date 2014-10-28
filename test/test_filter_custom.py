import unittest
import math
import yodel.filter
import yodel.analysis
import yodel.conversion
import yodel.complex


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


class TestCustomFilter(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000
        self.framesize = 512
        self.flt = yodel.filter.Custom(self.samplerate, self.framesize)

    def test_default(self):
        insignal = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(0, self.framesize)]
        outsignal = [0] * self.framesize

        self.flt.process(insignal, outsignal)

        fr_real, fr_imag = frequency_response(self.flt.ir)
        ampl = amplitude_response(fr_real, fr_imag)

        for i in range(0, len(ampl)):
            self.assertAlmostEqual(1, ampl[i], delta=1e-3)

        for i in range(0, self.flt.latency+1):
            self.assertAlmostEqual(0, outsignal[i])

        for i in range(self.flt.latency+1, self.framesize):
            self.assertAlmostEqual(insignal[i-self.flt.latency-1], outsignal[i], delta=1e-3)

    def test_flat(self):
        insignal = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(0, self.framesize)]
        outsignal = [0] * self.framesize
        flatresp = [1] * int((self.framesize/2)+1)

        self.flt.design(flatresp, db=False)
        self.flt.process(insignal, outsignal)

        fr_real, fr_imag = frequency_response(self.flt.ir)
        ampl = amplitude_response(fr_real, fr_imag)

        for i in range(0, len(ampl)):
            self.assertAlmostEqual(1, ampl[i], delta=1e-3)

        for i in range(0, self.flt.latency+1):
            self.assertAlmostEqual(0, outsignal[i])

        for i in range(self.flt.latency+1, self.framesize):
            self.assertAlmostEqual(insignal[i-self.flt.latency-1], outsignal[i], delta=1e-3)

    def test_flat_db(self):
        insignal = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(0, self.framesize)]
        outsignal = [0] * self.framesize
        flatresp = [0] * int((self.framesize/2)+1)

        self.flt.design(flatresp, db=True)
        self.flt.process(insignal, outsignal)

        fr_real, fr_imag = frequency_response(self.flt.ir)
        ampl = amplitude_response(fr_real, fr_imag)

        for i in range(0, len(ampl)):
            self.assertAlmostEqual(1, ampl[i], delta=1e-3)

        for i in range(0, self.flt.latency+1):
            self.assertAlmostEqual(0, outsignal[i])

        for i in range(self.flt.latency+1, self.framesize):
            self.assertAlmostEqual(insignal[i-self.flt.latency-1], outsignal[i], delta=1e-3)

    def test_total_cancellation(self):
        insignal = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(0, self.framesize)]
        outsignal = [0] * self.framesize
        flatresp = [0] * int((self.framesize/2)+1)

        self.flt.design(flatresp, db=False)
        self.flt.process(insignal, outsignal)

        fr_real, fr_imag = frequency_response(self.flt.ir)
        ampl = amplitude_response(fr_real, fr_imag)

        for i in range(0, len(ampl)):
            self.assertAlmostEqual(0, ampl[i], delta=1e-3)

        for i in range(0, self.framesize):
            self.assertAlmostEqual(0, outsignal[i])


if __name__ == '__main__':
    unittest.main()
