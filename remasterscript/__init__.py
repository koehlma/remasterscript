# -*- coding:utf8 -*-
import re
import os

import gtk
import gobject

import controller

def _new_success(new, source):
    edit = controller.edit.Controller(source)
    edit.connect('quit', quit)
    edit.connect('build', _build)
    edit.start()
    new.stop()

def _open(open, source):
    edit = controller.edit.Controller(source)
    edit.connect('quit', quit)
    edit.connect('build', _build)
    edit.start()
    open.stop()

def _build(source):
    pass

def quit(*args):
    gtk.main_quit()

def main():
    new = controller.new.Controller()
    new.stop()
    new.connect('quit', quit)
    new.connect('cancel', quit)
    new.connect('success', _new_success)
    open = controller.open.Controller()
    open.connect('quit', quit)
    open.connect('open', _open)
    open.stop()
    welcome = controller.welcome.Controller()
    welcome.start()
    welcome.connect('quit', quit)
    welcome.connect('new', new.start)
    welcome.connect('open', open.start)
    gtk.main()