import setuptools
from distutils.core import setup
from Cython.Build import cythonize
import numpy
#import sys
#import os

#ys.path.append(os.path.dirname(__file__))

setup(name='pbgerecolor',
      include_dirs=[numpy.get_include()],
      ext_modules=cythonize("pbgerecolor.pyx"))
