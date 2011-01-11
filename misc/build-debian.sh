#!/bin/bash
mkdir -p debian/usr/share/remasterscript/
mkdir -p debian/usr/share/pixmaps/
cp -rp src/remasterscript/ src/remaster.py debian/usr/share/remasterscript/
cp icon/icon.png debian/usr/share/pixmaps/remasterscript.png
dpkg -b debian/ remasterscript.deb