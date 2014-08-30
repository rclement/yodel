import yodel.filter
import yodel.analysis
import yodel.complex
import yodel.conversion
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


class ParametricEQSelector:

    def __init__(self):
        self._fs = 48000
        self._nbands = 7
        self._params = []
        for i in range(0, self._nbands):
            self._params.append({'center': 0, 'resonance': 1.0/math.sqrt(2.0), 'dbgain': 0})
        self._selected_band = 0
        self._blocksize = 512
        self._nfft = int(self._blocksize / 2)
        self._impulse_response = [0] * self._blocksize
        self._freq_response_real = [0] * self._blocksize
        self._freq_response_imag = [0] * self._blocksize
        self._response = [0] * self._blocksize
        self._plot_db = True
        self._eq = yodel.filter.ParametricEQ(self._fs, self._nbands)

        self._create_plot()
        self._create_plot_controls()
        self.select_band('Band ' + str(self._selected_band+1))

    def _create_plot(self):
        self._fig, self._ax = plt.subplots()
        self._ax.set_title('Parametric Equalizer Design')
        self._ax.grid()
        plt.subplots_adjust(bottom=0.3)

        self._update_filter_response()
        self._x_axis = [i*(self._fs/2/self._nfft) for i in range(0, self._nfft)]
        self._y_axis = self._response[0:self._nfft]

        self._l_center, = self._ax.plot(self._x_axis, [0] * self._nfft, 'k')
        self._l_fr, = self._ax.plot(self._x_axis, self._y_axis, 'b')

        self._rescale_plot()

    def _create_plot_controls(self):
        self._dbrax = plt.axes([0.12, 0.05, 0.13, 0.10])
        self._dbradio = RadioButtons(self._dbrax, ('Amplitude', 'Phase'))
        self._dbradio.on_clicked(self.set_plot_style)

        self._rax = plt.axes([0.27, 0.03, 0.15, 0.20])
        bands_list = []
        for i in range(1, self._nbands+1):
            bands_list.append('Band ' + str(i))
        self._radio = RadioButtons(self._rax, tuple(bands_list))
        self._radio.on_clicked(self.select_band)

        self._sfax = plt.axes([0.6, 0.19, 0.2, 0.03])
        self._sqax = plt.axes([0.6, 0.12, 0.2, 0.03])
        self._sdbax = plt.axes([0.6, 0.05, 0.2, 0.03])
        self._fcslider = Slider(self._sfax, 'Cut-off frequency', 0, self._fs/2, valinit = self._params[self._selected_band]['center'])
        self._qslider = Slider(self._sqax, 'Q factor', 0.01, 10.0, valinit = self._params[self._selected_band]['resonance'])
        self._dbslider = Slider(self._sdbax, 'dB gain', -20.0, 20.0, valinit = self._params[self._selected_band]['dbgain'])

        self._fcslider.on_changed(self.set_center_frequency)
        self._qslider.on_changed(self.set_resonance)
        self._dbslider.on_changed(self.set_dbgain)

    def _rescale_plot(self):
        if self._plot_db:
            self._ax.set_ylim(-30, 30)
        else:
            self._ax.set_ylim(- 200, 200)
        plt.draw()

    def _plot_frequency_response(self, redraw=True):
        self._update_filter_response()
        self._y_axis = self._response[0:self._nfft]
        self._l_fr.set_ydata(self._y_axis)
        if redraw:
            plt.draw()

    def _plot_range_limits(self, redraw=True):
        self._l_center.set_ydata([0] * self._nfft)
        if redraw:
            plt.draw()

    def set_plot_style(self, style):
        if style == 'Phase':
            self._plot_db = False
        elif style == 'Amplitude':
            self._plot_db = True
        self._plot_range_limits(False)
        self._plot_frequency_response(False)
        self._rescale_plot()

    def select_band(self, band):
        idx = band.split(' ')
        self._selected_band = int(idx[1]) - 1
        self._fcslider.set_val(self._params[self._selected_band]['center'])
        self._qslider.set_val(self._params[self._selected_band]['resonance'])
        self._dbslider.set_val(self._params[self._selected_band]['dbgain'])

    def set_center_frequency(self, val):
        self._params[self._selected_band]['center'] = val
        self._set_band(self._selected_band)
        self._plot_frequency_response()
    
    def set_resonance(self, val):
        self._params[self._selected_band]['resonance'] = val
        self._set_band(self._selected_band)
        self._plot_frequency_response()

    def set_dbgain(self, val):
        self._params[self._selected_band]['dbgain'] = val
        self._set_band(self._selected_band)
        self._plot_frequency_response()

    def _set_band(self, band):
        center = self._params[band]['center']
        resonance = self._params[band]['resonance']
        dbgain = self._params[band]['dbgain']
        self._eq.set_band(band, center, resonance, dbgain)

    def _update_filter_response(self):
        self._impulse_response = impulse_response(self._eq, self._blocksize)
        self._freq_response_real, self._freq_response_imag = frequency_response(self._impulse_response)
        if self._plot_db:
            self._response = amplitude_response(self._freq_response_real, self._freq_response_imag)
        else:
            self._response = phase_response(self._freq_response_real, self._freq_response_imag)

peqs = ParametricEQSelector()

plt.show()
