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
import subprocess

from knxremaster.toolkit.asynchron import ConditionsEvents, thread_exec

class _Progress(ConditionsEvents):
    def __init__(self, function, args, kwargs):
        ConditionsEvents.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.result = None
            
    def __call__(self):
        self.start()
        self.condition('finish').wait()
    
    def cancel(self):
        self.condition('cancel').activate()
    
    def start(self):
        @thread_exec
        def call():
            self.condition('start').activate()
            self.event('start').emit()
            self.result = self.function(self, *self.args, **self.kwargs)
            self.condition('finish').activate()
            if self.condition('cancel'):
                self.event('cancel').emit()
            elif self.condition('error'):
                self.event('error').emit()
            else:
                self.event('finish').emit()
        return call()      
    
    def update(self, percentage, message=None):
        self.event('update').emit(percentage, message)    

def progress(function):
    def wrapper(*args, **kwargs):
        return _Progress(function, args, kwargs)
    functools.update_wrapper(wrapper, function)
    return wrapper

class _Script(ConditionsEvents):
    def __init__(self, function, args, kwargs):
        ConditionsEvents.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.progress = None
    
    def __call__(self):
        self.start()
        self.condition('finish').wait()
    
    def cancel(self):
        self.condition('cancel').activate()
        if self.progress is not None:
            self.progress.cancel()
    
    def start(self):
        @thread_exec
        def call():
            for name, progress in self.function(self, *self.args, **self.kwargs):
                def update(percentage, message=None):
                    self.event('update').emit(name, percentage, message)
                self.progress = progress
                self.progress.event('update').connect(update)
                self.event('start').emit(name, self.progress)
                if self.condition('cancel'):
                    break
                self.progress()
                if progress.condition('cancel'):
                    self.condition('cancel').activate()
                    break
                elif progress.condition('error'):
                    self.condition('error').activate()
                    self.error = name
                    break
                self.event('finish').emit(name, self.progress)
            if self.condition('cancel'):
                self.event('cancel').emit()
            elif self.condition('error'):
                self.event('error').emit()
            else:
                self.event('success').emit()
        return call()       

def script(function):
    def wrapper(*args, **kwargs):
        return _Script(function, args, kwargs)
    functools.update_wrapper(wrapper, function)
    return wrapper
    
@progress
def command(progress, command, *arguments, **kwargs):
    progress.process = subprocess.Popen([command] + list(arguments), **kwargs)
    progress.condition('process').activate()
    while progress.process.poll() is None:
        progress.condition('cancel').wait(0.5)
        if progress.condition('cancel'):
            progress.process.kill()
    if progress.process.returncode != 0:
        progress.condition('error').activate()