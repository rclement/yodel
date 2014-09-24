"""
This module provides classes for delaying signals.
"""

import math


class DelayLine:
    """
    A delayline allows to delay a given signal by a certain amount of time or
    samples. Time-varying delay is allowed.
    """

    def __init__(self, samplerate, maxdelay=1000, delay=0):
        """
        Create a delayline.

        :param samplerate: sample-rate in Hz
        :param maxdelay: maximum allowed delay in ms
        :param delay: initial delay in ms
        """
        self.samplerate = samplerate
        self.maxdelay = maxdelay
        self.maxsampledelay = maxdelay * samplerate / 1000.0
        self.length = 1 << int(math.ceil(math.log(self.maxsampledelay, 2)))
        self.mask = self.length - 1
        self.delayline = [0] * self.length
        self.writepos = 0
        self.set_delay(delay)

    def clear(self):
        """
        Clear the current samples in the delayline with zeros.
        Every other state is kept (current delay, max delay).
        """
        for i in range(0, self.length):
            self.delayline[i] = 0

    def process_sample(self, input_sample):
        """
        Delay an input sample by the current amount of delay.

        :param input_signal: sample to be delayed
        :return: resulting delayed sample
        """
        self.delayline[self.writepos] = input_sample
        self.writepos = (self.writepos + 1) & self.mask
        prev_idx = int(math.floor(self.readpos))
        next_idx = (prev_idx + 1) & self.mask
        frac_pos = self.readpos - prev_idx
        output_sample = ((1.0 - frac_pos) * self.delayline[prev_idx] +
                         frac_pos * self.delayline[next_idx])
        self.readpos = ((prev_idx + 1) & self.mask) + frac_pos
        return output_sample

    def process(self, input_signal, output_signal):
        """
        Delay an input signal by the current amount of delay.

        :param input_signal: signal to be delayed
        :param output_signal: resulting delayed signal
        """
        size = len(input_signal)
        for i in range(0, size):
            output_signal[i] = self.process_sample(input_signal[i])

    def set_delay(self, delay):
        """
        Specify a new time delay value.

        :param delay: new delay value in ms
        """
        if delay < 0:
            self.delay = 0
        elif delay > self.maxdelay:
            self.delay = self.maxdelay
        else:
            self.delay = delay

        self.sampledelay = self.delay * self.samplerate / 1000.0
        frac = self.sampledelay - int(self.sampledelay)
        self.readpos = ((self.writepos + self.length - int(self.sampledelay))
                        & self.mask) + frac
