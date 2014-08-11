import sys
import math
import random
import yodel.analysis as da
import yodel.conversion as dcv
import yodel.complex as dcx
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider


def amplitude_response(spec_real, spec_imag, db=True):
    size = len(spec_real)
    amp = [0] * size
    for i in range(0, size):
        amp[i] = dcx.modulus(spec_real[i], spec_imag[i]) / (size/2)
        if db:
            amp[i] = dcv.lin2db(amp[i])
    return amp

def generate_sine(fs, f0, amp, size):
    twopi = 2.0 * math.pi
    inc = twopi * f0 / fs
    phase = 0
    y = [0] * size

    for i in range(0, size):
        y[i] = amp * math.sin(phase)
        phase += inc
        if phase > twopi:
            phase -= twopi

    return y

def generate_square(fs, f0, amp, size):
    twopi = 2.0 * math.pi
    inc = twopi * f0 / fs
    phase = 0
    y = [0] * size

    for i in range(0, size):
        if phase < math.pi:
            y[i] = amp
        else:
            y[i] = -amp
        phase += inc
        if phase > twopi:
            phase -= twopi

    return y

def generate_sawtooth(fs, f0, amp, size):
    twopi = 2.0 * math.pi
    inc = twopi * f0 / fs
    phase = 0
    y = [0] * size

    for i in range(0, size):
        y[i] = amp - (amp / math.pi * phase)
        phase += inc
        if phase > twopi:
            phase -= twopi

    return y

def generate_triangle(fs, f0, amp, size):
    twopi = 2.0 * math.pi
    inc = twopi * f0 / fs
    phase = 0
    y = [0] * size

    for i in range(0, size):
        if phase < math.pi:
            y[i] = -amp + (2.0 * amp / math.pi) * phase
        else:
            y[i] = 3.0 * amp - (2.0 * amp / math.pi) * phase
        phase += inc
        if phase > twopi:
            phase -= twopi

    return y

def generate_noise(amp, size):
    return [ (amp * ((random.random() * 2.0) - 1.0)) for i in range(0, size) ]

def generate_constant(amp, size):
    return [amp] * size

class FourierAnalysisDemo:
    def __init__(self):
        self.samplerate = 48000
        self.frequency = 440
        self.amplitude = dcv.db2lin(0)
        self.signaltype = 'Sine'
        self.fft_size = 512
        self.window = da.AnalysisWindow(self.fft_size)
        self.fft = da.FFT(self.fft_size)

        self._generate_signal()
        self._analyze_signal()
        self._create_plots()
        self._create_controls()

        plt.show()

    def set_signal_type(self, signaltype):
        self.signaltype = signaltype
        self._generate_signal()
        self._analyze_signal()
        self._update_plots()

    def set_window_type(self, windowtype):
        if windowtype == 'Flat':
            self.window = da.AnalysisWindow(self.fft_size)
        elif windowtype == 'Hanning':
            self.window.hanning(self.fft_size)
        elif windowtype == 'Hamming':
            self.window.hamming(self.fft_size)
        elif windowtype == 'Blackman':
            self.window.blackman(self.fft_size)
        self._generate_signal()
        self._analyze_signal()
        self._update_plots()

    def set_signal_frequency(self, frequency):
        self.frequency = frequency
        self._generate_signal()
        self._analyze_signal()
        self._update_plots()

    def set_signal_amplitude(self, amplitude):
        self.amplitude = dcv.db2lin(amplitude)
        self._generate_signal()
        self._analyze_signal()
        self._update_plots()

    def _generate_signal(self):
        if self.signaltype == 'Sine':
            self.signal = generate_sine(self.samplerate,
                                        self.frequency,
                                        self.amplitude,
                                        self.fft_size)
        elif self.signaltype == 'Square':
            self.signal = generate_square(self.samplerate,
                                          self.frequency,
                                          self.amplitude,
                                          self.fft_size)
        elif self.signaltype == 'Sawtooth':
            self.signal = generate_sawtooth(self.samplerate,
                                            self.frequency,
                                            self.amplitude,
                                            self.fft_size)
        elif self.signaltype == 'Triangle':
            self.signal = generate_triangle(self.samplerate,
                                            self.frequency,
                                            self.amplitude,
                                            self.fft_size)
        elif self.signaltype == 'Noise':
            self.signal = generate_noise(self.amplitude,
                                         self.fft_size)
        elif self.signaltype == 'Constant':
            self.signal = generate_constant(self.amplitude,
                                            self.fft_size)
        self.windowed = [0] * self.fft_size
        self.window.process(self.signal, self.windowed)

    def _analyze_signal(self):
        self.specreal = [0] * self.fft_size
        self.specimag = [0] * self.fft_size
        self.fft.forward(self.windowed, self.specreal, self.specimag)
        self.spectrum = amplitude_response(self.specreal, self.specimag, True)

    def _create_plots(self):
        self._fig, (self._signal_ax, self._spec_ax) = plt.subplots(nrows=2,
                                                                   ncols=1)
        self._signal_ax.set_title('Signal')
        self._signal_ax.grid()
        self._spec_ax.set_title('Spectrum')
        self._spec_ax.grid()
        plt.subplots_adjust(bottom=0.3)
        self._signal_line, = self._signal_ax.plot(self.windowed)
        self._spec_line, = self._spec_ax.plot([(((i+1)/self.fft_size) * self.samplerate) for i in range(0, int(self.fft_size/2))],
                                              self.spectrum[0:int(self.fft_size/2)])
        self._signal_ax.set_ylim(-1, 1)
        self._spec_ax.set_ylim(-100, 10)
        
    def _create_controls(self):
        self._freq_ax = plt.axes([0.2, 0.19, 0.2, 0.03])
        self._freq_slider = Slider(self._freq_ax,
                                   'Frequency',
                                   0,
                                   self.samplerate / 2.0,
                                   valinit = self.frequency)
        self._freq_slider.on_changed(self.set_signal_frequency)

        self._ampl_ax = plt.axes([0.2, 0.1, 0.2, 0.03])
        self._ampl_slider = Slider(self._ampl_ax,
                                   'Amplitude',
                                   -100,
                                   0,
                                   valinit = dcv.lin2db(self.amplitude))
        self._ampl_slider.on_changed(self.set_signal_amplitude)

        self._signaltype_ax = plt.axes([0.5, 0.05, 0.15, 0.20])
        self._signaltype_radio = RadioButtons(self._signaltype_ax,
                                              ('Sine', 'Square', 'Sawtooth',
                                               'Triangle', 'Noise', 'Constant'))
        self._signaltype_radio.on_clicked(self.set_signal_type)

        self._windowtype_ax = plt.axes([0.7, 0.05, 0.15, 0.20])
        self._windowtype_radio = RadioButtons(self._windowtype_ax,
                                              ('Flat', 'Hanning', 'Hamming', 'Blackman'))
        self._windowtype_radio.on_clicked(self.set_window_type)

    def _update_plots(self):
        self._signal_line.set_ydata(self.windowed)
        self._spec_line.set_ydata(self.spectrum[0:int(self.fft_size/2)])
        plt.draw()


def main():
    demo = FourierAnalysisDemo()

if __name__ == '__main__':
    sys.exit(main())
