import sys
from cx_Freeze import setup, Executable
from Cython.Build import cythonize
from main import VERSION
import numpy

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "numpy"],
                     "include_files": ["data","design","image","music","credits.md","history.txt","LICENSE","README.md"],
                     "include_msvcr": True,}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "ghcaramel",
        version = VERSION,
        description = "My GUI application!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)],
        )

"""
from setuptools import setup, find_packages
import numpy

setup(  name='ghcaramel',
        version=VERSION,
        py_modules=['main',],
        packages=find_packages(),
        include_package_data = True,
        package_data={
            '': ['*.txt','*.png','*.cfg','*.ttf','data/*.txt','data/*.cfg','data/*.json'],
            'data': ['*.txt','*.cfg','*.json'],
            'image': ['*.png','*.ttf','*.otf'],
            'design': ['*.txt',],
            'music': ['*.ogg',],

        },
        entry_points={
            'gui_scripts': [
                'ghcaramel = main:play_the_game',
            ]
        },
        install_requires= [
            'Pygame','numpy'
        ],
        ext_modules=cythonize("caramel-recolor-cython/pbgerecolor.pyx"),
        include_dirs=[numpy.get_include()],
      )
"""