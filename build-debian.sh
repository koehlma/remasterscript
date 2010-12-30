#!/bin/bash
cp -rp remasterscript remaster.py debian/usr/share/remasterscript/
dpkg -b ./debian remasterscript.deb

