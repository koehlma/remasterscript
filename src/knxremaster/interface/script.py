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

from __future__ import division

import gobject
import gtk

from knxremaster.interface.misc import translate as _, error
from knxremaster.toolkit.asynchron import ConditionsEvents, gobject_exec

class Script(ConditionsEvents, gtk.VBox):
    def __init__(self, script, steps={}, messages={}):
        gtk.VBox.__init__(self)
        ConditionsEvents.__init__(self)
        
        self.script = script
        self.steps = steps
        self.messages = messages
               
        self.progress = gtk.ProgressBar()
        
        self.status = gtk.Label()
        self.status.set_alignment(0, 0.5)
        
        self.set_spacing(5)        
        self.pack_start(self.progress, False, False)
        self.pack_start(self.status, False, False)
        
        self._timeout = None
    
    def _pulse(self):
        self.progress.pulse()
        return True
    
    def _pulse_start(self):
        if self._timeout is None:
            self._timeout = gobject.timeout_add(100, self._pulse)
    
    def _pulse_stop(self):
        if self._timeout is not None:
            gobject.source_remove(self._timeout)
            self._timeout = None
    
    @gobject_exec       
    def _start(self, name, progress):
        self._pulse_start()
        self.status.set_text(self.steps.get(name, name))
    
    @gobject_exec
    def _update(self, name, percentage, message=None):
        self._pulse_stop()
        self.progress.set_fraction(percentage / 100)
        if message is None:
            self.status.set_text(self.steps.get(name, name))
        else:
            self.status.set_text('%s (%s)' % (self.steps.get(name, name), self.messages.get(message, message)))
                
    @gobject_exec
    def _error(self, name, progress):
        self._pulse_stop()
        self.progress.set_fraction(0)
        self.status.set_text(_('Error...'))
        error(_('Error'), _('Error occurred during: "%s"') % (self.steps.get(name, name)), self.parent)
        self.event('error').emit()
        
    @gobject_exec
    def _success(self):
        self._pulse_stop()
        self.progress.set_fraction(1)
        self.status.set_text(_('Finished...'))
        self.event('success').emit()
        
    def start(self, *args, **kwargs):
        script = self.script(*args, **kwargs)
        script.event('start').connect(self._start)
        script.event('update').connect(self._update)
        script.event('error').connect(self._error)
        script.event('success').connect(self._success)
        script.start()