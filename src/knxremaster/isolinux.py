# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import re

_COMMAND = re.compile('([a-zA-Z0-9]+) (.*)')

class Isolinux(dict):
    def __init__(self, filename):
        self.filename = filename
        self.attributes = {}
        with open(self.filename) as isolinux:
            for line in isolinux:
                match = _COMMAND.match(line)
                if match:
                    command, argument = match.group(1).lower(), match.group(2).strip()
                    if command == 'label':
                        current = argument
                        self[current] = {'append': '', 'kernel': ''}
                    elif command in ('append', 'kernel'):
                        self[current][command] = argument
                    elif command == 'default':
                        current = 'default'
                        self[current] = {'append': '', 'kernel': ''}
                        self.attributes['default'] = argument
                    else:
                        self.attributes[command] = argument
    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        with open(filename, 'wb') as isolinux:
            def write(command, argument):
                isolinux.write('%s %s\n' % (command.upper(), argument))
            if 'default' in self.attributes:
                write('default', self.attributes['default'])
                if self['default']['kernel']:
                    write('kernel', self['default']['kernel'])
                if self['default']['append']:
                    write('append', self['default']['append'])
            for name, value in self.attributes.items():
                if name != 'default':
                    write(name, value)
            for label, options in self.items():
                write('label', label)
                if self[label]['kernel']:
                    write('kernel', self[label]['kernel'])
                if self[label]['append']:
                    write('append', self[label]['append'])