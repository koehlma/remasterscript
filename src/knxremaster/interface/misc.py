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

import gettext
import os.path

import gtk

def label(markup, alignment=None):
    label = gtk.Label()
    label.set_markup(markup)
    if alignment is not None:
        label.set_alignment(*alignment)
    return label

def error(title, message, parent=None):
    dialog = gtk.MessageDialog(parent, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
    dialog.set_title('Error')
    dialog.set_markup('<span weight="bold">%s</span>\n%s' % (title, message))
    dialog.connect('response', lambda *args: dialog.destroy())
    dialog.run()   

translate = gettext.translation('knxremaster', os.path.join(os.path.dirname(__file__), 'locale'), fallback=True).gettext