# -*- coding:utf8 -*-
"""
This file is part of Knoppix-Remaster-Script.

Knoppix-Remaster-Script is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Knoppix-Remaster-Script is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Knoppix-Remaster-Script.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

BINARY_EXTRACT_COMPRESSED_FS = '/opt/knoppix/bin/extract_compressed_fs'
BINARY_CREATE_COMPRESSED_FS = '/opt/knoppix/bin/create_compressed_fs'
BINARY_COPY = '/bin/cp'
BINARY_MOUNT = '/bin/mount'
BINARY_UMOUNT = '/bin/umount'
BINARY_REMOVE = '/bin/rm'
BINARY_MKISOFS = '/usr/bin/mkisofs'
BINARY_BASH = '/bin/bash'
BINARY_QEMU = '/usr/bin/qemu'
BINARY_CHROOT = '/usr/sbin/chroot'
BINARY_GNOME_TERMINAL = '/usr/bin/gnome-terminal'
BINARY_XTERM = '/usr/bin/xterm'
BINARY_LXTERMINAL = '/usr/bin/lxterminal'

TERMINALS = {'XTerm' : BINARY_XTERM,
                'GNOME-Terminal' : BINARY_GNOME_TERMINAL,
                'LXTerminal' : BINARY_LXTERMINAL}

QEMU_MEM_SIZE = 256

PATH = os.path.dirname(__file__)