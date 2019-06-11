#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-11
# @Author  : hongshu

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='skyun',
    version='1.1.1',
    license='MIT',
    description='A socks5 proxy software',
    url='https://github.com/comeacrossyun/skyun',
    long_description=long_description,
    author='Yuyun Liu (cayun/comeacrossyun)',
    author_email='comeacrossyun@gmail.com',
    python_requires='>=3.6.0',
    install_requires=[],
    entry_points="""
    [console_scripts]
    skyserver = skyun.server:main
    skyclient = skyun.client:main
    """,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['skyun']
)
