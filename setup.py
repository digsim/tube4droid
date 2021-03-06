#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from distutils.command.install_data import install_data
from pip.req import parse_requirements


cmdclass = {'install_data': install_data}
data_files = [('/etc/Tube4Droid/', ['etc/tube4droid.conf', 'etc/logging.conf']), ('/usr/local/etc/bash_completion.d/', ['etc/tube4droid-completion.bash'])]
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]



# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="tube4droid",
    version='1.6.dev1',
    author="Andreas Ruppen",
    author_email="andreas.ruppen@gmail.com",
    description="Creates an RSS feed from a youtoube playlist",
    license="Apache",
    keywords="youtube, iTunes, RSS, podcast",
    url="https://github.com/digsim/missingTvShows",
    packages=find_packages(exclude=['contrib', 'docs', '*.tests*']),
    entry_points={
        'console_scripts': [
            'tube4droid=tube4droid.main:main',
        ],
    },
    cmdclass=cmdclass,
    #data_files=data_files,
    #package_data = {'etc':'**/*'},
    include_package_data = True,
    install_requires=reqs,
    test_suite='nose.collector',
    tests_require=['nose'],
    dependency_links=["git+https://github.com/svpino/rfeed.git#egg=rfeed"],
    long_description=read('README.md'),
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    platforms='any',
)
