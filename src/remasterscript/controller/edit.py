# -*- coding:utf-8 -*-
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

import controller
import remasterscript.core.views.edit as view
from remasterscript.plugins import plugins
import remasterscript.misc.const as const
import remasterscript.misc.utils as utils

class Edit(controller.Controller):
    def __init__(self, build):
        controller.Controller.__init__(self)
        self._build = build
        self._build.connect('success', self._build_success)
        self._build.connect('cancel', self._build_cancel)
        self._view = view.Edit()
        self._view.connect('quit', self._on_quit)
        self._view.connect('build', self._on_build)
        self._view.connect('plugin-start', self._on_plugin_start)
        self._view.connect('plugin-stop', self._on_plugin_stop)
        self._plugins = {}
        for plugin in plugins:
            self._view.plugin_add(plugin.get_name(), plugin.get_description())
            self._plugins[plugin.get_name()] = plugin
            self._plugins[plugin.get_name()].connect('stop', self._event_plugin_stop, plugin.get_name())
    
    def _event_plugin_stop(self, plugin, name):
        self._view.start_off(name)
        self._plugins[name].stop()
        
    def _on_plugin_start(self, view, name):
        self._plugins[name].start()
    
    def _on_plugin_stop(self, view, name):
        self._view.start_off(name)
        self._plugins[name].stop()
    
    def _on_quit(self, view):
        self._finish()
        self.emit('quit')
    
    def _build_cancel(self, controller):
        controller.stop()
        self._prepare()
        self._view.show()
    
    def _build_success(self, controller):
        controller.stop()
        self._prepare()
        self._view.show()
    
    def _on_build(self, view):
        self._build.reset()
        self._build.set_source(self._source)
        self._build.start(self)
    
    def _prepare(self):
        process = utils.Util('"%s" "%s" "%s"' % (const.BINARY_BASH,
                                                    const.PATH + '/scripts/chroot-prepare.sh',
                                                    self._source))
        process.wait()
    
    def _finish(self):
        process = utils.Util('"%s" "%s" "%s"' % (const.BINARY_BASH,
                                                    const.PATH + '/scripts/chroot-finish.sh',
                                                    self._source))
        process.wait()
    
    def set_source(self, source):
        self._source = source
        for plugin in self._plugins:
            self._plugins[plugin].set_source(source)

    def start(self, controller):
        self._parent = controller
        self._parent.stop()
        self._prepare()
        self._view.show()
    
    def stop(self):
        self._finish()
        self._view.hide()