
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
    python_requires='>=3.5',
    py_modules=['scanner', 'GPS_class'],
    install_requires=[
      'pybluez','termcolor','xlrd','numpy','pandas', 'pyserial', 'bluepy'],
    entry_points={
        'console_scripts': [
            'scanner = scanner:main',
        ],
    }

)
