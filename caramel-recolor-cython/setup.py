from distutils.core import setup
from Cython.Build import cythonize

setup(name='pbgerecolor',
      ext_modules=cythonize("pbgerecolor.pyx"))
