# -*- coding:utf8 -*-
"""
This file is part of Knoppix-Remaster-Script.

Knoppix-Remaster-Script is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Knoppix-Remaster-Script is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Knoppix-Remaster-Script. If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import shlex
import re

import gobject

import const

class Process(gobject.GObject):
    def __init__(self, command, priority=gobject.PRIORITY_LOW):
        gobject.GObject.__init__(self)
        self._command = shlex.split(command)
        self._priority = priority
        self._process = subprocess.Popen(self._command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._stdin = self._process.stdin
        self._stdout = self._process.stdout
        self._stderr = self._process.stderr
        self._handles = {}
        self._buffer = []
    
    def connect(self, detailed_signal, handler, *args):
        if detailed_signal == 'stdin' and 'stdin' not in self._handles:
            self._handles['stdin'] = gobject.io_add_watch(self._stdin,
                                                            gobject.IO_OUT,
                                                            self._on_stdin,
                                                            priority=self._priority)
        elif detailed_signal == 'stdout' and 'stdout' not in self._handles:
            self._handles['stdout'] = gobject.io_add_watch(self._stdout,
                                                           gobject.IO_IN | gobject.IO_PRI,
                                                            self._on_stdout,
                                                            priority=self._priority)
        elif detailed_signal == 'stderr' and 'stderr' not in self._handles:
            self._handles['stderr'] = gobject.io_add_watch(self._stderr,
                                                           gobject.IO_IN | gobject.IO_PRI,
                                                            self._on_stderr,
                                                            priority=self._priority)
        elif detailed_signal == 'close' and 'close' not in self._handles:
            self._handles['close'] = gobject.io_add_watch(self._stdout,
                                                            gobject.IO_ERR | gobject.IO_HUP,
                                                            self._on_close,
                                                            priority=self._priority)
        return gobject.GObject.connect(self, detailed_signal, handler, *args)
        
    def wait(self):
        return self._process.wait()
    
    def kill(self):
        return self._process.kill()
    
    def poll(self):
        return self._process.poll()
        
    def write(self, string):
        self._buffer.append(string)
    
    def _on_close(self, fileno, condition):
        self._process.wait()
        if 'stdin' in self._handles:
            gobject.source_remove(self._handles['stdin'])
        if 'stdout' in self._handles:
            gobject.source_remove(self._handles['stdout'])
        if 'stderr' in self._handles:
            gobject.source_remove(self._handles['stderr'])
        self.emit('close', self._process.returncode)
        return False
    
    def _on_stdin(self, fileno, condition):
        self.emit('stdin', fileno)
        if self._buffer:
            for string in self._buffer:
                fileno.write(string)
                self._buffer.remove(string)
            self._buffer = None
        return True
    
    def _on_stdout(self, fileno, condition):
        self.emit('stdout', fileno)
        return True
    
    def _on_stderr(self, fileno, condition):
        self.emit('stderr', fileno)
        return True

def register_Process():

    gobject.type_register(Process)
    gobject.signal_new('stdin',
                            Process,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_PYOBJECT,))
    gobject.signal_new('stdout',
                            Process,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_PYOBJECT,))
    gobject.signal_new('stderr',
                            Process,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_PYOBJECT,))
    gobject.signal_new('close',
                            Process,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_INT,))

class Util(gobject.GObject):
    def __init__(self, command):
        gobject.GObject.__init__(self)
        print 'command'
        print command
        self._process = Process(command)
        self._process.connect('close', self._on_close)
    
    def kill(self):
        return self._process.kill()
    
    def wait(self):
        return self._process.wait()
    
    def poll(self):
        return self._process.poll()
        
    def _on_close(self, process, returncode):
        if returncode == 0:
            self.emit('success')
        else:
            self.emit('error', returncode)

def register_Util():
    gobject.type_register(Util)
    gobject.signal_new('success',
                            Util,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            ())
    gobject.signal_new('error',
                            Util,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_INT,))

class UpdateUtil(Util):
    def __init__(self, command):
        Util.__init__(self, command)

def register_UpdateUtil():
    gobject.type_register(UpdateUtil)
    gobject.signal_new('update',
                            UpdateUtil,
                            gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_BOOLEAN,
                            (gobject.TYPE_PYOBJECT,))

register_Process()
register_Util()
register_UpdateUtil()

class ExtractCompressedFs(UpdateUtil):
    def __init__(self, source, target):
        self._source = source
        self._target = target
        self._number = re.compile('^[0-9]+')
        UpdateUtil.__init__(self, '"%s" "%s" "%s"' % (const.BINARY_EXTRACT_COMPRESSED_FS,
                                                            self._source,
                                                            self._target))
        self._process.connect('stderr', self._on_out)
       
    def _on_out(self, process, fileno):
        data = self._number.match(fileno.readline())
        if data:
            self.emit('update', int(data.group(0)))

class CreateCompressedFs(Util):
    def __init__(self, source, target):
        print 'create compressed fs'
        self._source = source
        self._target = target
        print 'starting util'
        Util.__init__(self, '"%s" "%s" "%s" %s' % (const.BINARY_CREATE_COMPRESSED_FS,
                                                                    self._source,
                                                                    self._target,
                                                                    const.CREATE_COMPRESSED_FS_OPTIONS))
class Copy(Util):
    def __init__(self, options, sources, target):
        self._options = options
        self._target = target
        if type(sources) == tuple or type(sources) == list:
            sources_quote = []
            for source in sources:
                sources_quote.append('"' + source + '"')
            self._source = ' '.join(sources_quote)
        else:
            self._source = sources
        Util.__init__(self, '"%s" %s %s "%s"' % (const.BINARY_COPY,
                                                        self._options,
                                                        self._source,
                                                        self._target))

class Mount(Util):
    def __init__(self, options, source, target):
        self._options = options
        self._source = source
        self._target = target
        Util.__init__(self, '"%s" %s "%s" "%s"' % (const.BINARY_MOUNT,
                                                    self._options,
                                                    self._source,
                                                    self._target))

class Umount(Util):
    def __init__(self, path):
        self._path = path
        Util.__init__(self, '"%s" "%s"' % (const.BINARY_UMOUNT,
                                                    self._path))

#class MountManager(gobject.GObject): pass

class Remove(Util):
    def __init__(self, options, paths):
        self._options = options
        paths_quote = []
        if type(paths) == tuple or type(paths) == list:
            for path in paths:
                paths_quote.append('"' + path + '"')
            self._path = ' '.join(paths_quote)
        else:
            self._path = paths
        Util.__init__(self, '"%s" %s %s' % (const.BINARY_REMOVE,
                                                self._options,
                                                self._path))

class MkIsoFs(UpdateUtil):
    def __init__(self, options, source, target):
        self._options = options
        self._source = source
        self._target = target
        self._number = re.compile('[0-9]+')
        UpdateUtil.__init__(self, '"%s" %s "%s" "%s"' % (const.BINARY_MKISOFS,
                                                            self._options,
                                                            self._target,
                                                            self._source))
        self._process.connect('stderr', self._on_out)
        
    def _on_out(self, process, fileno):
        data = self._number.match(fileno.readline().strip())
        if data:
            self.emit('update', int(data.group(0)))
