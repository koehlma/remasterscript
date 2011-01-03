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
along with Knoppix-Remaster-Script.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import shlex
import re

import gobject

import const

HANDLE_STDIN = 0
HANDLE_STDOUT = 1
HANDLE_STDERR = 2

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
        if detailed_signal == 'stdin':
            self._handles['stdin'] = gobject.io_add_watch(self._stdin,
                                                            gobject.IO_OUT,
                                                            self._on_stdin,
                                                            priority=self._priority)
        elif detailed_signal == 'stdout':
            self._handles['stdout'] = gobject.io_add_watch(self._stdout,
                                                           gobject.IO_IN | gobject.IO_PRI,
                                                            self._on_stdout,
                                                            priority=self._priority)
        elif detailed_signal == 'stderr':
            self._handles['stderr'] = gobject.io_add_watch(self._stderr,
                                                           gobject.IO_IN | gobject.IO_PRI,
                                                            self._on_stderr,
                                                            priority=self._priority)
        elif detailed_signal == 'close':
            self._handles['close'] = gobject.io_add_watch(self._stdout,
                                                            gobject.IO_ERR | gobject.IO_HUP,
                                                            self._on_close,
                                                            priority=self._priority)
        return gobject.GObject.connect(self, detailed_signal, handler, *args)
        
    def wait(self):
        self._process.wait()
    
    def kill(self):
        self._process.kill()
        
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
        self._process = Process('%s' % (command))
        self._process.connect('close', self._on_close)

    def kill(self):
        self._process.kill()
        
    def wait(self):
        self._process.wait()
        
    def _on_close(self, process, returncode):
        if returncode == 0:
            self.emit('success')
        else:
            self.emit('error', returncode)

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

class ExtractCompressedFs(gobject.GObject):
    def __init__(self, source, target):
        gobject.GObject.__init__(self)
        self._process = Process('"%s" "%s" "%s"' % (const.BINARY_EXTRACT_COMPRESSED_FS,
                                                    source,
                                                    target))
        self._process.connect('stderr', self._on_out)
        self._process.connect('close', self._on_close)
        self._number = re.compile('^[0-9]+')
        
    def kill(self):
        self._process.kill()
        
    def _on_out(self, process, fileno):
        data = self._number.match(fileno.readline())
        if data:
            self.emit('update', int(data.group(0)))
        
    def _on_close(self, process, returncode):
        if returncode == 0:
            self.emit('success')
        else:
            self.emit('error', returncode)
            
gobject.type_register(ExtractCompressedFs)
gobject.signal_new('update',
                        ExtractCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))
gobject.signal_new('success',
                        ExtractCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('error',
                        ExtractCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))

class CreateCompressedFs(gobject.GObject):
    def __init__(self, temp, source, target):
        gobject.GObject.__init__(self)
        self._process = Process('"%s" -B 65536 -f "%s" "%s" "%s"' % (const.BINARY_CREATE_COMPRESSED_FS,
                                                    temp,
                                                    source,
                                                    target))
        self._process.connect('stderr', self._on_out)
        self._process.connect('close', self._on_close)
        self._number = re.compile('[0-9]+')
        
    def kill(self):
        self._process.kill()
        
    def _on_out(self, process, fileno):
        data = fileno.readline().strip().split(' ')
        if len(data) > 8:
            data = self._number.match(data[len(data) - 1])
            if data:
                self.emit('update', int(data.group(0)))
        
    def _on_close(self, process, returncode):
        if returncode == 0:
            self.emit('success')
        else:
            self.emit('error', returncode)
            
gobject.type_register(CreateCompressedFs)
gobject.signal_new('update',
                        CreateCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))
gobject.signal_new('success',
                        CreateCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('error',
                        CreateCompressedFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))

class MkIsoFs(gobject.GObject):
    def __init__(self, options, source, target):
        gobject.GObject.__init__(self)
        self._process = Process('"%s" %s "%s" "%s"' % (const.BINARY_MKISOFS,
                                                            options,
                                                            target,
                                                            source))
        self._process.connect('stderr', self._on_out)
        self._process.connect('close', self._on_close)
        self._number = re.compile('[0-9]+')
        
    def kill(self):
        self._process.kill()
        
    def _on_out(self, process, fileno):
        data = self._number.match(fileno.readline().strip())
        if data:
            self.emit('update', int(data.group(0)))
        
    def _on_close(self, process, returncode):
        if returncode == 0:
            self.emit('success')
        else:
            self.emit('error', returncode)
            
gobject.type_register(MkIsoFs)
gobject.signal_new('update',
                        MkIsoFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))
gobject.signal_new('success',
                        MkIsoFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('error',
                        MkIsoFs,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_INT,))