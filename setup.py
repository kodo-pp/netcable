#!/usr/bin/env python
from setuptools import setup


setup(
    name = 'netcable',
    version = '1.0.0',
    author = 'kodopp',
    packages = ['netcable'],
    entry_points = {
        'console_scripts': [
            'patchcord = netcable.netcable:patchcord',
            'tcp-forward = netcable.netcable:tcp_forward',
            #'echo-server = netcable.netcable:echo_server',
        ],
    },
)
