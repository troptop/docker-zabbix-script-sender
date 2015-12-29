#!/usr/bin/env python
import os
import sys
from setuptools import setup
from textwrap import dedent

NAME = "docker-zabbix-script-sender"
GITHUB_ORG_URL = ""
ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

exec(open('docker_zabbix_script_sender/version.py').read())

setup(
    name=NAME,
    version=version,
    author="Cyril Moreau",
    author_email="cyril.moreauu@gmail.com",
    url= GITHUB_ORG_URL + '/' + NAME,
    download_url="{0}/{1}/tarball/v{2}".format(GITHUB_ORG_URL, NAME, version),
    description="Push Docker containers script results to Zabbix efficiently",
    long_description=dedent("""
        Rationale
        ---------
        Docker Zabbix Sender delivers a daemon script that push to Zabbix statistics about Docker containers.

        It leverages 3 interesting components:

        - Zabbix maintains a tool titled ``zabbix-sender``.
          It is meant to push `Zabbix trapper items`_ efficiently.

	- Develop your own scripts to monitor your docker container

        - Docker 1.5.0 comes with Docker Remote API version 17, providing a new `stats endpoint`_.
          It allows the client to subscribe to a live feed delivering a container statistics.

        The daemon script stands in the middle of those 3 components.
        It collects Docker containers statistics and transforms them in Zabbix trapper events.

        Published metrics
        -----------------
        The daemon script does not publish any statistic yet.
	You have to develop your own script

        Documentation
        -------------
        The stable documentation is available on ReadTheDocs_

    """),
    keywords="docker zabbix monitoring",
    packages=['docker_zabbix_script_sender'],
    install_requires=[
        'docker-py >= 1.0.0',
    ],
    zip_safe=False,
    license="Apache license version 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points = """
        [console_scripts]
        docker-zabbix-script-sender = docker_zabbix_script_sender.zabbix_sender:run
    """
)
