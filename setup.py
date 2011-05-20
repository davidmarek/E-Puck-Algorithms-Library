#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='epuck',
    version='1.0',
    description='Controlling e-puck robot',
    long_description="""Library for controlling e-puck robot (http://www.e-puck.org).""",
    author='David Marek',
    author_email='davidm@atrey.karlin.mff.cuni.cz',
    url='http://e-puck.davidmarek.cz/',
    platforms=['POSIX'],
    license='LGPL',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering'
    ],
    packages=['epuck', 'epuck.comm'],
    )
