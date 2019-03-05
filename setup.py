
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
    py_modules=['scanner'],
install_requires=[
      'pybluez','termcolor','xlrd','numpy','pandas'],
    entry_points={
        'console_scripts': [
            'scanner = scanner.scanner:main',
        ],
    }

)
