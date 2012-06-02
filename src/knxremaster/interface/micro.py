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

import gettext
import os.path

import gobject
import gtk

from knxremaster.isolinux import Isolinux
from knxremaster.micro import unpack
from knxremaster.toolkit.asynchron import gobject_exec

_ = gettext.translation('knxremaster', os.path.join(os.path.dirname(__file__), 'locale'), fallback=True).gettext

_task_translation = {'unpack_iso': _('unpack iso image...'),
                     'cleanup': _('cleanup...')}

class Micro():
    def __init__(self):
        self.assistant = gtk.Assistant()
        self.assistant.set_title(_('Knoppix Remasterscript'))
        self.assistant.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.assistant.set_icon_from_file(os.path.join(os.path.dirname(__file__), 'resources', 'icon.png'))
        self.assistant.connect('prepare', self._prepare_page)
        self._setup_page_welcome()
        self._setup_page_unpack()
        self._setup_page_remaster()
        self._pulse = None
        
        
    def _setup_page_welcome(self):
        welcome = gtk.Label()
        welcome.set_markup(_('<span weight="bold">Welcome to Knoppix Remasterscript!!!</span>\nThis assistant will guide you through the steps of micro remastering Knoppix.'))
        welcome.set_alignment(0, 0.5)
        

        self.source = gtk.FileChooserButton(gtk.FileChooserDialog(_('Source'), parent=self.assistant,
                                                                  action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.source.set_filename(os.curdir)
        filter = gtk.FileFilter()
        filter.add_pattern('*.iso')
        self.source.set_filter(filter)
        self._source_set = False
        self.source.connect('current-folder-changed', self._source_changed)
    
        self.target = gtk.FileChooserButton(gtk.FileChooserDialog(_('Target'), parent=self.assistant,
                                                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.target.set_filename(os.curdir)
        self._target_set = False
        self.target.connect('current-folder-changed', self._target_changed)
        
        table = gtk.Table(2, 2)
        label = gtk.Label(_('Source:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.source, 1, 2, 0, 1, ypadding=2)
        label = gtk.Label(_('Target:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.target, 1, 2, 1, 2, ypadding=2)
        
        box = gtk.VBox()
        box.pack_start(welcome, False, False, 5)
        box.pack_start(table, False, False, 5)               
        
        self.welcome = gtk.Alignment(1, 1, 1, 1)
        self.welcome.add(box)
        self.welcome.set_padding(5, 5, 5, 5)

        self.assistant.append_page(self.welcome)
        self.assistant.set_page_title(self.welcome, _('Welcome'))
        self.assistant.set_page_type(self.welcome, gtk.ASSISTANT_PAGE_CONFIRM)
    
    def _setup_page_unpack(self):
        unpack = gtk.Label()
        unpack.set_markup(_('<span weight="bold">Unpacking for micro remastering!!!</span>\nThis script is now unpacking the ISO for micro remastering.'))
        unpack.set_alignment(0, 0.5)
        
        self.progress = gtk.ProgressBar()
        self.status = gtk.Label()
        self.status.set_alignment(0, 0.5)
        
        box = gtk.VBox()
        box.pack_start(unpack, False, False, 5)
        box.pack_start(self.progress, False, False, 5)
        box.pack_start(self.status, False, False, 5) 
        
        self.unpack = gtk.Alignment(1, 1, 1, 1)
        self.unpack.add(box)
        self.unpack.set_padding(5, 5, 5, 5)
        
        self.assistant.append_page(self.unpack)
        self.assistant.set_page_title(self.unpack, _('Unpack'))
        self.assistant.set_page_type(self.unpack, gtk.ASSISTANT_PAGE_PROGRESS)
    
    def _setup_page_remaster(self): 
        self.background = gtk.FileChooserButton(gtk.FileChooserDialog(_('Background'), parent=self.assistant,
                                                                      action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.background.set_current_folder(os.curdir)
        filter = gtk.FileFilter()
        filter.add_pattern('*.jpg')
        self.background.set_filter(filter)
        
        self.save = gtk.FileChooserButton(gtk.FileChooserDialog(_('Save'), parent=self.assistant,
                                                                action=gtk.FILE_CHOOSER_ACTION_SAVE | gtk.FILE_C,
                                                                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK)))
        self.save.set_current_folder(os.curdir)
        
        table = gtk.Table(2, 2)
        label = gtk.Label(_('Background:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.background, 1, 2, 0, 1, ypadding=2)
        label = gtk.Label(_('Save:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.save, 1, 2, 1, 2, ypadding=2)
        
        box = gtk.VBox()
        box.pack_start(table, False, False, 5)               
        
        self.remaster = gtk.Alignment(1, 1, 1, 1)
        self.remaster.add(box)
        self.remaster.set_padding(5, 5, 5, 5)
        
        self.assistant.append_page(self.remaster)
        self.assistant.set_page_title(self.remaster, _('Remaster'))
        self.assistant.set_page_complete(self.remaster, True)
        self.assistant.set_page_type(self.remaster, gtk.ASSISTANT_PAGE_CONFIRM)
    
    def _source_changed(self, filechooser):
        filename = self.source.get_filename()
        if filename is not None and os.path.isfile(filename) and filename.endswith('.iso'):
            self._source_set = True
            self._welcome_check()
        else:
            self._source_set = False
            self._welcome_check()
    
    def _target_changed(self, filechooser):
        filename = self.target.get_filename()
        if filename is not None and len(os.listdir(self.target.get_filename())) == 0:
            self._target_set = True
            self._welcome_check()
        else:
            self._target_set = False
            self._welcome_check()
    
    def _squashfs_changed(self, checkbutton):
        if self.squashfs.get_active():
            self.filesystem.set_active(True)
            self.filesystem.set_sensitive(False)
            self.minirt.set_active(True)
            self.minirt.set_sensitive(False)
        else:
            self.filesystem.set_sensitive(True)
            self.minirt.set_sensitive(True)
    
    def _welcome_check(self):
        if self._source_set and self._target_set:
            self.assistant.set_page_complete(self.welcome, True)
        else:
            self.assistant.set_page_complete(self.welcome, False)
    
    def _prepare_page(self, assistant, page):
        if page == self.unpack:
            self._unpack()
        elif page == self.remaster:
            self._remaster()
            
    def _unpack(self):
        script = unpack(self.source.get_filename(), self.target.get_filename())
        script.event('start').connect(self._task_started)
        script.event('update').connect(self._task_update)
        script.event('success').connect(self._create_success)
        script.event('error').connect(lambda *args, **kwargs: print('error -> no handling yet'))
        script.start()
    
    def _remaster(self):
        self.isolinux = Isolinux(os.path.join(self.target.get_filename(), 'boot', 'isolinux', 'isolinux.cfg'))
        print(self.isolinux)
       
    def _task_pulse(self):
        self.progress.pulse()
        return True
    
    @gobject_exec
    def _task_started(self, name, progress):
        if self._pulse is None:
            self._pulse = gobject.timeout_add(100, self._task_pulse)
        self.status.set_text(_task_translation[name])
    
    @gobject_exec
    def _task_update(self, name, percentage, message):
        if self._pulse is None:
            self.progress.set_fraction(percentage / 100)
        else:
            gobject.source_remove(self._pulse)
            self._pulse = None
    
    @gobject_exec
    def _create_success(self):
        self.assistant.set_page_complete(self.unpack, True)
        if self._pulse is not None:
            gobject.source_remove(self._pulse)
            self.progress.set_fraction(1)
        self.status.set_text(_('Finished...'))
        self.assistant.set_current_page(2)
    
if __name__ == '__main__':
    interface = Micro()
    interface.assistant.show_all()
    interface.assistant.connect('cancel', lambda *args: gtk.main_quit())
    interface.assistant.connect('close', lambda *args: gtk.main_quit())
    gtk.main()