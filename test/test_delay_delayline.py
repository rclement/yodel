import unittest
import yodel.delay
import math


class TestDelayLine(unittest.TestCase):

    def setUp(self):
        self.samplerate = 48000
        self.block_size = 512
        self.maxdelay = 100
        self.dly = yodel.delay.DelayLine(self.samplerate, self.maxdelay, 0)

    def tearDown(self):
        pass

    def test_zero_delay(self):
        self.dly.set_delay(0)
        inbuffer = [math.sin(2.0*math.pi*100*i/self.samplerate) for i in range(0, self.block_size)]
        outbuffer = [0] * self.block_size

        self.dly.process(inbuffer, outbuffer)

        for i in range(0, self.block_size):
            self.assertEqual(inbuffer[i], outbuffer[i])

    def test_int_delay(self):
        delaysmp = int(self.block_size / 2.0)
        delay = delaysmp * 1000.0 / self.samplerate
        self.dly.set_delay(delay)
        inbuffer = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(1, self.block_size+1)]
        outbuffer = [0] * self.block_size

        self.dly.process(inbuffer, outbuffer)

        for i in range(0, delaysmp):
            self.assertEqual(outbuffer[i], 0)
        for i in range(delaysmp, self.block_size):
            self.assertEqual(outbuffer[i], inbuffer[i-delaysmp])

    def test_frac_delay(self):
        frac = 0.125
        delaysmp = 23
        delay = (delaysmp+frac) * 1000 / self.samplerate
        self.dly.set_delay(delay)
        inbuffer = [math.sin(2.0*math.pi*100*i/self.samplerate) for i in range(1, self.block_size+1)]
        outbuffer = [0] * self.block_size

        self.dly.process(inbuffer, outbuffer)

        for i in range(0, delaysmp-1):
            self.assertEqual(outbuffer[i], 0)
        for i in range(delaysmp-1, delaysmp):
            self.assertEqual(outbuffer[i], frac * inbuffer[0])
        for i in range(delaysmp, self.block_size):
            self.assertEqual(outbuffer[i], (1-frac) * inbuffer[i-(delaysmp)] + frac * inbuffer[i-(delaysmp-1)])

    def test_max_delay(self):
        delay = 2000
        delaysmp = int(delay * self.samplerate / 1000.0)
        maxdelaysmp = int(self.maxdelay * self.samplerate / 1000.0)
        self.dly.set_delay(delay)
        inbuffer = [math.sin(2.0*math.pi*100*i/self.samplerate) for i in range(0, (maxdelaysmp+2))]
        outbuffer = [0] * (maxdelaysmp+2)

        self.dly.process(inbuffer, outbuffer)

        for i in range(0, maxdelaysmp):
            self.assertEqual(outbuffer[i], 0)
        for i in range(maxdelaysmp, (maxdelaysmp+2)):
            self.assertEqual(outbuffer[i], inbuffer[i-maxdelaysmp])

    def test_negative_delay(self):
        self.dly.set_delay(-123)
        inbuffer = [math.sin(2.0*math.pi*100*i/self.samplerate) for i in range(0, self.block_size)]
        outbuffer = [0] * self.block_size

        self.dly.process(inbuffer, outbuffer)

        for i in range(0, self.block_size):
            self.assertEqual(inbuffer[i], outbuffer[i])

    def test_clear_delayline(self):
        delaysmp = int(self.block_size / 2.0)
        delay = delaysmp * 1000.0 / self.samplerate
        self.dly.set_delay(delay)
        inbuffer = [math.sin(2.0*math.pi*100.0*i/self.samplerate) for i in range(1, self.block_size+1)]
        outbuffer = [0] * self.block_size

        self.dly.process(inbuffer, outbuffer)
        self.dly.clear()

        for i in range(0, self.block_size):
            self.assertEqual(self.dly.delayline[i], 0)


if __name__ == '__main__':
    unittest.main()
