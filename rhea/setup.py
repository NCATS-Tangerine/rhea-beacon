from setuptools import setup

setup(
    name = "rhea",
    version = "1.0",
    author = "lance@starinformatics.com",
    description = "Implementation of the controller classes of the Rhea beacon",
    packages = ['rhea'],
    # data_files=[
    #     ('docs', [
    #         'docs/chebiId_name.tsv',
    #         'docs/rhea-relationships.tsv',
    #         ]
    #     )
    #     # ('config', 'config.yml')
    # ],
    include_package_data=True,
    install_requires=['pandas==0.23.4']
)
