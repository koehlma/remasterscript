#!/bin/bash
mkdir -p debian/usr/share/remasterscript/
cp -rp remasterscript remaster.py debian/usr/share/remasterscript/
dpkg -b ./debian remasterscript.deb

