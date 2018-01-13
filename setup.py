#!/usr/bin/env python

from distutils.core import setup

setup(name="turbofloat",
      version="4.1.0",
      description="Python bindings for TurboFloat",
      url="https://github.com/Jude188/python-turbofloat/",
      author="Judah Rand",
      author_email="JudahRand@obe.tv",
      maintainer="Judah Rand",
      maintainer_email="JudahRand@gmail.tv",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      packages=["turbofloat"],
      long_description=open("README.rst").read()
)
