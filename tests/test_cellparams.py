import unittest
from sys import path
path.append("../components/cryp")
from itertools import product
from numpy import array, sqrt, zeros
from cellparams import calc_orhomb, calc_hex, calc_tetra, calc_cubic


class TestCellparams(unittest.TestCase):
    def test_orhomb(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        h, k, el = hkl
        a, b, c = 3., 4., 5.
        d = 1. / a ** 2 * h ** 2 + 1. / b ** 2 * k ** 2 + 1. / c ** 2 * el ** 2
        d = sqrt(1. / d)
        dhkl = zeros((4, len(d)))
        dhkl[0, :] = d
        dhkl[1:, :] = hkl
        self.assertEqual(calc_orhomb(dhkl)[:3], (a, b, c))

    def test_hex(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a, c = 3.1, 5.2
        d = 4. / 3. / a ** 2 * (h ** 2 + h * k + k ** 2)\
            + 1. / c ** 2 * el ** 2
        d = sqrt(1. / d)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        self.assertEqual(calc_hex(dhkl)[:3], (a, None, c))

    def test_tetra(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a, c = 3.1, 5.1
        d = 1. / a ** 2 * (h ** 2 + k ** 2) + 1. / c ** 2 * el ** 2
        d = sqrt(1. / d)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        self.assertEqual(calc_tetra(dhkl)[:3], (a, None, c))

    def test_cubic(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a = 3.2
        d = 1. / a ** 2 * (h ** 2 + k ** 2 + el ** 2)
        d = sqrt(1. / d)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        self.assertEqual(calc_cubic(dhkl)[0], a)


if __name__ == "__main__":
    unittest.main()
