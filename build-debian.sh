#!/bin/bash
mkdir -p debian/usr/share/remasterscript/
cp -rp src/remasterscript/ src/remaster.py debian/usr/share/remasterscript/
dpkg -b debian/ remasterscript.deb

