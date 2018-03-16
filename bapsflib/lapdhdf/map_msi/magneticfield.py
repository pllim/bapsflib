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
import h5py
import numpy as np

from warnings import warn

from .msi_template import hdfMap_msi_template


class hdfMap_msi_magneticfield(hdfMap_msi_template):
    """
    Mapping class for the 'Magnetic field' MSI diagnostic.

    Simple group structure looks like:

    .. code-block:: none

        +-- Magnetic field
        |   +-- Magnet power supply currents
        |   +-- Magnetic field profile
        |   +-- Magnetic field summary
    """
    def __init__(self, diag_group):
        """
        :param diag_group: the HDF5 MSI diagnostic group
        :type diag_group: :class:`h5py.Group`
        """
        # initialize
        hdfMap_msi_template.__init__(self, diag_group)

        # populate self.configs
        self._build_configs()

    def _build_configs(self):
        """Builds the :attr:`configs` dictionary."""
        # assume build is successful
        # - alter if build fails
        #
        self._build_successful = True
        warn_why = ''
        for dset_name in ['Magnet power supply currents',
                          'Magnetic field profile',
                          'Magnetic field summary']:
            if dset_name not in self.group:
                warn_why = 'dataset (' + dset_name + ') not found'
                warn("Mapping for MSI Diagnostic 'Magnetic field' was"
                     " unsuccessful (" + warn_why + ")")
                self._build_successful = False
                return

        # initialize general info values
        self._configs['z'] = self.group.attrs['Profile z locations']
        self._configs['shape'] = ()

        # initialize 'shotnum'
        self._configs['shotnum'] = {
            'dset paths': [],
            'dset field': 'Shot number',
            'shape': [],
            'dtype': np.int32
        }

        # initialize 'signals'
        # - there are two signal fields
        #   1. 'magnet ps current'
        #   2. 'magnetic field'
        #
        self._configs['signals'] = {
            'magnet ps current': {
                'dset paths': [],
                'dset field': None,
                'shape': [],
                'dtype': np.float32
            },
            'magnetic field': {
                'dset paths': [],
                'dset field': None,
                'shape': [],
                'dtype': np.float32
            }
        }

        # initialize 'meta'
        self._configs['meta'] = {
            'shape': (),
            'timestamp': {
                'dset paths': [],
                'dset field': 'Timestamp',
                'shape': [],
                'dtype': np.float64
            },
            'data valid': {
                'dset paths': [],
                'dset field': 'Data valid',
                'shape': [],
                'dtype': np.int8
            },
            'peak magnetic field': {
                'dset paths': [],
                'dset field': 'Peak magnetic field',
                'shape': [],
                'dtype': np.float32
            },
        }

        # ---- update configs related to 'Magnetic field summary'   ----
        # - dependent configs are:
        #   1. 'shotnum'
        #   2. all of 'meta'
        #
        dset_name = 'Magnetic field summary'
        dset = self.group[dset_name]

        # define 'shape'
        if dset.ndim == 1:
            self._configs['shape'] = dset.shape
        else:
            warn_why = "'/Magnetic field summary' does not match " \
                       "expected shape"
            warn("Mapping for MSI Diagnostic 'Magnetic field' was"
                 " unsuccessful (" + warn_why + ")")
            self._build_successful = False
            return

        # update 'shotnum'
        self._configs['shotnum']['dset paths'].append(dset.name)
        self._configs['shotnum']['shape'].append(
            dset.dtype['Shot number'].shape)

        # update 'meta/timestamp'
        self._configs['meta']['timestamp']['dset paths'].append(
            dset.name)
        self._configs['meta']['timestamp']['shape'].append(
            dset.dtype['Timestamp'].shape)

        # update 'meta/data valid'
        self._configs['meta']['data valid']['dset paths'].append(
            dset.name)
        self._configs['meta']['data valid']['shape'].append(
            dset.dtype['Data valid'].shape)

        # update 'meta/peak magnetic field'
        self._configs['meta']['peak magnetic field']['dset paths'].append(
            dset.name)
        self._configs['meta']['peak magnetic field']['shape'].append(
            dset.dtype['Peak magnetic field'].shape)

        # update configs related to 'Magnet power supply currents'  ----
        # - dependent configs are:
        #   1. 'signals/magnet ps current'
        #
        dset_name = 'Magnet power supply currents'
        dset = self.group[dset_name]
        self._configs['signals']['magnet ps current'][
            'dset paths'].append(dset.name)

        # check 'shape'
        if dset.ndim == 2:
            if dset.shape[0] == self._configs['shape'][0]:
                self._configs['signals']['magnet ps current'][
                    'shape'].append((dset.shape[1],))
            else:
                self._build_successful = False
        else:
            self._build_successful = False
        if not self._build_successful:
            warn_why = "'/Magnet power supply currents' does not " \
                       "match expected shape"
            warn("Mapping for MSI Diagnostic 'Magnetic field' was"
                 " unsuccessful (" + warn_why + ")")
            return

        # ---- update configs related to 'Magnetic field profile'   ----
        # - dependent configs are:
        #   1. 'signals/magnetic field'
        #
        dset_name = 'Magnetic field profile'
        dset = self.group[dset_name]
        self._configs['signals']['magnetic field'][
            'dset paths'].append(dset.name)

        # check 'shape'
        if dset.ndim == 2:
            if dset.shape[0] == self._configs['shape'][0]:
                self._configs['signals']['magnetic field'][
                    'shape'].append((dset.shape[1],))
            else:
                self._build_successful = False
        else:
            self._build_successful = False
        if not self._build_successful:
            warn_why = "'/Magnetic field profile' does not " \
                       "match expected shape"
            warn("Mapping for MSI Diagnostic 'Magnetic field' was"
                 " unsuccessful (" + warn_why + ")")
            return
