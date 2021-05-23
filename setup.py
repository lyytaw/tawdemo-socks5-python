#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-11
# @Author  : hongshu

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tawdemo-socks5-python',
    version='1.0.0',
    license='MIT',
    description='A socks5 proxy software',
    url='https://github.com/lyytaw/tawdemo-socks5-python',
    long_description=long_description,
    author='lyytaw',
    author_email='lyytaw@gmail.com',
    python_requires='>=3.6.0',
    install_requires=[],
    entry_points="""
    [console_scripts]
    tawsocks-server = tawsocks.server:main
    tawsocks-client = tawsocks.client:main
    """,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['tawsocks']
)
