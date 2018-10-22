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
import bapsflib
import os
import pprint as pp
import sys

from datetime import datetime

from .file import File


class HDFOverview(object):
    """
    Reports an overview of the HDF5 file mapping.
    """
    def __init__(self, hdf_obj: File):
        """
        :param hdf_obj: HDF5 file map object
        :type hdf_obj: :class:`bapsflib.lapd.File`
        """
        super().__init__()

        # store an instance of the HDF5 file object for HDFOverview
        if isinstance(hdf_obj, File):
            self._file = hdf_obj
            self._fmap = hdf_obj.file_map
        else:
            raise ValueError('input arg is not of type HDFMap')

    def print(self):
        """
        Print full Overview Report.
        """
        # TODO: add a self.report_data_run_sequence
        # TODO: add a self.report_motion_lists
        #
        # ------ Print Header                                     ------
        print('=' * 72)
        print('{} Overview'.format(self._file.info['filename']))
        print('Generated by bapsflib (v' + bapsflib.__version__ + ')')
        print('Generated date: '
              + datetime.now().strftime('%-m/%-d/%Y %-I:%M:%S %p'))
        print('=' * 72 + '\n\n')

        # ------ Print General Info                               ------
        self.report_general()

        # ------ Print Discovery Report                           ------
        self.report_discovery()

        # ------ Print Detailed Reports                           ------
        self.report_details()

    def report_general(self):
        """
        Prints general HDF5 file info.
        """
        # print basic file info
        print('Filename:     {}'.format(
            self._file.info['filename']))
        print('Abs. Path:    {}'.format(
            self._file.info['absolute file path']))
        print('LaPD version: {}'.format(
            self._file.info['lapd version']))
        print('Investigator: {}'.format(
            self._file.info['investigator']))
        print('Run Date:     {}'.format
              (self._file.info['run date']))

        # exp. and run structure
        print('\nExp. and Run Structure:')
        print('  (set)  {}'.format(self._file.info['exp set name']))
        print('  (exp)  +-- {}'.format(self._file.info['exp name']))
        print('  (run)  |   +-- {}'.format(
            self._file.info['run name']))

        # print run description
        print('\nRun Description:')
        for line in self._file.info['run description'].splitlines():
            print('    ' + line)

        # print exp description
        print('\nExp. Description:')
        for line in self._file.info['exp description'].splitlines():
            print('    ' + line)

    def report_discovery(self):
        """
        Prints a discovery (brief) report of all detected MSI
        diagnostics, digitizers, and control devices.
        """
        # print header
        print('\n\nDiscovery Report')
        print('----------------\n')

        # print msi
        self.msi_discovery()

        # print data
        self.data_discovery()

    def report_details(self):
        """
        Prints a detailed report of all detected MSI diagnostics,
        digitizers, and control devices.
        """
        # print header
        print('\n\nDetailed Reports')
        print('-----------------')

        # digitizer report
        self.report_digitizers()

        # control devices report
        self.report_controls()

        # msi report
        self.report_msi()

    def save(self, filename):
        """Saves the HDF5 overview to a text file."""
        if filename is True:
            # use the same name as the HDF5 file
            filename = os.path.splitext(self._file.filename)[0]\
                       + '.txt'

        # write to file
        with open(filename, 'w') as of:
            sys.stdout = of
            self.print()

        # return to standard output
        sys.stdout = sys.__stdout__

    def msi_discovery(self):
        """
        Prints a discovery report of the 'MSI' Group.
        """
        # is there a MSI
        # msi_detected = self._fmap.has_msi_group
        msi_detected = self._fmap._MSI_PATH in self._file

        # print status to screen
        item = self._fmap._MSI_PATH + '/'
        found = 'found' if msi_detected else 'missing'
        status_print(item, found, '', item_found_pad=' ')

        # print number of diagnostics
        ndiag = len(self._fmap.msi)
        item = 'diagnostics ({})'.format(ndiag)
        status_print(item, '', '', indent=1)

        # list diagnostics
        for diag in self._fmap.msi:
            status_print(diag, '', '', indent=2)

    def data_discovery(self):
        """
        Prints a discovery report of the 'Raw data + config' Group.
        This includes a discovery report of digitizers and control
        devices.
        """
        # TODO: HANDLE CASES WERE _DIGITIZER_PATH AND _CONTROL_PATH ARE NOT THE SAME
        # is there a 'Raw data + config'
        data_detected = self._fmap._DIGITIZER_PATH in self._file

        # print status to screen
        item = self._fmap._DIGITIZER_PATH + '/ '
        found = 'found' if data_detected else 'missing'
        status_print(item, found, '')

        # ---- Data run Sequence                                    ----
        item = 'Data run sequence'
        found = '' \
            if self._fmap.has_data_run_sequence \
            else 'not mapped'
        status_print(item, found, '', indent=1)

        # ---- Digitizers                                           ----
        item = 'digitizers ({})'.format(len(self._fmap.digitizers))
        status_print(item, '', '', indent=1)

        # list digitizers
        for digi in self._fmap.digitizers:
            item = digi
            if digi == self._fmap.main_digitizer.device_name:
                item += ' (main)'
            status_print(item, '', '', indent=2)

        # ---- Control Devices                                      ----
        item = 'control devices ({})'.format(
            len(self._fmap.controls))
        status_print(item, '', '', indent=1)

        # list controls
        for control in self._fmap.controls:
            status_print(control, '', '', indent=2)

        # ---- Unknowns                                             ----
        item = 'Unknowns ({})'.format(len(self._fmap.unknowns))
        note = 'aka unmapped'
        status_print(item, note, '', indent=0)

        # list unknowns
        for unknown in self._fmap.unknowns:
            status_print(unknown, '', '', indent=1)

    def report_msi(self, name=None):
        """
        Prints to screen a report of detected MSI diagnostics and
        their configurations.

        :param str name: name of MSI diagnostic. If :code:`None` or
            `name` is not detected then all MSI diagnostics are printed.
        """
        # gather configs to print
        if name is None:
            configs = self._fmap.msi.values()
        elif name in self._fmap.msi:
            configs = [self._fmap.msi[name]]
        else:
            name = None
            configs = self._fmap.msi.values()

        # print heading
        title = 'MSI Diagnostic Report'
        if name is not None:
            title += ' ({} ONLY)'.format(name)
        print('\n\n' + title)
        print('^' * len(title) + '\n')

        # print msi diagnostic config
        for diag in configs:
            # print msi diag name
            status_print(diag.device_name, '', '')

            # print path to diagnostic
            item = 'path:  ' + diag.info['group path']
            status_print(item, '', '', indent=1)

            # print the configs dict
            self.report_msi_configs(diag)

    @staticmethod
    def report_msi_configs(mmap):
        """
        Report the configs for MSI diagnostic with mmap.

        :param mmap: map of MSI diagnostic
        """
        # print configs title
        status_print('configs', '', '', indent=1)

        # pretty print the configs dict
        ppconfig = pp.pformat(mmap.configs)
        for line in ppconfig.splitlines():
            status_print(line, '', '', indent=2)

    def report_digitizers(self, name=None):
        """
        Prints to screen a report of detected digitizers and their
        configurations.

        :param str name: name of digitizer. If :code:`None` or
            `name` is not detected then all digitizers are printed.
        """
        # gather configs to print
        if name is None:
            configs = self._fmap.digitizers
        elif name in self._fmap.digitizers:
            configs = [name]
        else:
            name = None
            configs = self._fmap.digitizers

        # print heading
        title = 'Digitizer Report'
        if name is not None:
            title += ' ({} ONLY)'.format(name)
        print('\n\n' + title)
        print('^' * len(title) + '\n')

        # print digitizer config
        for key in configs:
            # print digitizer name
            item = key
            if key in self._fmap.main_digitizer.info['group name']:
                item += ' (main)'
            status_print(item, '', '')

            # print adc's
            # noinspection PyProtectedMember
            item = "adc's:  "\
                   + str(self._fmap.digitizers[key]._device_adcs)
            status_print(item, '', '', indent=1)

            # print digitizer configs
            self.report_digitizer_configs(
                self._fmap.digitizers[key])

    @staticmethod
    def report_digitizer_configs(digi):
        """
        Prints to screen information about the passed digitizer
        configuration(s).

        :param digi: an instance of a single member of
            `HDFMap.digitizers`
        """
        if len(digi.configs) != 0:
            nconfigs = len(digi.configs)
            nconf_active = 0
            for key in digi.configs:
                if digi.configs[key]['active']:
                    nconf_active += 1

            item = 'Configurations Detected ({})'.format(nconfigs)
            note = '({0} active, {1} inactive)'.format(
                nconf_active, nconfigs - nconf_active)
            status_print(item, '', note, indent=1, item_found_pad=' ')

            for conf in digi.configs:
                # print configuration name
                item = conf
                found = ''
                note = 'active' if digi.configs[conf]['active'] \
                    else 'NOT active'
                status_print(item, found, note, indent=2,
                             item_found_pad=' ')

                # print active adc's
                item = "adc's (active):  "\
                       + str(digi.configs[conf]['adc'])
                status_print(item, '', '', indent=3)

                # print path for config
                item = 'path: '\
                       + digi.configs[conf]['group path']
                status_print(item, '', '', indent=3, item_found_pad=' ')

                # print adc details for configuration
                for adc in digi.configs[conf]['adc']:
                    # adc name
                    item = adc + ' adc connections'
                    status_print(item, '', '', indent=3,
                                 item_found_pad=' ')

                    # print adc header
                    line_indent = ('|   ' * 4) + '+-- '
                    line = line_indent + '(brd, [ch, ...])'
                    line = line.ljust(51)
                    line += 'bit'.ljust(5)
                    line += 'clock rate'.ljust(13)
                    line += 'nshotnum'.ljust(10)
                    line += 'nt'.ljust(10)
                    line += 'shot ave.'.ljust(11)
                    line += 'sample ave.'
                    print(line)

                    # adc connections
                    nconns = len(digi.configs[conf][adc])
                    for iconn in range(nconns):
                        conns = digi.configs[conf][adc][iconn][0:2]
                        adc_stats = digi.configs[conf][adc][iconn][2]

                        # construct and print line
                        line = line_indent + str(conns)
                        line = line.ljust(51)
                        line += str(adc_stats['bit']).ljust(5)
                        line += '{0} {1}'.format(
                            adc_stats['clock rate'][0],
                            adc_stats['clock rate'][1]).ljust(13)
                        line += str(adc_stats['nshotnum']).ljust(10)
                        line += str(adc_stats['nt']).ljust(10)
                        line += str(
                            adc_stats['shot average (software)']
                        ).ljust(11)
                        line += str(
                            adc_stats['sample average (hardware)'])
                        print(line)
        else:
            status_print('Configurations Detected (0)', '', '',
                         indent=1)

    def report_controls(self, name=None):
        """
        Prints to screen a detailed report of detected control devices
        and their configurations.

        :param str name: name of control device. If :code:`None` or
            `name` is not detected then all control devices are printed.
        """
        # gather configs to print
        if name is None:
            configs = self._fmap.controls.values()
        elif name in self._fmap.controls:
            configs = [self._fmap.controls[name]]
        else:
            name = None
            configs = self._fmap.controls.values()

        # print heading
        title = 'Control Device Report'
        if name is not None:
            title += ' ({} ONLY)'.format(name)
        print('\n\n' + title)
        print('^' * len(title) + '\n')

        # print control config
        for control in configs:
            # print control name
            status_print(control.device_name, '', '')

            # print path to control
            item = 'path:     ' + control.info['group path']
            status_print(item, '', '', indent=1)

            # print path to contype
            item = 'contype:  ' + control.contype
            status_print(item, '', '', indent=1)

            # print configurations
            self.report_control_configs(control)

    @staticmethod
    def report_control_configs(cmap):
        """
        Report the configs for control associated with cmap.

        :param cmap: map of a control device
        """
        if len(cmap.configs) != 0:
            # display number of configurations
            item = 'Configurations Detected ({})'.format(
                len(cmap.configs))
            status_print(item, '', '', indent=1)

            # display config values
            for config_name, config in cmap.configs.items():
                # print config_name
                status_print(config_name, '', '', indent=2)

                # get pretty print string
                ppconfig = pp.pformat(config)
                for line in ppconfig.splitlines():
                    status_print(line, '', '', indent=3)

        else:
            item = 'Configurations Detected (0)'
            status_print(item, '', '', indent=1)


def status_print(item, found, note, indent=0,
                 item_found_pad=' ', found_tab=55):
    """
    Stylistic status printing for :py:class:`HDFOverview`

    :param item: `str` for item (1st) column
    :param found: `str` for found (2nd) column
    :param note: `str` for note (3rd) column
    :param indent: `int` num. of indentations for `item` display
    :param item_found_pad: `str` pad style between `item` and `found`
    """
    note_tab = 7

    if indent == 0:
        str_print = ''
    elif indent == 1:
        str_print = '+-- '
    else:
        str_print = ('|   ' * (indent - 1)) + '+-- '
    str_print += str(item) + ' '
    str_print = str_print.ljust(found_tab - 1, item_found_pad) + ' '
    str_print += str(found).ljust(note_tab) + str(note)

    print(str_print)
