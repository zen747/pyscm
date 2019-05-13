#!/usr/bin/env python3
import sys

from setuptools import find_packages, setup


# Get version without importing, which avoids dependency issues

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='py-scm',
      version='1.0.1',
      description='A python state machine framework based on statecharts (scxml)',
      long_description=readme(),
      author='Zen Chien',
      author_email='jixing.jian@gmail.com',
      url='https://github.com/zen747/pyscm',
      license="Apache License 2.0",
      keywords=['statecharts', 'state-machine', 'scxml', 'david-harel'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache Software License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Topic :: Text Processing :: Linguistic"],
      packages=find_packages(),
      python_requires=">=3.6")
