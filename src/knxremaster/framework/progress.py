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
import threading

class _Progress():
    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.started = threading.Event()
        self.finished = threading.Event()
        self.cancel = threading.Event()
        self.error = threading.Event()
        self.result = None
        self.handler = {'update': [], 'started': [], 'finished': [], 'canceled': [], 'error': []}
    
    def __call__(self):
        self.start()
        self.finished.wait()
    
    def start(self):
        self.started.set()
        def call():
            for handler in self.handler['started']:
                handler()
            self.result = self.function(self, *self.args, **self.kwargs)
            self.finished.set()
            if self.cancel.is_set():
                for handler in self.handler['canceled']:
                    handler()
            elif self.error.is_set():
                for handler in self.handler['error']:
                    handler()
            else:
                for handler in self.handler['finished']:
                    handler()
        threading.Thread(target=call).start()        
    
    def update(self, percentage, message=None):
        for handler in self.handler['update']:
            handler(percentage, message)       

def progress(function):
    def wrapper(*args, **kwargs):
        return _Progress(function, args, kwargs)
    functools.update_wrapper(wrapper, function)
    return wrapper

@progress
def command(progress, command, *arguments):
    command = [command]
    command.extend(arguments)
    process = subprocess.Popen(command)
    while True:
        progress.cancel.wait(0.5)
        if progress.cancel.is_set():
            break
        if process.poll() is not None:
            if process.returncode == 0:
                break
            else:
                progress.error.set()
                break