Knoppix-Remaster-Skript
=======================

Installation
------------
Für Debian gibt es ein [Paket](https://github.com/downloads/koehlma/remasterscript/remasterscript.deb).
Fur alle anderen Distributionen müssen folgende Schritte ausgeführt werden.
* Installation von `create_compressed_fs` und `extract_compressed_fs`
    * Installieren der [zlib](http://zlib.net/) inklusive der Header, die zur Entwicklung nötig sind
    * Kompilieren der Programme durch ausführen von `build.sh` im Verzeichnis `cloop`
    * Aus dem Verzeichnis `cloop` `create_compressed_fs` und `extract_compressed_fs` nach `/opt/knoppix/bin` kopieren
* Installation der Abhängigkeiten
    * zlib
    * qemu
    * XTerm oder GNOME-Terminal
    * bash
    * mkisofs
    * mount, umount
    * cp, rm
    * find
    * sed
    * chroot
    * Python >= 2.5
    * PyGTK >= 2

Benutzung
---------
Beim Debian-Paket über `sudo remasterscript`.
Ansonsten `remaster.py` an den Python-Interpreter übgeben (`python remaster.py`)
