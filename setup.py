from setuptools import setup

setup(
    name="rhea-beacon",
    url="https://github.com/NCATS-Tangerine/rhea-beacon",
    version = "1.3.1",
    packages = [
        'beacon_controller',
        'beacon_controller.controllers',
        'beacon_controller.providers',
        'config',
        'data'
    ],
    include_package_data=True,
    install_requires=[
        'bmt',
        'biolinkml',
        'tornado',
        'requests',
        'flask',
        'pyyaml',
        'connexion == 1.1.15',
        'python_dateutil == 2.6.1',
        'setuptools >= 21.0.0',
        'pandas',
        'bmt',
    ]
)
