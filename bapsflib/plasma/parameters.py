# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017-2018 Erik T. Everson and contributors
#
# License: Standard 3-clause BSD; see "LICENSES/LICENSE.txt" for full
#   license terms and contributor agreement.
#
# TODO: add plasma betas (electron, ion, and total)
# TODO: add Coulomb Logarithm
# TODO: add collision frequencies
# TODO: add mean-free-paths
#
"""
Plasma parameters

All units are in Gaussian cgs except for temperature, which is
expressed in eV. (same as the NRL Plasma Formulary)
"""
import astropy.units as u
import numpy as np

from . import constants as conts
from plasmapy import utils
from typing import Union


# ---- Frequencies                                                  ----
@utils.check_quantity({'q': {'units': u.statcoulomb,
                             "can_be_negative": True},
                       'B': {'units': u.Gauss,
                             "can_be_negative": False},
                       'm': {'units': u.g,
                             "can_be_negative": False}})
def cyclotron_frequency(q: u.Quantity, B: u.Quantity, m: u.Quantity,
                        to_Hz=False, **kwargs) -> u.Quantity:
    """
    particle cyclotron frequency (rad/s)

    .. math::

        \\Omega_{c} = \\frac{q B}{m c}

    :param q: particle charge (in statcoulomb)
    :param B: magnetic-field (in Gauss)
    :param m: particle mass (in grams)
    :param to_Hz: :code:`False` (DEFAULT). Set to :code:`True` to
        return frequency in Hz (i.e. divide by :math:`2 * \\pi`)
    """
    # ensure args have correct units
    q = q.to(u.Fr)
    B = B.to(u.gauss)
    m = m.to(u.g)

    # calculate
    _oc = ((q.value * B.value) / (m.value * conts.c.cgs.value))
    if to_Hz:
        _oc = (_oc / (2.0 * conts.pi)) * u.Hz
    else:
        _oc = _oc * (u.rad / u.s)
    return _oc


@utils.check_quantity({'n': {'units': u.cm ** -3,
                             "can_be_negative": False},
                       'q': {'units': u.statcoulomb,
                             "can_be_negative": True},
                       'm': {'units': u.g,
                             "can_be_negative": False}})
def plasma_frequency_generic(
        n: u.Quantity, q: u.Quantity, m: u.Quantity,
        to_Hz=False, **kwargs) -> u.Quantity:
    """
    generalized plasma frequency (rad/s)

    .. math::

        \\omega_{p}^{2} = \\frac{4 \\pi n q^{2}}{m}

    :param n: particle number density (in number/cm^3)
    :param q: particle charge (in statcoulombs)
    :param m: particle mass (in g)
    :param to_Hz: :code:`False` (DEFAULT). Set to :code:`True` to
        return frequency in Hz (i.e. divide by :math:`2 * \\pi`)
    """
    # ensure args have correct units
    n = n.to(u.cm ** -3)
    q = q.to(u.Fr)
    m = m.to(u.g)

    # calculate
    _op = np.sqrt((4.0 * conts.pi * n.value * (q.value * q.value))
                  / m.value)
    if to_Hz:
        _op = (_op / (2.0 * conts.pi)) * u.Hz
    else:
        _op = _op * (u.rad / u.s)
    return _op


@utils.check_quantity({'B': {'units': u.Gauss,
                             "can_be_negative": False}})
def oce(B: u.Quantity, **kwargs) -> u.Quantity:
    """
    electron-cyclotron frequency (rad/s)

    .. math::

        \\Omega_{ce} = -\\frac{|e| B}{m_{e} c}

    :param B: magnetic-field (in Gauss)
    :param kwargs: supports any keywords used by
        :func:`cyclotron_frequency`
    """
    return cyclotron_frequency(-conts.e_gauss, B, conts.m_e,
                               **kwargs['kwargs'])


@utils.check_quantity({'B': {'units': u.Gauss,
                             "can_be_negative": False},
                       'm_i': {'units': u.g,
                               "can_be_negative": False}})
def oci(Z: Union[int, float], B: u.Quantity, m_i: u.Quantity,
        **kwargs) -> u.Quantity:
    """
    ion-cyclotron frequency (rad/s)

    .. math::

        \\Omega_{ci} = \\frac{Z |e| B}{m_{i} c}

    :param Z: charge number
    :param B: magnetic-field (in Gauss)
    :param m_i: ion mass (in grams)
    :param kwargs: supports any keywords used by
        :func:`cyclotron_frequency`
    """
    return cyclotron_frequency(Z * conts.e_gauss, B, m_i,
                               **kwargs['kwargs'])
