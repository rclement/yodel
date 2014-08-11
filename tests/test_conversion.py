import unittest
import yodel.conversion as dc


class TestLin2Db(unittest.TestCase):

    def test_one(self):
        self.assertEqual(dc.lin2db(1.0), 0.0)

    def test_min_limit(self):
        self.assertEqual(dc.lin2db(1e-5), -100.0)

    def test_minus_inf(self):
        self.assertEqual(dc.lin2db(1e-10), -100.0)


class TestDb2Lin(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(dc.db2lin(0.0), 1.0)

    def test_minus_inf(self):
        self.assertEqual(dc.db2lin(-100), 1.0e-5)

