import yodel.filter
import yodel.analysis
import yodel.complex as dcx
import yodel.conversion as dcv
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider


def impulse_response(svf, size):
    impulse = [0] * size
    impulse[0] = 1
    hp = [0] * size
    lp = [0] * size
    bp = [0] * size
    br = [0] * size
    svf.process(impulse, hp, bp, lp, br)
    return (hp, bp, lp, br)


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


class StateVariableSelector:
    def __init__(self):
        self.fs = 48000
        self.fc = 200
        self.q  = 1.0 / math.sqrt(2.0)
        self.block_size = 512
        self.plot_ampl = True
        self.nfft = int(self.block_size / 2)
        self.response_hp = [0] * self.block_size
        self.response_lp = [0] * self.block_size
        self.response_bp = [0] * self.block_size
        self.response_br = [0] * self.block_size
        self.flt = yodel.filter.StateVariable()
        self.update_filter()

        self._create_plot()
        self._create_plot_controls()

    def _create_plot(self):
        self._fig, self._ax = plt.subplots()
        self._ax.set_title('State Variable Filter Design')
        self._ax.grid()
        plt.subplots_adjust(bottom=0.3)

        self.update_filter_response()

        self._x_axis = [i*(self.fs/2/self.nfft) for i in range(0, self.nfft)]
        self._y_axis_hp = self.response_hp[0:self.nfft]
        self._y_axis_lp = self.response_lp[0:self.nfft]
        self._y_axis_bp = self.response_bp[0:self.nfft]
        self._y_axis_br = self.response_br[0:self.nfft]

        if self.plot_ampl:
            self._l_bot, = self._ax.plot(self._x_axis, [-100] * self.nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [0] * self.nfft, 'k')
        else:
            self._l_bot, = self._ax.plot(self._x_axis, [- 180] * self.nfft, 'k')
            self._l_top, = self._ax.plot(self._x_axis, [180] * self.nfft, 'k')

        if self.plot_ampl:
            self._l_fc, = self._ax.plot([self.fc] * 100, [i for i in range(-100, 0)], 'k')
        else:
            self._l_fc, = self._ax.plot([self.fc] * int(2.0 * self.nfft), [(180*i/self.nfft) for i in range(-self.nfft, self.nfft)], 'k')

        self._l_fr_hp, = self._ax.plot(self._x_axis, self._y_axis_hp, 'b', label='High-Pass')
        self._l_fr_lp, = self._ax.plot(self._x_axis, self._y_axis_lp, 'r', label='Low-Pass')
        self._l_fr_bp, = self._ax.plot(self._x_axis, self._y_axis_bp, 'g', label='Band-Pass')
        self._l_fr_br, = self._ax.plot(self._x_axis, self._y_axis_br, 'y', label='Band-Reject')
        plt.legend()

        self._rescale_plot()

    def _create_plot_controls(self):
        self._dbrax = plt.axes([0.12, 0.05, 0.13, 0.10])
        self._dbradio = RadioButtons(self._dbrax, ('Amplitude', 'Phase'))
        self._dbradio.on_clicked(self.set_plot_style)

        self._sfax = plt.axes([0.6, 0.19, 0.2, 0.03])
        self._sqax = plt.axes([0.6, 0.12, 0.2, 0.03])

        self._fcslider = Slider(self._sfax, 'Cut-off frequency', 0, self.fs/5, valinit = self.fc)
        self._qslider = Slider(self._sqax, 'Q factor', 0.5, 1.5, valinit = self.q)

        self._fcslider.on_changed(self.set_biquad_frequency_cutoff)
        self._qslider.on_changed(self.set_biquad_q_factor)

    def update_filter(self):
        self.flt.reset()
        self.flt.set(self.fs, self.fc, self.q)

    def set_biquad_frequency_cutoff(self, fc):
        self.fc = fc
        self.update_filter()
        self._plot_frequency_response()

    def set_biquad_q_factor(self, q):
        self.q = q
        self.update_filter()
        self._plot_frequency_response()

    def update_filter_response(self):
        responses = impulse_response(self.flt, self.block_size)

        if self.plot_ampl:
            freq_response_real, freq_response_imag = frequency_response(responses[0])
            self.response_hp = amplitude_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[1])
            self.response_bp = amplitude_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[2])
            self.response_lp = amplitude_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[3])
            self.response_br = amplitude_response(freq_response_real, freq_response_imag)
        else:
            freq_response_real, freq_response_imag = frequency_response(responses[0])
            self.response_hp = phase_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[1])
            self.response_bp = phase_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[2])
            self.response_lp = phase_response(freq_response_real, freq_response_imag)

            freq_response_real, freq_response_imag = frequency_response(responses[3])
            self.response_br = phase_response(freq_response_real, freq_response_imag)

    def set_plot_style(self, style):
        if style == 'Phase':
            self.plot_ampl = False
        elif style == 'Amplitude':
            self.plot_ampl = True

        self._plot_range_limits(False)
        self._plot_frequency_response(False)
        self._rescale_plot()

    def _plot_frequency_response(self, redraw = True):
        self.update_filter_response()

        self._y_axis_hp = self.response_hp[0:self.nfft]
        self._y_axis_lp = self.response_lp[0:self.nfft]
        self._y_axis_bp = self.response_bp[0:self.nfft]
        self._y_axis_br = self.response_br[0:self.nfft]

        if self.plot_ampl:
            self._l_fc.set_xdata([self.fc] * 100)
            self._l_fc.set_ydata([i for i in range(-100, 0)])
        else:
            self._l_fc.set_xdata([self.fc] * int(2.0 * self.nfft))
            self._l_fc.set_ydata([(180*i/self.nfft) for i in range(-self.nfft, self.nfft)])

        self._l_fr_hp.set_ydata(self._y_axis_hp)
        self._l_fr_bp.set_ydata(self._y_axis_bp)
        self._l_fr_lp.set_ydata(self._y_axis_lp)
        self._l_fr_br.set_ydata(self._y_axis_br)

        if redraw:
            plt.draw()

    def _plot_range_limits(self, redraw = True):
        if self.plot_ampl:
            self._l_bot.set_ydata([-100] * self.nfft)
            self._l_top.set_ydata([0] * self.nfft)
        else:
            self._l_bot.set_ydata([- 180] * self.nfft)
            self._l_top.set_ydata([180] * self.nfft)
        if redraw:
            plt.draw()

    def _rescale_plot(self):
        if self.plot_ampl:
            self._ax.set_ylim(-110, 20)
        else:
            self._ax.set_ylim(- 200, 200)
        plt.draw()


bqs = StateVariableSelector()

plt.show()

