#!/bin/bash
which dpkg >/dev/null 2>&1
if [ $? = 0 ]; then
	if [ -e "./debian/" ]; then
		rm -rf ./debian/
	fi
	mkdir -p ./debian/DEBIAN/
	mkdir -p ./debian/opt/remasterscript/{bin,share}
	mkdir -p ./debian/usr/share/{pixmaps,applications}/
	mkdir -p ./debian/usr/bin
	cp -rp ./src/* debian/opt/remasterscript/share/
	cp ./icon/icon.png ./debian/usr/share/pixmaps/remasterscript.png
	cp ./misc/remasterscript.desktop ./debian/usr/share/applications
	cp ./misc/extract_compressed_fs.static ./debian/opt/remasterscript/bin/extract_compressed_fs
	cp ./misc/create_compressed_fs.static ./debian/opt/remasterscript/bin/create_compressed_fs
	cp ./misc/debian.control ./debian/DEBIAN/control
	cp ./misc/remasterscript ./debian/usr/bin/
	dpkg -b debian/ remasterscript.deb
else
	echo "You have to install dpkg..."
fi
