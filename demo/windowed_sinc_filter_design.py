import yodel.filter
import yodel.analysis
import yodel.complex
import yodel.conversion
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider


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


class WindowedSincFilterDesigner:

    def __init__(self):
        self.samplerate = 48000
        self.framesize = 512
        self.cutoff = self.samplerate / 4.0
        self.bandwidth = 1000
        self.nfft = 0
        self.filter_type = 'Lowpass'
        self.flt = yodel.filter.WindowedSinc(self.samplerate, self.framesize)
        self.update_filter()
        self.create_plot()
        self.create_controls()

    def create_plot(self):
        self._fig, self._ax = plt.subplots()
        self._ax.set_title('Windowed Sinc Filter Design')
        self._ax.grid()
        plt.subplots_adjust(bottom=0.3)

        self._l_bot, = self._ax.plot(self.fr_xscale, [0] * self.nfft, 'k')
        self._l_top, = self._ax.plot(self.fr_xscale, [-100] * self.nfft, 'k')
        self._l_fr, = self._ax.plot(self.fr_xscale, self.fr_amp, 'b')

        self.rescale_plot()

    def create_controls(self):
        self._rax = plt.axes([0.30, 0.03, 0.15, 0.20])
        self._radio = RadioButtons(self._rax, ('Lowpass', 'Highpass', 'Bandpass', 'Bandreject'))
        self._radio.on_clicked(self.set_filter_type)

        self._sfax = plt.axes([0.6, 0.19, 0.2, 0.03])
        self._dlyslider = Slider(self._sfax, 'Cut-off', 1.0, self.samplerate / 2.0, valinit=self.cutoff)
        self._dlyslider.on_changed(self.set_filter_cutoff)

        self._sfax = plt.axes([0.6, 0.10, 0.2, 0.03])
        self._gainslider = Slider(self._sfax, 'Bandwidth', 10, 5000, valinit=self.bandwidth)
        self._gainslider.on_changed(self.set_filter_bandwidth)

    def update_filter(self):
        if self.filter_type == 'Lowpass':
            self.flt.low_pass(self.cutoff, self.bandwidth)
        elif self.filter_type == 'Highpass':
            self.flt.high_pass(self.cutoff, self.bandwidth)
        elif self.filter_type == 'Bandpass':
            self.flt.band_pass(self.cutoff, self.bandwidth)
        elif self.filter_type == 'Bandreject':
            self.flt.band_reject(self.cutoff, self.bandwidth)

        frre, frim = frequency_response(self.flt.conv.ir)
        self.nfft = int((len(frre)/2.0)+1.0)
        self.fr_amp = amplitude_response(frre[0:self.nfft], frim[0:self.nfft])
        self.fr_xscale = [int((i * self.samplerate / 2.0) / self.nfft) for i in range(0, self.nfft)]

    def set_filter_cutoff(self, cutoff):
        self.cutoff = cutoff
        self.update_filter()
        self.update_plot()

    def set_filter_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.update_filter()
        self.update_plot()

    def set_filter_type(self, filter_type):
        self.filter_type = filter_type
        self.update_filter()
        self.update_plot()

    def update_plot(self):
        self._l_fr.set_xdata(self.fr_xscale)
        self._l_fr.set_ydata(self.fr_amp)
        self.rescale_plot()

    def rescale_plot(self):
        self._ax.set_ylim(-110, 5)
        plt.draw()

wsfd = WindowedSincFilterDesigner()

plt.show()
