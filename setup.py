#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='epuck',
    version='0.9.1',
    description='Controlling e-puck robot',
    long_description="""Library for controlling e-puck robot (http://www.e-puck.org).""",
    author='David Marek',
    author_email='davidm@atrey.karlin.mff.cuni.cz',
    url='http://e-puck.davidmarek.cz/',
    platforms=['POSIX'],
    download_url='http://atrey.karlin.mff.cuni.cz/~davidm/epuck-0.9.1.tar.gz',
    license='LGPL',
    install_requires=['pyserial'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Natural Language :: Czech',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering'
    ],
    packages=['epuck', 'epuck.comm'],
    )
