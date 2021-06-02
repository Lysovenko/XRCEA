import unittest
from sys import path
path.append("../components/cryp")
from itertools import product
from numpy import array, sqrt, zeros, sin, tan, cos, average
from numpy.random import random
from cellparams import (calc_orhomb, calc_hex, calc_tetra, calc_cubic,
                        calc_monoclinic)


class TestCellparams(unittest.TestCase):
    def test_orhomb(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        h, k, el = hkl
        a, b, c = 3., 4., 5.

        def get_d(a, b, c):
            d = 1. / a ** 2 * h ** 2 + 1. / b ** 2 * k ** 2 + \
                1. / c ** 2 * el ** 2
            return sqrt(1. / d)

        d = get_d(a, b, c)
        dhkl = zeros((4, len(d)))
        dhkl[0, :] = d
        dhkl[1:, :] = hkl
        a1, b1, c1 = calc_orhomb(dhkl)[:3]
        self.assertEqual((a1, b1, c1), (a, b, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, b1, c1, _, _, _, chi2 = calc_orhomb(dhkl)[:7]
        d2 = get_d(a1, b1, c1)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_hex(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a, c = 3.1, 5.2

        def get_d(a, c):
            d = 4. / 3. / a ** 2 * (h ** 2 + h * k + k ** 2)\
                + 1. / c ** 2 * el ** 2
            return sqrt(1. / d)

        d = get_d(a, c)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        a1, _, c1, _, _, _, chi2, siga, _, sigc, _, _, _ = calc_hex(dhkl)
        self.assertEqual((a1, c1), (a, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, c1, _, _, _, chi2, siga, _, sigc, _, _, _ = calc_hex(dhkl)
        d2 = get_d(a1, c1)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)
        self.assertLessEqual((a - a1)**2, siga)
        self.assertLessEqual((c - c1)**2, sigc)
        print((a - a1) ** 2, siga, '\n', (c - c1) ** 2, sigc)

    def test_tetra(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a, c = 3.1, 5.1

        def get_d(a, c):
            d = 1. / a ** 2 * (h ** 2 + k ** 2) + 1. / c ** 2 * el ** 2
            return sqrt(1. / d)

        d = get_d(a, c)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        a1, _, c1 = calc_tetra(dhkl)[:3]
        self.assertEqual((a1, c1), (a, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, c1, _, _, _, chi2 = calc_tetra(dhkl)[:7]
        d2 = get_d(a1, c1)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_cubic(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:])
        h, k, el = hkl.transpose()
        a = 3.2

        def get_d(a):
            d = 1. / a ** 2 * (h ** 2 + k ** 2 + el ** 2)
            return sqrt(1. / d)

        d = get_d(a)
        dhkl = array(list(zip(d, h, k, el))).transpose()
        self.assertEqual(calc_cubic(dhkl)[0], a)
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, _, _, _, _, chi2 = calc_cubic(dhkl)[:7]
        d2 = get_d(a1)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_rhombohedral(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        h, k, el = hkl
        a, alp = 3., 1.5

        def get_d(a, alp):
            d = 1. / a ** 2. * (((1. + cos(alp)) * (
                (h ** 2 + k ** 2 + el ** 2) - (
                    1. - tan(alp / 2.) ** 2) * (
                        h * k + k * el + el * h))) / (
                            1. + cos(alp) - 2. * cos(alp) ** 2))
            return sqrt(1. / d)

        d = get_d(a, alp)
        dhkl = zeros((4, len(d)))
        dhkl[0, :] = d
        dhkl[1:, :] = hkl
        # self.assertEqual(calc_rhombohedral(dhkl)[:4], (a, None, None, alp))

    def test_monoclinic(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        h, k, el = hkl
        a, b, c, bet = 3.1, 4.1, 5., 1.45

        def get_d(a, b, c, bet):
            d = 1. / a ** 2. * (h ** 2 / sin(bet) ** 2) + \
                1. / b ** 2 * k ** 2 + 1 / c ** 2 * el ** 2 \
                / (sin(bet) ** 2) - 2 * h * el / \
                (a * c * sin(bet) * tan(bet))
            return sqrt(1. / d)

        d = get_d(a, b, c, bet)
        dhkl = zeros((4, len(d)))
        dhkl[0, :] = d
        dhkl[1:, :] = hkl
        a1, b1, c1, _, bet1 = calc_monoclinic(dhkl)[:5]
        self.assertAlmostEqual(a1, a)
        self.assertAlmostEqual(b1, b)
        self.assertAlmostEqual(c1, c)
        self.assertAlmostEqual(bet1, bet)
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, b1, c1, _, bet1, _, chi2 = calc_monoclinic(dhkl)[:7]
        d2 = get_d(a1, b1, c1, bet1)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)
