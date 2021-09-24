# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.osext as osext


@rfm.simple_test
class TensorFlow2HorovodTest(rfm.RunOnlyRegressionTest):
    variant = parameter(['small', 'large'])

    def __init__(self):
        self.descr = 'Distributed training with TensorFlow2 and Horovod'

        self.valid_systems = ['kebnekaise:gpu_%s' % x for x in ['2xK80', '4xK80', '2xV100']]
        self.valid_systems += ['alvis:%s' % x for x in ['8xT4', '2xV100', '4xV100', '4xA100']]
        self.valid_systems += ['daint:gpu']

        self.kebnekaise_single_socket = ['kebnekaise:gpu_%s' % x for x in ['1xK80', '1xV100']]

        self.valid_prog_environs = ['builtin', 'fosscuda']

        cs = self.current_system.name

        if cs == 'kebnekaise' or cs == 'alvis':
            self.modules = ['fosscuda/2019b', 'Horovod/0.19.1-TensorFlow-2.1.0-Python-3.7.4']
            if cs == 'kebnekaise':
                self.IB_ifc = 'mlx5_0'
            else:
                self.IB_ifc = 'mlx5_2'
        # FIXME: The following will not be needed after the Daint upgrade
        elif cs == 'dom':
            self.IB_ifc = 'ipogif0'
            self.modules = [
                f'Horovod/0.21.0-CrayGNU-{osext.cray_cdt_version()}-tf-2.4.0'
            ]
        else:
            self.IB_ifc = 'ipogif0'
            self.modules = ['Horovod/0.19.1-CrayGNU-20.08-tf-2.2.0']

        # Settings for various systems. num_tasks is per-variant
        self.tasks_cpu_settings = {
            'alvis:2xV100': {
                'num_cpus_per_task': 8,
                'num_tasks_per_node': 2,
                'num_tasks': {'small': 2},
            },
            'alvis:4xV100': {
                'num_cpus_per_task': 8,
                'num_tasks_per_node': 4,
                'num_tasks': {'small': 4},
            },
            'alvis:8xT4': {
                'num_cpus_per_task': 4,
                'num_tasks_per_node': 8,
                'num_tasks': {'small': 8},
            },
            'alvis:4xA100': {
                'num_cpus_per_task': 8,
                'num_tasks_per_node': 4,
                'num_tasks': {'small': 4},
            },
            'kebnekaise:gpu_1xK80': {
                'num_cpus_per_task': 7,
                'num_tasks_per_node': 2,
                'num_tasks': {'small': 2},
            },
            'kebnekaise:gpu_2xK80': {
                'num_cpus_per_task': 7,
                'num_tasks_per_node': 4,
                'num_tasks': {'small': 4, 'large': 8},
            },
            'kebnekaise:gpu_4xK80': {
                'num_cpus_per_task': 7,
                'num_tasks_per_node': 8,
                'num_tasks': {'small': 8, 'large': 32},
            },
            'kebnekaise:gpu_1xV100': {
                'num_cpus_per_task': 14,
                'num_tasks_per_node': 1,
                'num_tasks': {'small': 1},
            },
            'kebnekaise:gpu_2xV100': {
                'num_cpus_per_task': 14,
                'num_tasks_per_node': 2,
                'num_tasks': {'small': 2, 'large': 4},
            },
            'default': {
                'num_cpus_per_task': 12,
                'num_tasks_per_node': 1,
                'num_tasks': {'small': 8, 'large': 32},
            },
        }

        self.sourcesdir = None

        if self.variant == 'small':
            self.valid_systems += ['dom:gpu'] + self.kebnekaise_single_socket
            self.reference = {
                'kebnekaise:gpu_1xK80': {
                    'throughput': (124, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (62.4, -0.05, None, 'images/s'),
                },
                'kebnekaise:gpu_2xK80': {
                    'throughput': (249, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (62.4, -0.05, None, 'images/s'),
                },
                'kebnekaise:gpu_4xK80': {
                    'throughput': (494, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (62.4, -0.05, None, 'images/s'),
                },
                'kebnekaise:gpu_1xV100': {
                    'throughput': (439, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (439, -0.05, None, 'images/s'),
                },
                'kebnekaise:gpu_2xV100': {
                    'throughput': (832, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (416, -0.05, None, 'images/s'),
                },
                'dom:gpu': {
                    'throughput': (1712, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (214, -0.05, None, 'images/s'),
                },
                'daint:gpu': {
                    'throughput': (1712, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (214, -0.05, None, 'images/s')
                },
            }
        else:
            self.reference = {
                'kebnekaise:gpu_2xK80': {
                    'throughput': (493, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (61.6, -0.05, None, 'images/s')
                },
                'daint:gpu': {
                    'throughput': (6848, -0.05, None, 'images/s'),
                    'throughput_per_gpu': (214, -0.05, None, 'images/s')
                },
            }

        model = 'InceptionV3'
        batch_size = 64
        self.sanity_patterns = sn.all([
            sn.assert_found(rf'Model: {model}', self.stdout),
            sn.assert_found(rf'Batch size: {batch_size}', self.stdout)
        ])
        self.variables = {
            'NCCL_DEBUG': 'INFO',
            'NCCL_IB_HCA': self.IB_ifc,
            'NCCL_IB_CUDA_SUPPORT': '1',
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            'OMPI_MCA_mpi_warn_on_fork': '0',
        }
        script = 'tensorflow2_synthetic_benchmark.py'
        self.prerun_cmds = ['wget https://raw.githubusercontent.com/horovod/'
                            'horovod/842d1075e8440f15e84364f494645c28bf20c3ae/'
                            'examples/tensorflow2_synthetic_benchmark.py',
                            'sed -i "s/weights=None/weights=None, '
                            f'input_shape=(224, 224, 3)/g" {script}']
        self.executable = 'python'
        self.executable_opts = [
            f'{script}',
            f'--model {model}',
            f'--batch-size {batch_size}',
            '--num-iters 5',
            '--num-batches-per-iter 5',
            '--num-warmup-batches 5',
        ]
        self.tags = {'production'}
        self.maintainers = ['RS', 'TR', 'AS']

    @run_before('run')
    def set_run_params(self):
        cs = self.current_system.name
        cp = self.current_partition.fullname
        cn = self.current_partition.name

        self.num_tasks_per_node = self.tasks_cpu_settings.get(cp, 'default')['num_tasks_per_node']
        self.num_cpus_per_task = self.tasks_cpu_settings.get(cp, 'default')['num_cpus_per_task']
        self.num_tasks = self.tasks_cpu_settings.get(cp, 'default')['num_tasks'][self.variant]

        self.perf_patterns = {
            'throughput': sn.extractsingle(
                rf'Total img/sec on {self.num_tasks} GPU\(s\): '
                rf'(?P<throughput>\S+) \S+',
                self.stdout, 'throughput', float),
            'throughput_per_gpu': sn.extractsingle(
                r'Img/sec per GPU: (?P<throughput_per_gpu>\S+) \S+',
                self.stdout, 'throughput_per_gpu', float)
        }

