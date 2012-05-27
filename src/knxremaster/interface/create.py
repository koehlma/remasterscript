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

import functools
import gettext
import os
import os.path

import gobject
import gtk

from knxremaster.framework.create import Create as Worker

gobject.threads_init()

def idle(function):
    def wrapper(*args, **kwargs):
        def call():
            function(*args, **kwargs)
        gobject.idle_add(call)
    functools.update_wrapper(wrapper, function)
    return wrapper

_ = gettext.translation('knxremaster', os.path.join(os.path.dirname(__file__), 'locale'), fallback=True).gettext

_task_translation = {'mkdir': _('create directory structure...'),
                     'copy': _('copy cd/dvd...'),
                     'extract': _('extract compressed filesytem...'),
                     'mount': _('mount extracted filesystem...'),
                     'knoppix': _('copy mounted filesystem...'),
                     'umount': _('umount compressed filesystem...'),
                     'clean': _('cleanup...')}

class Create(gtk.Assistant):
    def __init__(self):
        gtk.Assistant.__init__(self)
        self.set_title(_('Knoppix Remasterscript'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self._setup_page_welcome()
        self._setup_page_create()
        self._setup_page_finished()
        self.connect('prepare', self._prepare_page)
        self._pulse = None
        
    def _setup_page_welcome(self):
        welcome = gtk.Label()
        welcome.set_markup(_('<span weight="bold">Welcome to Knoppix Remasterscript!!!</span>\nThis assistant will guide you through the steps of creating your own Remaster.'))
        welcome.set_alignment(0, 0.5)
        
        self.source = gtk.FileChooserButton(gtk.FileChooserDialog(_('Source'), parent=self,
                                                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.source.set_filename(os.curdir)
        self._source_set = False
        self.source.connect('current-folder-changed', self._source_changed)
        
        self.target = gtk.FileChooserButton(gtk.FileChooserDialog(_('Target'), parent=self,
                                                                  action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)))
        self.target.set_filename(os.curdir)
        self._target_set = False
        self.target.connect('current-folder-changed', self._target_changed)
        
        table = gtk.Table(2, 2)
        label = gtk.Label(_('Source'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=5)
        table.attach(self.source, 1, 2, 0, 1)
        label = gtk.Label(_('Target'))
        label.set_alignment(1, 0.5)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, xpadding=5)
        table.attach(self.target, 1, 2, 1, 2)
        
        box = gtk.VBox()
        box.pack_start(welcome, False, False, 5)
        box.pack_start(table, False, False, 5)               
        
        self.welcome = gtk.Alignment(1, 1, 1, 1)
        self.welcome.add(box)
        self.welcome.set_padding(5, 5, 5, 5)

        self.append_page(self.welcome)
        self.set_page_title(self.welcome, _('Welcome'))
        self.set_page_type(self.welcome, gtk.ASSISTANT_PAGE_INTRO)
    
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
        
        self.append_page(self.create)
        self.set_page_title(self.create, _('Create'))
        self.set_page_type(self.create, gtk.ASSISTANT_PAGE_PROGRESS)
    
    def _setup_page_finished(self):
        finished = gtk.Label()
        finished.set_markup(_('<span weight="bold">Remaster successful created!!!</span>\nFinished. A new Remaster was created.'))
        finished.set_alignment(0, 0.5)
               
        box = gtk.VBox()
        box.pack_start(finished, False, False, 5)
        
        self.finished= gtk.Alignment(1, 1, 1, 1)
        self.finished.add(box)
        self.finished.set_padding(5, 5, 5, 5)
        
        self.append_page(self.finished)
        self.set_page_title(self.finished, _('Finished'))
        self.set_page_type(self.finished, gtk.ASSISTANT_PAGE_SUMMARY)
    
    def _source_changed(self, filechooser):
        if os.path.exists(os.path.join(self.source.get_filename(), 'KNOPPIX', 'KNOPPIX')):
            self._source_set = True
            self._welcome_check()
        else:
            self._source_set = False
    
    def _target_changed(self, filechooser):
        if len(os.listdir(self.target.get_filename())) == 0:
            self._target_set = True
            self._welcome_check()
        else:
            self._target_set = False
    
    def _welcome_check(self):
        if self._source_set and self._target_set:
            self.set_page_complete(self.welcome, True)
        else:
            self.set_page_complete(self.welcome, False)
    
    def _prepare_page(self, assistant, page):
        if page == self.create:
            self._create()
    
    def _create(self):
        worker = Worker(self.source.get_filename(), self.target.get_filename())
        worker.handler['started'].append(self._task_started)
        worker.handler['update'].append(self._task_update)
        worker.handler['success'].append(self._create_success)
        worker.run()
    
    def _task_pulse(self):
        self.progress.pulse()
        return True
    
    @idle
    def _task_started(self, name):
        if self._pulse is None:
            self._pulse = gobject.timeout_add(100, self._task_pulse)
        self.status.set_text(_task_translation[name])
    
    @idle
    def _task_update(self, percentage, message):
        if self._pulse is None:
            self.progress.set_fraction(percentage / 100)
        else:
            gobject.source_remove(self._pulse)
            self._pulse = None
    
    @idle
    def _create_success(self):
        self.set_page_complete(self.create, True)
        if self._pulse is not None:
            gobject.source_remove(self._pulse)
            self.progress.set_fraction(1)
        self.status.set_text(_('Finished...'))
        self.set_current_page(2)