#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from buildqt import BuildQt

cmdclass = {}
cmdclass['build_qt'] = BuildQt

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    'PySide',
    'twisted',
    'xerox',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='splash',
    version='0.1.0',
    description='Splash your data across your mates.',
    long_description=readme + '\n\n' + history,
    author='Ivan Bienco, Tomas Touceda',
    author_email='ivanalejandro0@gmail.com, chiiph@gmail.com',
    url='https://github.com/chiiph/splash',
    packages=[
        'splash',
    ],
    package_dir={'splash':
                 'splash'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='splash',
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
