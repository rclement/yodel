import yodel.filter
import yodel.analysis
import yodel.complex as dcx
import yodel.conversion as dcv
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider


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


def phase_response(spec_real, spec_imag, degrees=True):
    size = len(spec_real)
    pha = [0] * size
    for i in range(0, size):
        pha[i] = yodel.complex.phase(spec_real[i], spec_imag[i])
        if degrees:
            pha[i] = (pha[i] * 180.0 / math.pi)
    return pha


class BiquadSelector:
    def __init__(self):
        self._bq_fs = 48000
        self._bq_fc = self._bq_fs/4
        self._bq_q  = 1.0 / math.sqrt(2.0)
        self._bq_dbgain = 0
        self._bq_size = 512
        self._bq_plot_db = True
        self._nfft = int(self._bq_size / 2)
        self._impulse_response = [0] * self._bq_size
        self._freq_response_real = [0] * self._bq_size
        self._freq_response_imag = [0] * self._bq_size
        self._response = [0] * self._bq_size
        self._bq_filter = yodel.filter.Biquad()
        self._biquad_type = 'Low Pass'
        self.update_biquad()

        self._create_plot()
        self._create_plot_controls()

    def _create_plot(self):
        self._fig, self._ax = plt.subplots()
        self._ax.set_title('Biquad Filter Design')
        self._ax.grid()
        plt.subplots_adjust(bottom=0.3)

        self.update_biquad_response()
        self._x_axis = [i*(self._bq_fs/2/self._nfft) for i in range(0, self._nfft)]
        self._y_axis = self._response[0:self._nfft]

        if self._bq_plot_db:
            self._l_bot, = self._ax.plot(self._x_axis, [-100] * self._nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [0] * self._nfft, 'k')
        else:
            self._l_bot, = self._ax.plot(self._x_axis, [- 180] * self._nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [180] * self._nfft, 'k')

        if self._bq_plot_db:
            self._l_fc, = self._ax.plot([self._bq_fc] * 100, [i for i in range(-100, 0)], 'k')
        else:
            self._l_fc, = self._ax.plot([self._bq_fc] * int(2.0 * self._nfft), [(180*i/self._nfft) for i in range(-self._nfft, self._nfft)], 'k')

        self._l_fr, = self._ax.plot(self._x_axis, self._y_axis, 'b')

        self._rescale_plot()

    def _create_plot_controls(self):
        self._dbrax = plt.axes([0.12, 0.05, 0.13, 0.10])
        self._dbradio = RadioButtons(self._dbrax, ('Amplitude', 'Phase'))
        self._dbradio.on_clicked(self.set_plot_style)

        self._rax = plt.axes([0.27, 0.03, 0.15, 0.20])
        self._radio = RadioButtons(self._rax, ('Low Pass', 'High Pass', 'Band Pass', 'All Pass', 'Notch', 'Peak', 'Low Shelf', 'High Shelf'))
        self._radio.on_clicked(self.set_biquad_type)

        self._sfax = plt.axes([0.6, 0.19, 0.2, 0.03])
        self._sqax = plt.axes([0.6, 0.12, 0.2, 0.03])
        self._sdbax = plt.axes([0.6, 0.05, 0.2, 0.03])
        self._fcslider = Slider(self._sfax, 'Cut-off frequency', 0, self._bq_fs/2, valinit = self._bq_fc)
        self._qslider = Slider(self._sqax, 'Q factor', 0.01, 10.0, valinit = self._bq_q)
        self._dbslider = Slider(self._sdbax, 'dB gain', -20.0, 20.0, valinit = self._bq_dbgain)

        self._fcslider.on_changed(self.set_biquad_frequency_cutoff)
        self._qslider.on_changed(self.set_biquad_q_factor)
        self._dbslider.on_changed(self.set_biquad_dbgain)

    def update_biquad(self):
        if self._biquad_type == 'Low Pass':
            self._bq_filter.low_pass(self._bq_fs, self._bq_fc, self._bq_q)
        elif self._biquad_type == 'High Pass':
            self._bq_filter.high_pass(self._bq_fs, self._bq_fc, self._bq_q)
        elif self._biquad_type == 'Band Pass':
            self._bq_filter.band_pass(self._bq_fs, self._bq_fc, self._bq_q)
        elif self._biquad_type == 'All Pass':
            self._bq_filter.all_pass(self._bq_fs, self._bq_fc, self._bq_q)
        elif self._biquad_type == 'Notch':
            self._bq_filter.notch(self._bq_fs, self._bq_fc, self._bq_q)
        elif self._biquad_type == 'Peak':
            self._bq_filter.peak(self._bq_fs, self._bq_fc, self._bq_q, self._bq_dbgain)
        elif self._biquad_type == 'Low Shelf':
            self._bq_filter.low_shelf(self._bq_fs, self._bq_fc, self._bq_q, self._bq_dbgain)
        elif self._biquad_type == 'High Shelf':
            self._bq_filter.high_shelf(self._bq_fs, self._bq_fc, self._bq_q, self._bq_dbgain)

    def set_biquad_type(self, biquad_type):
        self._biquad_type = biquad_type
        self.update_biquad()
        self._plot_frequency_response(False)
        self._rescale_plot()

    def set_biquad_frequency_cutoff(self, fc):
        self._bq_fc = fc
        self.update_biquad()
        self._plot_frequency_response()

    def set_biquad_q_factor(self, q):
        self._bq_q = q
        self.update_biquad()
        self._plot_frequency_response()

    def set_biquad_dbgain(self, dbgain):
        self._bq_dbgain = dbgain
        self.update_biquad()
        self._plot_frequency_response()

    def update_biquad_response(self):
        self._impulse_response = impulse_response(self._bq_filter, self._bq_size)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        if self._bq_plot_db:
            self._response = amplitude_response(self._freq_response_real, self._freq_response_imag)
        else:
            self._response = phase_response(self._freq_response_real, self._freq_response_imag)

    def set_plot_style(self, style):
        if style == 'Phase':
            self._bq_plot_db = False
        elif style == 'Amplitude':
            self._bq_plot_db = True
        self._plot_range_limits(False)
        self._plot_frequency_response(False)
        self._rescale_plot()

    def _plot_frequency_response(self, redraw = True):
        self.update_biquad_response()
        self._y_axis = self._response[0:self._nfft]
        if self._bq_plot_db:
            self._l_fc.set_xdata([self._bq_fc] * 100)
            self._l_fc.set_ydata([i for i in range(-100, 0)])
        else:
            self._l_fc.set_xdata([self._bq_fc] * int(2.0 * self._nfft))
            self._l_fc.set_ydata([(180*i/self._nfft) for i in range(-self._nfft, self._nfft)])
        self._l_fr.set_ydata(self._y_axis)
        if redraw:
            plt.draw()

    def _plot_range_limits(self, redraw = True):
        if self._bq_plot_db:
            self._l_bot.set_ydata([-100] * self._nfft)
            self._l_top.set_ydata([0] * self._nfft)
        else:
            self._l_bot.set_ydata([- 180] * self._nfft)
            self._l_top.set_ydata([180] * self._nfft)
        if redraw:
            plt.draw()

    def _rescale_plot(self):
        if self._bq_plot_db:
            self._ax.set_ylim(-110, 20)
        else:
            self._ax.set_ylim(- 200, 200)
        plt.draw()


bqs = BiquadSelector()

plt.show()

