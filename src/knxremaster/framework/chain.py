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

from __future__ import print_function

import functools
import threading

class Chain():
    def __init__(self):
        self.handler = {'success': [], 'error': [], 'started': [], 'finished': [self._next], 'update': []}
               
    def _next(self):
        if len(self.chain):
            threading.Thread(target=self.chain.pop(0)).start()
        else:
            self.emit('success')
    
    def connect(self, progress, name):
        progress.handler['update'].append(functools.partial(self.emit, 'update'))
        progress.handler['started'].append(functools.partial(self.emit, 'started', name))
        progress.handler['finished'].append(functools.partial(self.emit, 'finished'))
        progress.handler['error'].append(lambda *args, **kwargs: print('error!!!'))
    
    def run(self):
        self._next()
    
    def emit(self, type, *args, **kwargs):
        for handler in self.handler[type]:
            handler(*args, **kwargs) 