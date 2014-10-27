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


class TestWindowedSincFilter(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000
        self.framesize = 512
        self.flt = yodel.filter.WindowedSinc(self.samplerate, self.framesize)

    def test_default(self):
        frre, frim = frequency_response(self.flt.conv.ir)
        framp = amplitude_response(frre, frim)

        for i in range(0, len(framp)):
            self.assertAlmostEqual(1.0, framp[i])

    def test_lowpass_1(self):
        fc = 0.015 * self.samplerate
        bw = 384 # M = 4 / (384 / 48000) = 500

        self.flt.low_pass(fc, bw)

        self.assertAlmostEqual(0.03, self.flt.kernel[int(self.flt.kernelsize/2.0)], delta=1e-3)

    def test_lowpass_2(self):
        fc = 0.04 * self.samplerate
        bw = 384 # M = 4 / (384 / 48000) = 500

        self.flt.low_pass(fc, bw)

        self.assertAlmostEqual(0.08, self.flt.kernel[int(self.flt.kernelsize/2.0)], delta=1e-3)

    def test_lowpass_3(self):
        fc = 0.04 * self.samplerate
        bw = 1280 # M = 4 / (1280 / 48000) = 150

        self.flt.low_pass(fc, bw)

        self.assertAlmostEqual(0.08, self.flt.kernel[int(self.flt.kernelsize/2.0)], delta=1e-3)

    def test_highpass_1(self):
        fc = 0.25 * self.samplerate
        bw = 384 # M = 4 / (384 / 48000) = 500

        self.flt.low_pass(fc, bw)
        lpre, lpim = frequency_response(self.flt.conv.ir)
        lpamp = amplitude_response(lpre, lpim)

        self.flt.high_pass(fc, bw)
        hpre, hpim = frequency_response(self.flt.conv.ir)
        hpamp = amplitude_response(hpre, hpim)

        for i in range(0, len(lpamp)):
            self.assertAlmostEqual(1.0 - lpamp[i], hpamp[i], delta=1e-3)

    def test_bandpass_1(self):
        fc = 0.25 * self.samplerate
        bw = 400

        self.flt.band_pass(fc, bw)
        bpre, bpim = frequency_response(self.flt.conv.ir)
        bpamp = amplitude_response(bpre, bpim)

        idxcenter = int(fc * len(bpamp) / self.samplerate)
        idxbottom = (fc-(bw/2.0)) * len(bpamp) / self.samplerate
        idxbottomalpha = 1.0 - (idxbottom - int(idxbottom))
        idxbottombeta = 1.0 - idxbottomalpha
        idxtop = (fc+(bw/2.0)) * len(bpamp) / self.samplerate
        idxtopalpha = 1.0 - (idxtop - int(idxtop))
        idxtopbeta = 1.0 - idxtopalpha

        self.assertAlmostEqual(1.0, bpamp[idxcenter], delta=1e-3)
        self.assertAlmostEqual(0.5, idxbottomalpha * bpamp[int(idxbottom)] + idxbottombeta * bpamp[int(idxbottom+1)], delta=1e-3)
        self.assertAlmostEqual(0.5, idxtopalpha * bpamp[int(idxtop)] + idxtopbeta * bpamp[int(idxtop+1)], delta=1e-3)

    def test_bandreject_1(self):
        fc = 0.25 * self.samplerate
        bw = 400

        self.flt.band_reject(fc, bw)
        bpre, bpim = frequency_response(self.flt.conv.ir)
        bpamp = amplitude_response(bpre, bpim)

        idxcenter = int(fc * len(bpamp) / self.samplerate)
        idxbottom = (fc-(bw/2.0)) * len(bpamp) / self.samplerate
        idxbottomalpha = 1.0 - (idxbottom - int(idxbottom))
        idxbottombeta = 1.0 - idxbottomalpha
        idxtop = (fc+(bw/2.0)) * len(bpamp) / self.samplerate
        idxtopalpha = 1.0 - (idxtop - int(idxtop))
        idxtopbeta = 1.0 - idxtopalpha

        self.assertAlmostEqual(0.0, bpamp[idxcenter], delta=1e-3)
        self.assertAlmostEqual(0.5, idxbottomalpha * bpamp[int(idxbottom)] + idxbottombeta * bpamp[int(idxbottom+1)], delta=1e-3)
        self.assertAlmostEqual(0.5, idxtopalpha * bpamp[int(idxtop)] + idxtopbeta * bpamp[int(idxtop+1)], delta=1e-3)


if __name__ == '__main__':
    unittest.main()
