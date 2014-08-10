import math
import array


class DFT:
    """
    The Discrete Fourier Transform allows to convert a time-domain signal
    into a frequency-domain spectrum.

    *Warning:*
        It should not be used in practice for computational reasons,
        and should only be used for testing purposes. Instead, prefer
        using the :py:class:`.FFT`.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, size):
        """
        Initialize the Discrete Fourier Transform.

        :param size: length of the DFT (should only be a power of 2)
        """
        self.size = size
        self._generate_lookup_tables()

    def _generate_lookup_tables(self):
        """
        Generate internal lookup tables for trigonometric functions (sin, cos)
        """
        table_size = self.size * self.size
        self.cos_table = array.array('f', [0] * table_size)
        self.sin_table = array.array('f', [0] * table_size)
        two_pi = 2.0 * math.pi
        for i in range(0, table_size):
            self.cos_table[i] = math.cos(two_pi * i / self.size)
            self.sin_table[i] = math.sin(two_pi * i / self.size)

    def forward(self, real_signal, real_spec, imag_spec):
        """
        Compute the complex spectrum of a given real time-domain signal

        :param real_signal: real time-domain input signal
        :param real_spec: real-part of the output complex spectrum
        :param imag_spec: imaginary-part of the output complex spectrum
        """
        for i in range(0, self.size):
            real_spec[i] = 0
            imag_spec[i] = 0

        for k in range(0, self.size):
            for i in range(0, self.size):
                real_spec[k] += real_signal[i] * self.cos_table[k * i]
                imag_spec[k] -= real_signal[i] * self.sin_table[k * i]

    def inverse(self, real_spec, imag_spec, real_signal):
        """
        Compute the real time-domain signal of a given complex spectrum

        :param real_spec: real-part of the complex spectrum
        :param imag_spec: imaginary-part of the complex spectrum
        :param real_signal: real time-domain output signal
        """
        for i in range(0, self.size):
            real_signal[i] = 0

        for k in range(0, self.size):
            real_spec[k] = real_spec[k] / self.size
            imag_spec[k] = - imag_spec[k] / self.size

        for k in range(0, self.size):
            for i in range(0, self.size):
                real_signal[i] += real_spec[k] * self.cos_table[k * i]
                real_signal[i] += imag_spec[k] * self.sin_table[k * i]


class FFT:
    """
    The Fast Fourier Transform is a faster algorithm for performing the
    :py:class:`.DFT`. It allows converting a time-domain signal into a
    frequency-domain spectrum.

    *Reference:*
        "Digital Signal Processing, a practical guide for engineers and
        scientists", Steven W. Smith
    """

    def __init__(self, size):
        """
        Initialize the Fast Fourier Transform.

        :param size: length of the FFT (should only be a power of 2)
        """
        self.size = size
        self._generate_lookup_tables()

    def _generate_lookup_tables(self):
        """
        Generate internal lookup tables for trigonometric functions (sin, cos)
        """
        table_size = self.size
        self.cos_table = array.array('f', [0] * table_size)
        self.sin_table = array.array('f', [0] * table_size)
        for i in range(1, table_size):
            self.cos_table[i] = math.cos(math.pi / i)
            self.sin_table[i] = math.sin(math.pi / i)

    def forward(self, real_signal, real_spec, imag_spec):
        """
        Compute the complex spectrum of a given real time-domain signal

        :param real_signal: real time-domain input signal
        :param real_spec: real-part of the output complex spectrum
        :param imag_spec: imaginary-part of the output complex spectrum
        """
        spec_len = int(self.size / 2)

        for i in range(0, spec_len):
            real_spec[i] = real_signal[2 * i]
            imag_spec[i] = real_signal[2 * i + 1]

        n = spec_len

        nm1 = n - 1
        nd2 = int(n / 2)
        m = round(math.log(n) / math.log(2))
        j = nd2

        for i in range(1, nm1):
            if i < j:
                tr = real_spec[j]
                ti = imag_spec[j]
                real_spec[j] = real_spec[i]
                imag_spec[j] = imag_spec[i]
                real_spec[i] = tr
                imag_spec[i] = ti
            k = nd2
            while k <= j:
                j -= k
                k /= 2
            j = int(j + k)

        for l in range(1, int(m + 1)):
            le = round(math.pow(2, l))
            le2 = int(le / 2)
            ur = 1
            ui = 0
            sr = self.cos_table[le2]
            si = - self.sin_table[le2]

            for j in range(1, int(le2 + 1)):
                jm1 = j - 1
                for i in range(int(jm1), int(nm1 + 1), int(le)):
                    ip = i + le2
                    tr = real_spec[int(ip)] * ur - imag_spec[int(ip)] * ui
                    ti = real_spec[int(ip)] * ui + imag_spec[int(ip)] * ur
                    real_spec[int(ip)] = real_spec[i] - tr
                    imag_spec[int(ip)] = imag_spec[i] - ti
                    real_spec[i] += tr
                    imag_spec[i] += ti
                tr = ur
                ur = tr * sr - ui * si
                ui = tr * si + ui * sr

        n = n * 2

        nm1 = n - 1
        nd2 = int(n / 2)
        n4 = int(n / 4 - 1)

        for i in range(1, n4 + 1):
            im = nd2 - i
            ip2 = i + nd2
            ipm = im + nd2
            real_spec[ip2] = (imag_spec[i] + imag_spec[im]) / 2
            real_spec[ipm] = real_spec[ip2]
            imag_spec[ip2] = -(real_spec[i] - real_spec[im]) / 2
            imag_spec[ipm] = -imag_spec[ip2]
            real_spec[i] = (real_spec[i] + real_spec[im]) / 2
            real_spec[im] = real_spec[i]
            imag_spec[i] = (imag_spec[i] - imag_spec[im]) / 2
            imag_spec[im] = -imag_spec[i]

        real_spec[int(n * 3 / 4)] = imag_spec[int(n / 4)]
        real_spec[nd2] = imag_spec[0]
        imag_spec[int(n * 3 / 4)] = 0
        imag_spec[nd2] = 0
        imag_spec[int(n / 4)] = 0
        imag_spec[0] = 0

        l = round(math.log(n) / math.log(2))
        le = round(math.pow(2, l))
        le2 = int(le / 2)
        ur = 1
        ui = 0
        sr = self.cos_table[le2]
        si = - self.sin_table[le2]

        for j in range(1, int(le2 + 1)):
            jm1 = j - 1
            for i in range(jm1, nm1 + 1, int(le)):
                ip = int(i + le2)
                tr = real_spec[ip] * ur - imag_spec[ip] * ui
                ti = real_spec[ip] * ui + imag_spec[ip] * ur
                real_spec[ip] = real_spec[i] - tr
                imag_spec[ip] = imag_spec[i] - ti
                real_spec[i] += tr
                imag_spec[i] += ti
            tr = ur
            ur = tr * sr - ui * si
            ui = tr * si + ui * sr

    def inverse(self, real_spec, imag_spec, real_signal):
        """
        Compute the real time-domain signal of a given complex spectrum

        :param real_spec: real-part of the complex spectrum
        :param imag_spec: imaginary-part of the complex spectrum
        :param real_signal: real time-domain output signal
        """
        n = self.size
        nspec = int(n / 2 + 1)

        for k in range(nspec, n):
            real_spec[k] = real_spec[n - k]
            imag_spec[k] = - imag_spec[n - k]

        for k in range(0, n):
            real_spec[k] = real_spec[k] + imag_spec[k]

        tmp_real = [0] * n
        tmp_imag = [0] * n

        self.forward(real_spec, tmp_real, tmp_imag)

        for i in range(0, n):
            real_signal[i] = (tmp_real[i] + tmp_imag[i]) / n


class AnalysisWindow:
    """
    An analysis window function allows to reduce unwanted frequencies
    when performing spectrum analysis.
    """

    def __init__(self, size):
        """
        Initialize the analysis window. By default, a flat window is applied.
        Use one of the provided methods to make it Hanning or Hamming.

        :param size: length of the analysis window
        """
        self._resize(size)

    def hanning(self, size):
        """
        Make a Hanning analysis window.

        :param size: length of the analysis window
        """
        self._resize(size)
        for i in range(0, self.size):
            self.signal[i] = (0.5 -
                              (0.5 * math.cos(2.0 * math.pi * i /
                                              (self.size - 1))))

    def hamming(self, size):
        """
        Make a Hamming analysis window.

        :param size: length of the analysis window
        """
        self._resize(size)
        for i in range(0, self.size):
            self.signal[i] = (0.54 -
                              (0.46 * math.cos(2.0 * math.pi * i /
                                               (self.size - 1))))

    def blackman(self, size):
        """
        Make a Blackman analysis window.

        :param size: length of the analysis window
        """
        self._resize(size)
        for i in range(0, self.size):
            self.signal[i] = (0.42659 -
                              (0.49656 * math.cos(2.0 * math.pi * i /
                                                  (self.size - 1))) +
                              (0.076849 * math.cos(4.0 * math.pi * i /
                                                   (self.size - 1))))

    def process(self, input_signal, output_signal):
        """
        Perform windowing on an input signal.

        :param input_signal: input signal to be windowed
        :param output_signal: resulting windowed signal
        """
        for i in range(0, self.size):
            output_signal[i] = input_signal[i] * self.signal[i]

    def _resize(self, size):
        """
        Resize the analysis window.

        :param size: new length of the analysis window
        """
        self.size = size
        self.signal = array.array('f', [1] * self.size)
