
from setuptools import setup, find_packages
from os import path
setup(
    name='scanner-snap',
    version='',
    url='',
    license='',
    author='newton',
    author_email='',
    description='',
    packages=find_packages(),
install_requires=[
      'pybluez','termcolor','bluepy','xlrd','numpy','pandas'],
    entry_points={
        'console_scripts': [
            'scanner-snap = Scanner:main',
        ],
    }

)
