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

import gobject
import gtk

from knxremaster.interface.misc import translate as _, label, error

class Isolinux(gtk.VBox):
    class Add(gtk.Dialog):
        def __init__(self, parent=None):
            gtk.Dialog.__init__(self, _('Add'), parent, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
            self.set_response_sensitive(gtk.RESPONSE_OK, False)
            
            self.label = gtk.Entry()
            self.label.connect('changed', self._label_changed)
            
            self.kernel = gtk.Entry()
            self.append = gtk.Entry()
            
            table = gtk.Table(3, 2)
            table.attach(label(_('Label:'), (1, 0.5)), 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
            table.attach(self.label, 1, 2, 0, 1, ypadding=2)
            table.attach(label(_('Kernel:'), (1, 0.5)), 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
            table.attach(self.kernel, 1, 2, 1, 2, ypadding=2)
            table.attach(label(_('Append:'), (1, 0.5)), 0, 1, 2, 3, xoptions=gtk.FILL, xpadding=5, ypadding=2)
            table.attach(self.append, 1, 2, 2, 3, ypadding=2)
            table.show_all()
            
            self.get_content_area().pack_start(table)
        
        def _label_changed(self, entry):
            if entry.get_text():
                self.set_response_sensitive(gtk.RESPONSE_OK, True)
            else:
                self.set_response_sensitive(gtk.RESPONSE_OK, False)            
        
    def __init__(self, isolinux):
        gtk.VBox.__init__(self)
        self.set_spacing(5)
        
        self.isolinux = isolinux
        
        self.default = gtk.combo_box_new_text()
        self.default.connect('changed', self._default_changed)
        self.defaults = []
        for number, name in enumerate(self.isolinux):
            if name != 'default':
                self.default.append_text(name)
                self.defaults.append(name)
                if 'default' in self.isolinux.attributes and name == self.isolinux.attributes['default']:
                    self.default.set_active(number)
        
        self.timeout = gtk.Adjustment(int(self.isolinux.attributes['timeout']) if 'timeout' in self.isolinux.attributes else 0,
                                      0, 10000, 1, 10)
        self.timeout.connect('value-changed', self._timeout_changed)
        
        self.entries = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        for name, options in self.isolinux.items():
            self.entries.append((name, options['kernel'], options['append']))
        
        self.view = gtk.TreeView(self.entries)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect('edited', self._label_edited)
        self.label = gtk.TreeViewColumn(_('Label'), renderer, text=0)
        self.view.append_column(self.label)
        
        renderer = gtk.CellRendererText()
        renderer.connect('edited', self._kernel_edited)
        renderer.set_property('editable', True)
        column = gtk.TreeViewColumn(_('Kernel'), renderer, text=1)
        self.view.append_column(column)
        
        renderer = gtk.CellRendererText()
        renderer.connect('edited', self._append_edited)
        renderer.set_property('editable', True)
        column = gtk.TreeViewColumn(_('Append'), renderer, text=2)
        self.view.append_column(column)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.add(self.view)
                
        add = gtk.Button(stock=gtk.STOCK_ADD)
        add.connect('clicked', self._add)
        
        remove = gtk.Button(stock=gtk.STOCK_REMOVE)
        remove.connect('clicked', self._remove)
        
        buttons = gtk.HButtonBox()
        buttons.set_layout(gtk.BUTTONBOX_START)
        buttons.set_spacing(5)
        buttons.pack_start(add, False, False)
        buttons.pack_start(remove, False, False)
        
        table = gtk.Table(2, 2)
        table.attach(label(_('Default:'), (1, 0.5)), 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.default, 1, 2, 0, 1, ypadding=2)
        table.attach(label(_('Timeout:'), (1, 0.5)), 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(gtk.SpinButton(self.timeout), 1, 2, 1, 2, ypadding=2)
                
        self.pack_start(table, False, False)
        self.pack_start(scrolled)
        self.pack_start(buttons, False, False)
    
    def _default_changed(self, combobox):
        self.isolinux.attributes['default'] = self.default.get_active_text()
    
    def _timeout_changed(self, adjustment):
        self.isolinux.attributes['timeout'] = str(int(self.timeout.get_value())) 
    
    def _label_edited(self, renderer, number, new):
        if self.entries[number][0] == self.default.get_active_text():
            error(_('Error'), _('You could not edit the label of the current default entry.'), self.parent)
        elif self.entries[number][0] == 'default':
            error(_('Error'), _('You cloud not edit the label of the default entry.'), self.parent)
        else:
            position = self.defaults.index(self.entries[number][0])
            self.defaults[position] = new 
            self.default.remove_text(position)
            self.default.insert_text(position, new)
            self.entries[number][0] = new                        
    
    def _kernel_edited(self, renderer, number, new):
        self.entries[number][1] = new
        self.isolinux[self.entries[number][0]]['kernel'] = new
    
    def _append_edited(self, renderer, number, new):
        self.entries[number][2] = new
        self.isolinux[self.entries[number][0]]['append'] = new
    
    def _remove(self, button):
        iter = self.view.get_selection().get_selected()[1]
        if iter:
            number = self.entries.get_path(iter)
            if self.entries[number][0] == self.default.get_active_text():
                error(_('Error'), _('You could not remove the the current default entry.'), self.parent)
            elif self.entries[number][0] == 'default':
                error(_('Error'), _('You cloud not remove the default entry.'), self.parent)
            else:
                self.default.remove_text(self.defaults.index(self.entries[number][0]))
                self.defaults.remove(self.entries[number][0])
                del self.isolinux[self.entries[number][0]]
                self.entries.remove(iter)
    
    def _add(self, button):
        add = self.Add(self.parent)
        def response(dialog, response_id):
            if response_id == gtk.RESPONSE_OK:
                label, kernel, append = dialog.label.get_text(), dialog.kernel.get_text(), dialog.append.get_text()
                if label in self.isolinux:
                    error(_('Error'), _('Entry already exists.'), dialog)
                else:
                    self.defaults.append(label)
                    self.default.append_text(label)
                    self.entries.append((label, kernel, append))
                    self.isolinux[label] = {'kernel': kernel, 'append': append}
            add.destroy()        
        add.connect('response', response)
        add.run()