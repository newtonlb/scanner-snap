
from setuptools import setup, find_packages
from os import path
setup(
    name='scanner',
    version='',
    url='',
    license='',
    author='newton',
    author_email='',
    description='',
    packages=find_packages(),
install_requires=[
      'pybluez','termcolor','xlrd','numpy','pandas'],
    entry_points={
        'console_scripts': [
            'scanner = scanner:main',
        ],
    }

)
