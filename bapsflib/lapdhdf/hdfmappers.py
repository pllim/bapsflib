# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#
import h5py


def get_hdfMap(hdf_version, hdf_file):
    """
        Function to simulate a Class with dynamic inheritance.  An
        instance of the hdfMap class is returned.  The superclass
        inheritance of hdfMap is determined by the param hdf_version.

        :param hdf_file:
        :param hdf_version:
        :return:
    """
    known_hdf_version = {'1.1': hdfMap_LaPD_1dot1,
                         '1.2': hdfMap_LaPD_1dot2}

    if hdf_version in known_hdf_version.keys():
        class hdfMap(known_hdf_version[hdf_version]):
            """
                Contains the mapping relations for a given LaPD
                generated HDF5 file.
            """

            def __init__(self, hdf_obj):
                super(hdfMap, self).__init__(hdf_obj)

        hdf_mapping = hdfMap(hdf_file)
        return hdf_mapping
    else:
        print('Mapping of HDF5 file is not known.\n')


class hdfMapTemplate(object):
    """
        Required constants
            hdf_version = ''
            msi_diagnostic_goups = []
            sis_group = ''
            sis_crates = []
            data_configs = {}
    """
    msi_group = 'MSI'
    data_group = 'Raw data + config'

    def __init__(self):
        self.hdf_version = ''
        self.msi_diagnostic_groups = []
        self.sis_group = ''
        self.sis_crates = []
        self.data_configs = {}

    def sis_path(self):
        return self.data_group + '/' + self.sis_group


class hdfMap_LaPD_1dot1(hdfMapTemplate):
    def __init__(self, hdf_obj):
        hdfMapTemplate.__init__(self)

        self.hdf_version = '1.1'
        self.msi_diagnostic_groups.extend(['Discharge', 'Gas pressure',
                                           'Heater',
                                           'Interferometer array',
                                           'Magnetic field'])
        self.sis_group = 'SIS 3301'
        self.sis_crates.extend(['SIS 3301'])

        # Gather and build data configurations if sis_group exists
        dgroup = hdf_obj.get(self.sis_path())
        if dgroup is not None:
            self.build_data_configs(dgroup)

    def build_data_configs(self, group):
        """
            Builds self.data_configs dictionary. A dict. entry follows:

            data_configs[config_name] = {
                'active': True/False,
                'crates: [list of active SIS crates],
                'group name': 'name of config group',
                'group path': 'absolute path to config group',
                'SIS 3301': {'bit': 14,
                             'sample rate': (100.0, 'MHz'),
                             'connections': [(br, [ch,]), ]}}

            :param group:
            :return:
        """
        # collect sis_group's dataset names and sub-group names
        subgroup_names = []
        dataset_names = []
        for key in group.keys():
            if isinstance(group[key], h5py.Dataset):
                dataset_names.append(key)
            if isinstance(group[key], h5py.Group):
                subgroup_names.append(key)

        # populate self.data_configs
        for name in subgroup_names:
            is_config, config_name = self.parse_config_name(name)
            if is_config:
                # initialize configuration name in the config dict
                self.data_configs[config_name] = {}

                # determine if config is active
                self.data_configs[config_name]['active'] = \
                    self.is_config_active(config_name, dataset_names)

                # assign active crates to the configuration
                self.data_configs[config_name]['crates'] = \
                    self.sis_crates

                # add 'group name'
                self.data_configs[config_name]['group name'] = name

                # add 'group path'
                self.data_configs[config_name]['group path'] = \
                    group.name

                # add SIS info
                self.data_configs[config_name]['SIS 3301'] = \
                    self.__crate_info('SIS 3301', group[name])

    @staticmethod
    def parse_config_name(name):
        """
            Parses 'name' to see if it matches the naming scheme for a
            data configuration group.  A group representing a data
            configuration has the scheme:

                Configuration: config_name

            :param name:
            :return:
        """
        split_name = name.split()
        is_config = True if split_name[0] == 'Configuration:' else False
        config_name = ' '.join(split_name[1::]) if is_config else None
        return is_config, config_name

    @staticmethod
    def is_config_active(config_name, dataset_names):
        """
            The naming of a dataset starts with the name of its
            corresponding configuration.  This scans 'dataset_names'
            fo see if 'config_name' is used in the list of datasets.

            :param config_name:
            :param dataset_names:
            :return:
        """
        active = False

        for name in dataset_names:
            if config_name in name:
                active = True
                break

        return active

    def __crate_info(self, crate_name, config_group):
        # LaPD v1.1 only has crate 'SIS 3301'
        crate_info = {'bit': 14,
                      'sample rate': (100, 'MHz'),
                      'connections': self.__find_crate_connections(
                          crate_name, config_group)}
        return crate_info

    @staticmethod
    def __find_crate_connections(crate_name, config_group):
        conn = []
        brd = None
        chs = []
        for ibrd, board in enumerate(config_group.keys()):
            brd_group = config_group[board]
            for ich, ch_key in enumerate(brd_group.keys()):
                ch_group = brd_group[ch_key]

                if ich == 0:
                    brd = ch_group.attrs['Board']
                    chs = [ch_group.attrs['Channel']]
                else:
                    chs.append(ch_group.attrs['Channel'])

            subconn = (brd, chs)
            if ibrd == 0:
                conn = [subconn]
            else:
                conn.append(subconn)

        return conn

    def parse_dataset_name(self, name):
        pass


