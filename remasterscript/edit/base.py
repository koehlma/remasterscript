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

class Edit(gobject.GObject):
    def __init__(self, source):
        gobject.GObject.__init__(self)
        self._source = source
    
    def start(self):
        print 'Start'
        
    def stop(self):
        print 'Stop'
        
gobject.type_register(Edit)
gobject.signal_new('stoped',
                        Edit,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('started',
                        Edit,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())