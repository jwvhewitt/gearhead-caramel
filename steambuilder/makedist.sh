#!/bin/bash

# Move and rename everything for a new release.
# Stick all the zip files into dist, then run "makedist {version}"

rm -rf ghcaramel

mv ghcaramel_steam.zip ghcaramel-$1-steamos.zip
mv ghclinux.zip ghcaramel-$1-linux.zip
mv ghcmac.zip ghcaramel-$1-macos.zip

unzip ghcwin.zip
mv exe.win-amd64-3.8 ghcaramel
mv ghcaramel/main.exe ghcaramel/ghcaramel.exe

zip -r ghcaramel-$1-windows.zip ghcaramel
cd ghcaramel
zip -r ghcaramel-$1-steamwin.zip *
mv ghcaramel-$1-steamwin.zip ..
cd ..
rm ghcwin.zip



