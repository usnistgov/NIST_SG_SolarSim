import os
import sys

try:
    from setuptools import setup, find_namespace_packages
    from setuptools.extension import Extension
except ImportError:
    raise RuntimeError('setuptools is required')

DISTNAME = 'sg_solarsim'
LICENSE = 'NIST'
AUTHOR = 'Allen Goldstein'
MAINTAINER_EMAIL = 'allen.goldstein@ieee.org'

INSTALL_REQUIRES = ['pvlib',
                    'pysimplegui >=  4.60.0',
                    'tk',
                    'datetime',
                    'pytz',
                    'timezonefinder',
                    'matplotlib',
                    'importlib-metadata; python_version < "3.8"']

PACKAGES = find_namespace_packages(include=['sg_solarsim*'])
PACKAGE_DATA={'' : ['*.PNG','*.csv']}

setuptools_kwargs = {
    'zip_safe': False,
    'scripts': [],
    'include_package_data': True,
    'python_requires': '>=3.7'
}

extensions = []

setup(name=DISTNAME,
      version='0.2.1',
      packages=PACKAGES,
      package_data=PACKAGE_DATA,
      install_requires=INSTALL_REQUIRES,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      **setuptools_kwargs)
