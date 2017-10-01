from setuptools import setup

import core.App

setup(
    name='Robot',
    version=core.__version__,
    install_requires=['pymata-aio']
)
