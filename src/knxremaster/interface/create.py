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
import os
import os.path

import gobject
import gtk

from knxremaster.create import create
from knxremaster.versions import get_version
from knxremaster.toolkit.asynchron import gobject_exec

_ = gettext.translation('knxremaster', os.path.join(os.path.dirname(__file__), 'locale'), fallback=True).gettext

_task_translation = {'create_directories': _('create directory structure...'),
                     'copy_master': _('copy cd/dvd...'),
                     'filesystem_decompress': _('extract compressed filesytem...'),
                     'filesystem_mount': _('mount extracted filesystem...'),
                     'filesystem_copy': _('copy mounted filesystem...'),
                     'filesystem_umount': _('umount compressed filesystem...'),
                     'minirt_decompress': _('extract minirt...'),
                     'minirt_unpack': _('unpack minirt...'),
                     'squashfs_patch': _('patching for squashfs...'),
                     'cleanup': _('cleanup...'),
                     'write_settings': _('write settings...')}

class Create():
    def __init__(self):
        self.assistant = gtk.Assistant()
        self.assistant.set_title(_('Knoppix Remasterscript'))
        self.assistant.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.assistant.set_icon_from_file(os.path.join(os.path.dirname(__file__), 'resources', 'icon.png'))
        self.assistant.connect('prepare', self._prepare_page)
        self._setup_page_welcome()
        self._setup_page_settings()
        self._setup_page_summary()
        self._setup_page_create()
        self._setup_page_finished()        
        self._pulse = None
        
    def _setup_page_welcome(self):
        welcome = gtk.Label()
        welcome.set_markup(_('<span weight="bold">Welcome to Knoppix Remasterscript!!!</span>\nThis assistant will guide you through the steps of creating your own Remaster.'))
        welcome.set_alignment(0, 0.5)
        
        self.source = gtk.FileChooserButton(gtk.FileChooserDialog(_('Source'), parent=self.assistant,
                                                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.source.set_filename(os.curdir)
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
        self.assistant.set_page_type(self.welcome, gtk.ASSISTANT_PAGE_INTRO)
    
    def _setup_page_settings(self):
        self.name = gtk.Entry()
        self.name.set_text(_('My Remaster'))
        
        self.filesystem = gtk.CheckButton()
        self.filesystem.set_active(True)
        
        self.minirt = gtk.CheckButton()
        self.minirt.set_active(True)
        
        self.squashfs = gtk.CheckButton()
        self.squashfs.connect('toggled', self._squashfs_changed)
        
        table = gtk.Table(4, 2)
        label = gtk.Label(_('Name:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.name, 1, 2, 0, 1, ypadding=2)
        label = gtk.Label(_('Extract Filesystem:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.filesystem, 1, 2, 1, 2, ypadding=2)
        label = gtk.Label(_('Extract Minirt:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.minirt, 1, 2, 2, 3, ypadding=2)
        label = gtk.Label(_('SquashFS:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 3, 4, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.squashfs, 1, 2, 3, 4, ypadding=2)

        box = gtk.VBox()
        box.pack_start(table, False, False, 5)               
        
        self.settings = gtk.Alignment(1, 1, 1, 1)
        self.settings.add(box)
        self.settings.set_padding(5, 5, 5, 5)

        self.assistant.append_page(self.settings)
        self.assistant.set_page_title(self.settings, _('Settings'))
        self.assistant.set_page_complete(self.settings, True)
    
    def _setup_page_summary(self):
        summary = gtk.Label()
        summary.set_markup(_('<span weight="bold">Summary!!!</span>\nPlease check if everything is correct.'))
        summary.set_alignment(0, 0.5)

        self.base_version = gtk.Label()
        self.base_version.set_alignment(0, 0.5)
        
        self.base_compression = gtk.combo_box_new_text()
        self.base_compression.append_text(_('Cloop'))
        self.base_compression.append_text(_('SquashFS'))
        self.base_compression.set_sensitive(False)
        
        self.options = gtk.Label()
        self.options.set_alignment(0, 0.5)
               
        table = gtk.Table(3, 2)
        label = gtk.Label(_('Base Version:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.base_version, 1, 2, 0, 1, ypadding=2)
        label = gtk.Label(_('Base Compression:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.base_compression, 1, 2, 1, 2, ypadding=2)
        label = gtk.Label(_('Options:'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, xpadding=5, ypadding=2)
        table.attach(self.options, 1, 2, 2, 3, ypadding=2)

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
    
    def _setup_page_create(self):
        create = gtk.Label()
        create.set_markup(_('<span weight="bold">Creating a new Remaster!!!</span>\nThis script is now creating a new Remaster only for you.'))
        create.set_alignment(0, 0.5)
        
        self.progress = gtk.ProgressBar()
        self.status = gtk.Label()
        self.status.set_alignment(0, 0.5)
        
        box = gtk.VBox()
        box.pack_start(create, False, False, 5)
        box.pack_start(self.progress, False, False, 5)
        box.pack_start(self.status, False, False, 5) 
        
        self.create = gtk.Alignment(1, 1, 1, 1)
        self.create.add(box)
        self.create.set_padding(5, 5, 5, 5)
        
        self.assistant.append_page(self.create)
        self.assistant.set_page_title(self.create, _('Create'))
        self.assistant.set_page_type(self.create, gtk.ASSISTANT_PAGE_PROGRESS)
    
    def _setup_page_finished(self):
        finished = gtk.Label()
        finished.set_markup(_('<span weight="bold">Remaster successful created!!!</span>\nFinished. A new Remaster was created.'))
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
        if os.path.exists(os.path.join(self.source.get_filename(), 'KNOPPIX', 'KNOPPIX')):
            self._source_set = True
            self._welcome_check()
        else:
            self._source_set = False
            self._welcome_check()
    
    def _target_changed(self, filechooser):
        if len(os.listdir(self.target.get_filename())) == 0:
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
        if page == self.create:
            self._create()
        elif page == self.summary:
            self._summary()
    
    def _create(self):
        script = create(self.source.get_filename(), self.target.get_filename(),
                        self.name.get_text(), self.filesystem.get_active(),
                        self.minirt.get_active(), self.squashfs.get_active(),
                        'cloop' if self.base_compression.get_active() == 0 else 'squashfs',
                        self.base_version.get_text())
        script.event('start').connect(self._task_started)
        script.event('update').connect(self._task_update)
        script.event('success').connect(self._create_success)
        script.event('error').connect(lambda *args, **kwargs: print('error -> no handling yet'))
        script.start()
    
    def _summary(self):
        name, squashfs, base = get_version(self.source.get_filename())
        if name == 'Unknown':
            name = _('Unknown')
        self.base_version.set_text(name)
        if squashfs is None:
            self.base_compression.set_active(0)
            self.base_compression.set_sensitive(True)
        elif squashfs is True:
            self.base_compression.set_active(1)
        else:
            self.base_compression.set_active(0)
        _yes_no = {True: _('Yes'), False: _('No')}
        self.options.set_text('%s %s | %s %s | %s %s' % (_('Filesystem:'), _yes_no[self.filesystem.get_active()],
                                                         _('Minirt:'), _yes_no[self.minirt.get_active()],
                                                         _('SquashFS:'), _yes_no[self.squashfs.get_active()]))
    
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
        self.assistant.set_page_complete(self.create, True)
        if self._pulse is not None:
            gobject.source_remove(self._pulse)
            self.progress.set_fraction(1)
        self.status.set_text(_('Finished...'))
        self.assistant.set_current_page(4)

if __name__ == '__main__':
    interface = Create()
    interface.assistant.show_all()
    interface.assistant.connect('cancel', lambda *args: gtk.main_quit())
    interface.assistant.connect('close', lambda *args: gtk.main_quit())
    gtk.main()