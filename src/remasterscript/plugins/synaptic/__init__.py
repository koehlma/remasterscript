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

import gobject

import remasterscript.misc.const as const
import remasterscript.misc.utils as utils

class Synaptic(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._synaptic = None
        
    def _success(self, process):
        self._synaptic = None
        self.emit('stop')
        
    def _error(self, process, errorcode):
        self._synaptic = None
        self.emit('stop')

    def set_source(self, source):
        self._source = source
    
    def start(self):
        self._synaptic = utils.Util('"%s" "%s" /usr/sbin/synaptic' % (const.BINARY_CHROOT,
                                                                            self._source + '/rootdir/'))
        self._synaptic.connect('success', self._success)
        self._synaptic.connect('error', self._error)
        
    def stop(self):
        if self._synaptic:
            self._synaptic.kill()
    
    def get_name(self):
        return 'Synaptic'
    
    def get_description(self):
        return 'Öffne Synaptic'

gobject.type_register(Synaptic)
gobject.signal_new('stop',
                        Synaptic,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())