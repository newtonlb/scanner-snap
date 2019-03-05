
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
    py_modules=['scanner', 'GPS_class'],
install_requires=[
      'pybluez','termcolor','xlrd','numpy','pandas', 'pyserial'],
    entry_points={
        'console_scripts': [
            'scanner = scanner.scanner:main',
        ],
    }

)