class hdfMap_LaPD_1dot2(hdfMapTemplate):
    def __init__(self, hdf_obj):
        hdfMapTemplate.__init__(self)

        self.hdf_version = '1.2'
        self.msi_diagnostic_groups.extend(['Discharge', 'Gas pressure',
                                           'Heater',
                                           'Interferometer array',
                                           'Magnetic field'])
        self.sis_group = 'SIS crate'
        self.sis_crates.extend(['SIS 3302', 'SIS 3305'])

        # Gather and build data configurations if sis_group exists
        dgroup = hdf_obj.get(self.sis_path())
        if dgroup is not None:
            self.build_data_configs(dgroup)

    def build_data_configs(self, group):
        """
            Builds self.data_configs dictionary. A dict. entry follows:

            data_configs[config_name] = {
                'active': True/False,
                'crates: [list of active SIS crates],
                'group name': 'name of config group',
                'group path': 'absolute path to config group',
                'SIS 3301': {'bit': 14,
                             'sample rate': (100.0, 'MHz'),
                             'connections': [(br, [ch,]), ]}}

            :param group:
            :return:
        """
        # collect sis_group's dataset names and sub-group names
        subgroup_names = []
        dataset_names = []
        for key in group.keys():
            if isinstance(group[key], h5py.Dataset):
                dataset_names.append(key)
            if isinstance(group[key], h5py.Group):
                subgroup_names.append(key)

        # populate self.data_configs
        for name in subgroup_names:
            is_config, config_name = self.parse_config_name(name)
            if is_config:
                # initialize configuration name in the config dict
                self.data_configs[config_name] = {}

                # determine if config is active
                self.data_configs[config_name]['active'] = \
                    self.is_config_active(config_name, dataset_names)

                # assign active crates to the configuration
                self.data_configs[config_name]['crates'] = \
                    self.__config_crates(group[name])

                # add 'group name'
                self.data_configs[config_name]['group name'] = name

                # add 'group path'
                self.data_configs[config_name]['group path'] = \
                    group.name

                # add SIS info
                for crate in self.data_configs[config_name]['crates']:
                    self.data_configs[config_name][crate] = \
                        self.__crate_info(crate, group[name])

    @staticmethod
    def parse_config_name(name):
        """
            Parses 'name' to see if it matches the naming scheme for a
            data configuration group.  A group representing a data
            configuration has the scheme:

                config_name

            :param name:
            :return:
        """
        return True, name

    @staticmethod
    def is_config_active(config_name, dataset_names):
        """
            The naming of a dataset starts with the name of its
            corresponding configuration.  This scans 'dataset_names'
            fo see if 'config_name' is used in the list of datasets.

            :param config_name:
            :param dataset_names:
            :return:
        """
        active = False

        for name in dataset_names:
            if config_name in name:
                active = True
            break

        return active

    @staticmethod
    def __config_crates(group):
        active_crates = []
        crate_types = list(group.attrs['SIS crate board types'])
        if 2 in crate_types:
            active_crates.append('SIS 3302')
        if 3 in crate_types:
            active_crates.append('SIS 3305')

        return active_crates

    def __crate_info(self, crate_name, config_group):
        # LaPD v1.2 has two DAQ crates, SIS 3302 and SIS 3305
        crate_info = {'bit': None,
                      'sample rate': (None, 'MHz'),
                      'connections': None}

        # info for SIS 3302
        if crate_name == 'SIS 3302':
            crate_info['bit'] = 16
            crate_info['sample rate'] = (100.0, 'MHz')
            crate_info['connections'] = \
                self.__find_crate_connections('SIS 3302', config_group)
        elif crate_name == 'SIS 3305':
            crate_info['bit'] = 10
            crate_info['connections'] = \
                self.__find_crate_connections('SIS 3305', config_group)

        return crate_info

    @staticmethod
    def __find_crate_connections(crate_name, config_group):
        conn = []
        brd = None
        chs = []

        return conn
