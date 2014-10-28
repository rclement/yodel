import yodel.filter
import yodel.analysis
import yodel.complex
import yodel.conversion
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider


def impulse_response(flt, size):
    impulse = [0] * size
    impulse[0] = 1
    response = [0] * size
    flt.process(impulse, response)
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


def phase_response(spec_real, spec_imag, degrees=True):
    size = len(spec_real)
    pha = [0] * size
    for i in range(0, size):
        pha[i] = yodel.complex.phase(spec_real[i], spec_imag[i])
        if degrees:
            pha[i] = (pha[i] * 180.0 / math.pi)
    return pha


class CombFilterSelector:
    def __init__(self):
        self._fs = 48000
        self._delay = 0.25
        self._gain  = 0.5
        self._size = 512
        self._plot_db = True
        self._nfft = int(self._size / 2)
        self._impulse_response = [0] * self._size
        self._freq_response_real = [0] * self._size
        self._freq_response_imag = [0] * self._size
        self._response = [0] * self._size
        self._comb_type = 'feedback'
        self._comb_filter = yodel.filter.Comb(self._fs, self._delay, self._gain)
        self.update_filter()

        self._create_plot()
        self._create_plot_controls()

    def _create_plot(self):
        self._fig, self._ax = plt.subplots()
        self._ax.set_title('Comb Filter Design')
        self._ax.grid()
        plt.subplots_adjust(bottom=0.3)

        self.update_filter_response()
        self._x_axis = [i*(self._fs/2/self._nfft) for i in range(0, self._nfft)]
        self._y_axis = self._response[0:self._nfft]

        if self._plot_db:
            self._l_bot, = self._ax.plot(self._x_axis, [-100] * self._nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [0] * self._nfft, 'k')
        else:
            self._l_bot, = self._ax.plot(self._x_axis, [-180] * self._nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [180] * self._nfft, 'k')

        self._l_fr, = self._ax.plot(self._x_axis, self._y_axis, 'b')

        self._rescale_plot()

    def _create_plot_controls(self):
        self._dbrax = plt.axes([0.12, 0.05, 0.15, 0.15])
        self._dbradio = RadioButtons(self._dbrax, ('Amplitude', 'Phase'))
        self._dbradio.on_clicked(self.set_plot_style)

        self._rax = plt.axes([0.30, 0.03, 0.15, 0.20])
        self._radio = RadioButtons(self._rax, ('feedback', 'feedforward', 'allpass'))
        self._radio.on_clicked(self.set_comb_type)

        self._sfax = plt.axes([0.6, 0.19, 0.2, 0.03])
        self._dlyslider = Slider(self._sfax, 'delay (ms)', 0, (self._size/2.0) * 1000.0 / self._fs, valinit = self._delay)
        self._dlyslider.on_changed(self.set_comb_delay)

        self._sfax = plt.axes([0.6, 0.10, 0.2, 0.03])
        self._gainslider = Slider(self._sfax, 'gain', -1, 1, valinit = self._gain)
        self._gainslider.on_changed(self.set_comb_gain)

    def update_filter(self):
        if self._comb_type == 'feedback':
            self._comb_filter.feedback(self._delay, self._gain)
        elif self._comb_type == 'feedforward':
            self._comb_filter.feedforward(self._delay, self._gain)
        elif self._comb_type == 'allpass':
            self._comb_filter.allpass(self._delay, self._gain)
        self._comb_filter.reset()

    def set_comb_type(self, comb_type):
        self._comb_type = comb_type
        self.update_filter()
        self._plot_frequency_response(False)
        self._rescale_plot()

    def set_comb_delay(self, delay):
        self._delay = delay
        self.update_filter()
        self._plot_frequency_response()

    def set_comb_gain(self, gain):
        self._gain = gain
        self.update_filter()
        self._plot_frequency_response()

    def update_filter_response(self):
        self._impulse_response = impulse_response(self._comb_filter, self._size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        if self._plot_db:
            self._response = amplitude_response(self._freq_response_real, self._freq_response_imag, True)
        else:
            self._response = phase_response(self._freq_response_real, self._freq_response_imag, True)

    def set_plot_style(self, style):
        if style == 'Amplitude':
            self._plot_db = True
        elif style == 'Phase':
            self._plot_db = False
        self._plot_range_limits(False)
        self._plot_frequency_response(False)
        self._rescale_plot()

    def _plot_frequency_response(self, redraw = True):
        self.update_filter_response()
        self._y_axis = self._response[0:self._nfft]
        self._l_fr.set_ydata(self._y_axis)
        if redraw:
            plt.draw()

    def _plot_range_limits(self, redraw = True):
        if self._plot_db:
            self._l_bot.set_ydata([-100] * self._nfft)
            self._l_top.set_ydata([0] * self._nfft)
        else:
            self._l_bot.set_ydata([-180] * self._nfft)
            self._l_top.set_ydata([180] * self._nfft)
        if redraw:
            plt.draw()

    def _rescale_plot(self):
        if self._plot_db:
            self._ax.set_ylim(-110, 20)
        else:
            self._ax.set_ylim(-200, 200)
        plt.draw()


cfs = CombFilterSelector()

plt.show()

