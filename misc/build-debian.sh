#!/bin/bash
which dpkg >/dev/null 2>&1
if [ $? = 0 ]; then
	if [ -e "./debian/" ]; then
		rm -rf ./debian/
	fi
	mkdir -p ./debian/DEBIAN/
	mkdir -p ./debian/opt/remasterscript/{bin,share}
	mkdir -p ./debian/usr/bin
	cp -rp ./src/* debian/opt/remasterscript/share/
	cp ./misc/debian.control ./debian/DEBIAN/control
	cp ./misc/remaster-create ./debian/usr/bin/
	cp ./misc/remaster-build ./debian/usr/bin/
	dpkg -b debian/ remasterscript.deb
else
	echo "You have to install dpkg..."
fi
