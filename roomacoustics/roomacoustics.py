# -*- coding: utf-8 -*-

"""Main module."""

import re
import numpy as np


def reverberation_time_energy_decay_curve(energy_decay_curve, times, T='T20', normalize=True):
    """Estimate the reverberation time from a given energy decay curve according
    to the ISO standard 3382 _[1].

    Parameters
    ----------
    energy_decay_curve : ndarray, double
        Energy decay curve. The time needs to be the arrays last dimension.
    times : ndarray, double
        Time vector corresponding to each sample of the EDC.
    T : 'T20', 'T30', 'T40', 'T50', 'T60', 'EDT'
        Decay interval to be used for the reverberation time extrapolation

    Returns
    -------
    reverberation_time : double
        The reverberation time

    References
    ----------
    .. [1]  ISO 3382, Acoustics - Measurement of the reverberation time of rooms
            with reference to other acoustical parameters.

    """
    if T == 'EDT':
        upper = 0.
        lower = -10.
    else:
        upper = -5
        lower = -np.double(re.findall(r'\d+', T)) + upper

    if normalize:
        energy_decay_curve /= energy_decay_curve[0]

    edc_db = 10*np.log10(np.abs(energy_decay_curve))

    idx_upper = np.argmin(np.abs(upper - edc_db))
    idx_lower = np.argmin(np.abs(lower - edc_db))

    edc_upper = edc_db[idx_upper]
    edc_lower = edc_db[idx_lower]

    time_upper = times[idx_upper]
    time_lower = times[idx_lower]

    reverberation_time = -60/((edc_lower - edc_upper)/(time_lower - time_upper))

    return reverberation_time


def energy_decay_curve_analytic(
        surfaces, alphas, volume, times, source=None,
        receiver=None, method='eyring', c=343.4, frequency=None):
    """Calculate the energy decay curve analytically by using Eyring's or
    Sabine's equation _[2].

    Parameters
    ----------
    surfaces : ndarray, double
        Surface areas of all surfaces in the room
    alphas : ndarray, double
        Absorption coefficients corresponding to each surface
    volume : double
        Room volume
    times : ndarray, double
        Time vector for which the decay curve is calculated
    source : Coordinates
        Coordinate object with the source coordinates
    receiver : Coordinates
        Coordinate object with the receiver coordinates
    method : 'eyring', 'sabine'
        Use either Eyring's or Sabine's equation
    c : double
        Speed of sound
    frequency : double, optional
        Center frequency of the respective octave band. This is only used for
        the air absorption calculation.

    Returns
    -------
    energy_decay_curve : ndarray, double
        The energy decay curve

    References
    ----------
    .. [2]  H. Kuttruff, Room acoustics, 4th Ed. Taylor & Francis, 2009.

    """

    alphas = np.asarray(alphas)
    surfaces = np.asarray(surfaces)
    surface_room = np.sum(surfaces)
    alpha_mean = np.sum(surfaces*alphas) / surface_room

    m = 0
    if all([source, receiver]):
        dist_source_receiver = np.linalg.norm(
            source.cartesian - receiver.cartesian)
        delay_direct = dist_source_receiver / c
    else:
        delay_direct = 0

    if method == 'eyring':
        energy_decay_curve = np.exp(
            -c*(times - delay_direct) *
            ((-surface_room * np.log(1 - alpha_mean) / 4 / volume) + m))
    elif method == 'sabine':
        energy_decay_curve = np.exp(
            -c*(times - delay_direct) *
            ((surface_room * alpha_mean / 4 / volume) + m))
    else:
        raise ValueError("The method has to be either 'eyring' or 'sabine'.")


    return energy_decay_curve
