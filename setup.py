#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# -*- Requirements -*-
_setup_requires = ["setuptools>=19.1"]


def setup_requires():
    needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
    if needs_pytest:
        return _setup_requires + ["pytest-runner==4.2"]
    return _setup_requires


def _strip_comments(l):
    return l.split("#", 1)[0].strip()


def _pip_requirement(req):
    if req.startswith("-i "):
        return []
    if req.startswith("-r "):
        _, path = req.split()
        return reqs(*path.split("/"))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r)
        for r in (
            _strip_comments(l)
            for l in open(os.path.join(os.getcwd(), *f)).readlines()
        )
        if r
    ]


def reqs(*f):
    """Parse requirement file.
    Example:
        reqs('default.txt')          # requirements.txt
        reqs('extras', 'redis.txt')  # extras/redis.txt
    Returns:
        List[str]: list of requirements specified in the file.
    """
    return [req for subreq in _reqs(*f) for req in subreq]


def install_requires():
    """Get list of requirements required for installation."""
    return reqs("requirements.txt")


def tests_require():
    """Get list of requirements required for testing."""
    return reqs("test-requirements.txt")


def console_scripts():
    return [
        "lucky_call = lucky_call.main:main",
    ]


setup_params = dict(
    name="lucky-call",
    version='0.0.1',
    summary="Lucky call radio server simulator",
    author="Francesco Ciaccia",
    author_email="",
    entry_points={"console_scripts": console_scripts()},
    setup_requires=setup_requires(),
    install_requires=install_requires(),
    tests_require=tests_require(),
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.5",
    zip_safe=False,
)


def main():
    """Invoke installation process using setuptools."""
    setup(**setup_params)


if __name__ == "__main__":
    main()
