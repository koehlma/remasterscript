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

import view

class Edit(view.View):
    def __init__(self):
        view.View.__init__(self, 'edit.ui')
        self._window.connect('delete-event', self._on_quit)
        self._quit = self._builder.get_object('quit')
        self._quit.connect('clicked', self._on_quit)
        self._build = self._builder.get_object('build')
        self._build.connect('clicked', self._on_build)
        self._plugins = self._builder.get_object('plugins')
        self._start_buttons = {}
        self._stop_buttons = {}
        self._current_row = 0
        
    def plugin_add(self, name, description):
        self._plugins.resize(self._current_row + 1, 4)
        label_name = view.gtk.Label(name)
        label_name.set_alignment(0, 0.5)
        label_description = view.gtk.Label(description)
        label_description.set_alignment(0, 0.5)
        self._start_buttons[name] = self._make_start_button()
        self._start_buttons[name].connect('clicked', self._plugin_start, name)
        self._stop_buttons[name] = self._make_stop_button()
        self._stop_buttons[name].connect('clicked', self._plugin_stop, name)
        self._plugins.attach(label_name, 0, 1, self._current_row, self._current_row + 1)
        self._plugins.attach(label_description, 1, 2, self._current_row, self._current_row + 1)
        self._plugins.attach(self._start_buttons[name], 2, 3, self._current_row, self._current_row + 1)
        self._plugins.attach(self._stop_buttons[name], 3, 4, self._current_row, self._current_row + 1)
        self._current_row += 1
    
    def start_off(self, name):
        self._start_buttons[name].set_active(False)
    
    def _make_start_button(self):
        button = view.gtk.ToggleButton()
        button_hbox = view.gtk.HBox()
        button_hbox.set_spacing(5)
        button_image = view.gtk.image_new_from_icon_name('gtk-yes', view.gtk.ICON_SIZE_BUTTON)
        button_label = view.gtk.Label('Starten')
        button_hbox.pack_start(button_image, False, False)
        button_hbox.pack_start(button_label, False, False)
        button.add(button_hbox)
        return button
    
    def _make_stop_button(self):
        button = view.gtk.Button()
        button_hbox = view.gtk.HBox()
        button_hbox.set_spacing(5)
        button_image = view.gtk.image_new_from_icon_name('gtk-no', view.gtk.ICON_SIZE_BUTTON)
        button_label = view.gtk.Label('Stoppen')
        button_hbox.pack_start(button_image, False, False)
        button_hbox.pack_start(button_label, False, False)
        button.add(button_hbox)
        return button
    
    def _plugin_start(self, button, name):
        self.emit('plugin-start', name)
    
    def _plugin_stop(self, button, name):
        self.emit('plugin-stop', name)
    
    def _on_build(self, button):
        self.emit('build')
        
    def _on_quit(self, widget, event = None):
        self.emit('quit')

view.type_register(Edit)
view.signal_new('build',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('plugin-start',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    (view.TYPE_STRING,))
view.signal_new('plugin-stop',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    (view.TYPE_STRING,))
view.signal_new('quit',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())