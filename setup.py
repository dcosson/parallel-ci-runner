#!/usr/bin/env python

from setuptools import setup

setup(
    name='parallel-ci-runner',
    version='0.1.6',
    description='A framework for defining and running parallel CI tests, '
                'with support for docker-compose.',
    author='Danny Cosson',
    author_email='dcosson@gmail.com',
    url='https://github.com/dcosson/parallel-ci-runner',
    license='MIT',
    packages=['parallel_ci_runner'],
)
