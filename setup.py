from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(  name='ghcaramel',
        version='0.100',
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
      )
