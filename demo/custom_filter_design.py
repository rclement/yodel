import yodel.analysis
import yodel.filter
import yodel.complex
import yodel.conversion
import matplotlib.pyplot as plt


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


class CustomFilterDesigner:

    def __init__(self):
        self.samplerate = 48000
        self.framesize = 256
        self.frsize = int((self.framesize/2)+1)
        self.custom_fr = [1] * self.frsize
        self.hzscale = [(i*self.samplerate) / (2.0*self.frsize) for i in range(0, self.frsize)]
        self.flt = yodel.filter.Custom(self.samplerate, self.framesize)
        self.pressed = None 

        self.update_filter()
        self.create_plot()

    def update_filter(self):
        self.flt.design(self.custom_fr, False)
        fr_re, fr_im = frequency_response(self.flt.ir)
        self.fft_fr = amplitude_response(fr_re, fr_im, False)

    def create_plot(self):
        self.fig = plt.figure()
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onpress)
        self.cid = self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', self.onmotion)

        self.ax_custom_fr = self.fig.add_subplot(111)
        self.ax_custom_fr.set_title('Custom Filter Design')
        self.plot_custom_fr, = self.ax_custom_fr.plot(self.hzscale, self.custom_fr, 'r', label='Desired Frequency Response')
        self.plot_fft_fr, = self.ax_custom_fr.plot(self.hzscale, self.fft_fr[0:self.frsize], 'b', label='Actual Frequency Response')
        self.ax_custom_fr.legend()
        self.ax_custom_fr.grid()

        self.rescale_plot()

    def rescale_plot(self):
        self.ax_custom_fr.set_ylim(-1, 5)
        plt.draw()

    def onpress(self, event):
        if event.inaxes != self.ax_custom_fr:
            return

        self.pressed = (event.xdata, event.ydata)

        xpos = int(event.xdata * 2.0 * self.frsize / self.samplerate)
        ypos = max(event.ydata, 0)

        if xpos >= 0 and xpos < self.frsize:
            self.custom_fr[xpos] = ypos
            self.update_filter()
            self.plot_custom_fr.set_ydata(self.custom_fr)
            self.plot_fft_fr.set_ydata(self.fft_fr[0:self.frsize])
            self.rescale_plot()

    def onrelease(self, event):
        self.pressed = None

    def onmotion(self, event):
        if self.pressed != None and event.xdata != None and event.ydata != None:
            xpos = int(event.xdata * 2.0 * self.frsize / self.samplerate)
            ypos = max(event.ydata, 0)

            if xpos >= 0 and xpos < self.frsize:
                self.custom_fr[xpos] = ypos
                self.update_filter()
                self.plot_custom_fr.set_ydata(self.custom_fr)
                self.plot_fft_fr.set_ydata(self.fft_fr[0:self.frsize])
                self.rescale_plot()


cfd = CustomFilterDesigner()

plt.show()

