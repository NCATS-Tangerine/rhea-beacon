from setuptools import setup

setup(
    name = 'Beacon Controller',
    packages = ['controller'],
    include_package_data=True,
    install_requires=['pandas']
)
