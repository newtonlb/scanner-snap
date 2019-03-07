
from setuptools import setup, find_packages
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
    py_modules=['scanner', 'GPS_class', 'requester'],
    install_requires=[
      'pybluez','termcolor','xlrd', 'pyserial', 'bluepy', 'requests'],
    entry_points={
        'console_scripts': [
            'scanner = scanner:main',
        ],
    }

)
