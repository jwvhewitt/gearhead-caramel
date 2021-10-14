
cd /src/caramel-recolor-cython
python3 setup.py install

#cxfreeze -c main.py --target-dir dist/ghcaramel --include-files=data,design,image,music,credits.md,history.txt,LICENSE,README.md -s --target-name=ghcaramel --packages=pygame,numpy,pbgerecolor
pyinstaller --clean --specpath /src/ --distpath /util/build --workpath /opt/bk/build /src/ghcaramel_linux.spec
