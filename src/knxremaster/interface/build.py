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

import os
import os.path

import gtk

from knxremaster.build import build
from knxremaster.interface.misc import translate as _
from knxremaster.interface.script import Script
from knxremaster.toolkit.asynchron import gobject_exec
from knxremaster.versions import get_version

_steps = {'prepare': _('prepare for building...'),
          'filesystem_image': _('create filesystem image...'),
          'filesystem_compress': _('compress filesystem image...'),
          'minirt_files': _('collect files for minirt...'),
          'minirt_image': _('create minirt image...'),
          'minirt_compress': _('compress minirt image...'),
          'iso_image': _('create cd/dvd iso image...'),
          'cleanup': _('cleanup...')}

class Build():
    def __init__(self):
        self.assistant = gtk.Assistant()
        self.assistant.set_title(_('Knoppix Remasterscript'))
        self.assistant.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.assistant.set_icon_from_file(os.path.join(os.path.dirname(__file__), 'resources', 'icon.png'))
        self.assistant.connect('prepare', self._prepare)
        
        self.script = Script(build, _steps)
        self.script.event('success').connect(self._success)
        
        self._setup_page_welcome()
        self._setup_page_summary()
        self._setup_page_build()
        self._setup_page_finished()        
        
    def _setup_page_welcome(self):
        welcome = gtk.Label()
        welcome.set_markup(_('<span weight="bold">Welcome to Knoppix Remasterscript!!!</span>\nThis assistant will guide you through the steps of building your own Remaster.'))
        welcome.set_alignment(0, 0.5)
        
        self.source = gtk.FileChooserButton(gtk.FileChooserDialog(_('Source'), parent=self.assistant,
                                                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.source.set_filename(os.curdir)
        self._source_set = False
        self.source.connect('current-folder-changed', self._source_changed)
        
        table = gtk.Table(1, 2)
        label = gtk.Label(_('Source:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.source, 1, 2, 0, 1, ypadding=2)
        
        box = gtk.VBox()
        box.pack_start(welcome, False, False, 5)
        box.pack_start(table, False, False, 5)               
        
        self.welcome = gtk.Alignment(1, 1, 1, 1)
        self.welcome.add(box)
        self.welcome.set_padding(5, 5, 5, 5)

        self.assistant.append_page(self.welcome)
        self.assistant.set_page_title(self.welcome, _('Welcome'))
        self.assistant.set_page_type(self.welcome, gtk.ASSISTANT_PAGE_INTRO)
    
    def _setup_page_summary(self):
        summary = gtk.Label()
        summary.set_markup(_('<span weight="bold">Summary!!!</span>\nPlease check if everything is correct.'))
        summary.set_alignment(0, 0.5)

        self.name = gtk.Label()
        self.name.set_alignment(0, 0.5)
        
        self.base_version = gtk.Label()
        self.base_version.set_alignment(0, 0.5)
        
        self.compression = gtk.Label()
        self.compression.set_alignment(0, 0.5)
               
        table = gtk.Table(3, 2)
        label = gtk.Label(_('Name:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.name, 1, 2, 0, 1, ypadding=2)
        label = gtk.Label(_('Base Version:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.base_version, 1, 2, 1, 2, ypadding=2)
        label = gtk.Label(_('Compression:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.compression, 1, 2, 2, 3, ypadding=2)

        box = gtk.VBox()
        box.pack_start(summary, False, False, 5)
        box.pack_start(table, False, False, 5)               
                
        self.summary = gtk.Alignment(1, 1, 1, 1)
        self.summary.add(box)
        self.summary.set_padding(5, 5, 5, 5)

        self.assistant.append_page(self.summary)
        self.assistant.set_page_title(self.summary, _('Summary'))
        self.assistant.set_page_complete(self.summary, True)
        self.assistant.set_page_type(self.summary, gtk.ASSISTANT_PAGE_CONFIRM)
    
    def _setup_page_build(self):
        build = gtk.Label()
        build.set_markup(_('<span weight="bold">Building a new Remaster!!!</span>\nThis script is now building a new Remaster.'))
        build.set_alignment(0, 0.5)
                
        box = gtk.VBox()
        box.set_spacing(5)
        box.pack_start(build, False, False)
        box.pack_start(self.script, False, False)
        
        self.build = gtk.Alignment(1, 1, 1, 1)
        self.build.add(box)
        self.build.set_padding(5, 5, 5, 5)
        
        self.assistant.append_page(self.build)
        self.assistant.set_page_title(self.build, _('Build'))
        self.assistant.set_page_type(self.build, gtk.ASSISTANT_PAGE_PROGRESS)
    
    def _setup_page_finished(self):
        finished = gtk.Label()
        finished.set_markup(_('<span weight="bold">Remaster successful built!!!</span>\nFinished. A new Remaster was built.'))
        finished.set_alignment(0, 0.5)
               
        box = gtk.VBox()
        box.pack_start(finished, False, False, 5)
        
        self.finished= gtk.Alignment(1, 1, 1, 1)
        self.finished.add(box)
        self.finished.set_padding(5, 5, 5, 5)
        
        self.assistant.append_page(self.finished)
        self.assistant.set_page_title(self.finished, _('Finished'))
        self.assistant.set_page_type(self.finished, gtk.ASSISTANT_PAGE_SUMMARY)
    
    def _source_changed(self, filechooser):
        if os.path.exists(os.path.join(self.source.get_filename(), 'master', 'KNOPPIX', 'KNOPPIX')):
            self.assistant.set_page_complete(self.welcome, True)
        else:
            self.assistant.set_page_complete(self.welcome, False)
    
    def _prepare(self, assistant, page):
        if page == self.build:
            self._build()
        elif page == self.summary:
            self._summary()
    
    def _build(self):
        self.script.start(self.source.get_filename())
    
    def _summary(self):
        name, squashfs, base = get_version(os.path.join(self.source.get_filename(), 'master'))
        if name == 'Unknown':
            name = _('Unknown')
        self.name.set_text(name)
        if base == 'Unknown':
            base = _('Unknown')
        self.base_version.set_text(base)
        if squashfs is None:
            self.compression.set_text(_('Cloop'))
        elif squashfs is True:
            self.compression.set_text(_('SquashFS'))
        else:
            self.compression.set_text(_('Cloop'))
    
    @gobject_exec
    def _success(self):
        self.assistant.set_page_complete(self.build, True)
        self.assistant.set_current_page(3)

if __name__ == '__main__':
    interface = Build()
    interface.assistant.show_all()
    interface.assistant.connect('cancel', lambda *args: gtk.main_quit())
    interface.assistant.connect('close', lambda *args: gtk.main_quit())
    gtk.main()