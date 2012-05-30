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
import threading

import gobject

gobject.threads_init()

class _Caller(object):
    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
        self.result = None
                
    def __call__(self):
        self.result = self.function(*self.args, **self.kwargs)
        self.finished.set()

def gobject_exec(function):
    def wrapper(*args, **kwargs):                        
        caller = _Caller(function, args, kwargs)
        gobject.idle_add(caller)
        return caller
    functools.update_wrapper(wrapper, function)
    return wrapper

def thread_exec(function):
    def wrapper(*args, **kwargs):                        
        caller = _Caller(function, args, kwargs)
        threading.Thread(target=caller).start()
        return caller
    functools.update_wrapper(wrapper, function)
    return wrapper

class Event(object):
    def __init__(self):
        self.handler = []
    
    def connect(self, function, *user_args, **user_kwargs):
        self.handler.append((function, user_args, user_kwargs))
    
    def emit(self, *call_args, **call_kwargs):
        for function, user_args, user_kwargs in self.handler:
            args = list(call_args)
            args.extend(user_args)
            kwargs = dict(call_kwargs)
            kwargs.update(user_kwargs)
            function(*args, **kwargs)

class Events(object):
    def __init__(self):
        self.__events = {}
    
    def connect(self, name, function, *args, **kwargs):
        if name not in self.__events:
            self.__events[name] = Event()
        self.__events[name].connect(function, *args, **kwargs)
    
    def emit(self, name, *args, **kwargs):
        if name not in self.__events:
            self.__events[name] = Event()
        self.__events[name].emit(*args, **kwargs)

class Condition(Events):
    def __init__(self):
        Events.__init__(self)
        self.event = threading.Event()
        self.value = None
    
    def __nonzero__(self):
        return self.event.is_set()
    
    def wait(self, timeout=None):
        self.event.wait(timeout)
    
    def activate(self, value=None):
        self.event.set()
        self.value = value
        self.emit('activate')
        
    def deactivate(self):     
        self.event.clear()
        self.emit('deactivate')
        self.value = None

class Conditions(object):
    def __init__(self):
        self.__conditions = {}
    
    def wait(self, name):
        if name not in self.__conditions:
            self.__conditions[name] = Condition()
        self.__conditions[name].wait()
    
    def activate(self, name, value=None):
        if name not in self.__conditions:
            self.__conditions[name] = Condition()
        self.__conditions[name].activate(value)
    
    def deactivate(self, name):
        if name not in self.__conditions:
            self.__conditions[name] = Condition()
        self.__conditions[name].deactivate()

class ConditionsEvents(Conditions, Events):
    def __init__(self):
        Conditions.__init__(self)
        Events.__init__(self)    