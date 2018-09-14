from setuptools import setup

setup(
    name='Beacon Controller',
    packages=['controller', 'controller.controllers', 'controller.providers'],
    include_package_data=True,
    install_requires=[
        'pandas',
        'pyyaml'
    ]
)
