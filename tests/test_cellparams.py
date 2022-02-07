import unittest
from sys import path
path.append("../xrcea/components/cryp")
from itertools import product
from numpy import array, sqrt, zeros, sin, tan, cos, average
from numpy.random import random
from cellparams import (
    calc_orhomb, calc_hex, calc_tetra, calc_cubic, calc_monoclinic,
    calc_rhombohedral,
    d_hkl_orhomb, d_hkl_hex, d_hkl_tetra, d_hkl_cubic, d_hkl_rhombohedral,
    d_hkl_monoclinic)


class TestCellparams(unittest.TestCase):
    @staticmethod
    def mkdkhl(d, hkl):
        dhkl = zeros((4, len(d)))
        dhkl[0, :] = d
        dhkl[1:, :] = hkl
        return dhkl

    def test_orhomb(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a, b, c = 3., 4., 5.
        d = d_hkl_orhomb(a, b, c, hkl)
        dhkl = self.mkdkhl(d, hkl)
        a1, b1, c1 = calc_orhomb(dhkl)[:3]
        self.assertEqual((a1, b1, c1), (a, b, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, b1, c1, _, _, _, chi2 = calc_orhomb(dhkl)[:7]
        d2 = d_hkl_orhomb(a1, b1, c1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_hex(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a, c = 3.1, 5.2
        d = d_hkl_hex(a, c, hkl)
        dhkl = self.mkdkhl(d, hkl)
        a1, _, c1, _, _, _, chi2, siga, _, sigc, _, _, _ = calc_hex(dhkl)
        self.assertEqual((a1, c1), (a, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, c1, _, _, _, chi2, siga, _, sigc, _, _, _ = calc_hex(dhkl)
        d2 = d_hkl_hex(a1, c1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)
        self.assertLessEqual((a - a1)**2, siga)
        self.assertLessEqual((c - c1)**2, sigc)

    def test_tetra(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a, c = 3.1, 5.1
        d = d_hkl_tetra(a, c, hkl)
        dhkl = self.mkdkhl(d, hkl)
        a1, _, c1 = calc_tetra(dhkl)[:3]
        self.assertEqual((a1, c1), (a, c))
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, c1, _, _, _, chi2 = calc_tetra(dhkl)[:7]
        d2 = d_hkl_tetra(a1, c1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_cubic(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a = 3.2
        d = d_hkl_cubic(a, hkl)
        dhkl = self.mkdkhl(d, hkl)
        self.assertEqual(calc_cubic(dhkl)[0], a)
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, _, _, _, _, chi2 = calc_cubic(dhkl)[:7]
        d2 = d_hkl_cubic(a1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_rhombohedral(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a, alp = 3.65556, 1.57
        d = d_hkl_rhombohedral(a, alp, hkl)
        dhkl = self.mkdkhl(d, hkl)
        a1, _, _, alp1 = calc_rhombohedral(dhkl)[:4]
        self.assertAlmostEqual(a1, a)
        self.assertAlmostEqual(alp1, alp)
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, _, _, alp1, _, _, chi2 = calc_rhombohedral(dhkl)[:7]
        d2 = d_hkl_rhombohedral(a1, alp1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)

    def test_monoclinic(self):
        hkl = array(list(product(*((tuple(range(5)),) * 3)))[1:]).transpose()
        a, b, c, bet = 3.1, 4.1, 5., 1.45
        d = d_hkl_monoclinic(a, b, c, bet, hkl)
        dhkl = self.mkdkhl(d, hkl)
        a1, b1, c1, _, bet1 = calc_monoclinic(dhkl)[:5]
        self.assertAlmostEqual(a1, a)
        self.assertAlmostEqual(b1, b)
        self.assertAlmostEqual(c1, c)
        self.assertAlmostEqual(bet1, bet)
        dr = d + (random(len(d)) - .5) * .1
        dhkl[0] = dr
        a1, b1, c1, _, bet1, _, chi2 = calc_monoclinic(dhkl)[:7]
        d2 = d_hkl_monoclinic(a1, b1, c1, bet1, hkl)
        self.assertAlmostEqual(average((1 / dr**2 - 1 / d2**2)**2), chi2)
