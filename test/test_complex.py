import unittest
import math
import yodel.complex as dc


class TestModulus(unittest.TestCase):

    def test_zero_zero(self):
        self.assertEqual(dc.modulus(0.0, 0.0), 0.0)

    def test_one_zero(self):
        self.assertEqual(dc.modulus(1.0, 0.0), 1.0)

    def test_zero_one(self):
        self.assertEqual(dc.modulus(0.0, 1.0), 1.0)

    def test_one_one(self):
        self.assertEqual(dc.modulus(1.0, 1.0), math.sqrt(2))

    def test_sqrt_2_on_2(self):
        self.assertEqual(dc.modulus(math.sqrt(2) / 2.0, math.sqrt(2) / 2.0), 1.0)

    def test_sqrt_3_on_2(self):
        self.assertAlmostEqual(dc.modulus(math.sqrt(3) / 2.0, 1.0 / 2.0), 1.0)


class TestPhase(unittest.TestCase):

    def test_zero_zero(self):
        self.assertEqual(dc.phase(0.0, 0.0), 0.0)

    def test_one_zero(self):
        self.assertEqual(dc.phase(1.0, 0.0), 0.0)

    def test_zero_one(self):
        self.assertEqual(dc.phase(0.0, 1.0), math.pi / 2.0)

    def test_pi_on_six(self):
        self.assertAlmostEqual(dc.phase(1.0 / 2.0, math.sqrt(3) / 2.0), math.pi / 3.0)

    def test_pi_on_four(self):
        self.assertEqual(dc.phase(math.sqrt(2) / 2.0, math.sqrt(2) / 2.0), math.pi / 4.0)

    def test_pi_on_six(self):
        self.assertAlmostEqual(dc.phase(math.sqrt(3) / 2.0, 1.0 / 2.0), math.pi / 6.0)
