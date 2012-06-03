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

import hashlib
import json
import os.path

versions = {'18a1728dfe7a6a23238c42ff46ff7fbf021e7b5b': 'Knoppix 6.7.1 CD',
            'bfec82fe9d789ed157f666312fa26ba2cb85048f': 'Knoppix 6.7.1 DVD',
            '0c2787693ea6e7a95f6f1ba332782feac8cf604c': 'Knoppix 7.0.1 DVD',
            '9bbbcfd3dca07076d8323f11fad2b284195e4c4f': 'Knoppix 7.0.2 DVD'}

def get_version(source):
    if os.path.exists(os.path.join(source, 'KNOPPIX', 'remaster.info')):
        with open(os.path.join(source, 'KNOPPIX', 'remaster.info')) as input:
            info = json.load(input)
            return info['name'], info['squashfs'], info['base']
    elif os.path.exists(os.path.join(source, 'KNOPPIX', 'sha1sums')):
        with open(os.path.join(source, 'KNOPPIX', 'sha1sums')) as input:
            hash = hashlib.sha1(input.read()).hexdigest()
            if hash in versions:
                return versions[hash], False, 'Unknown'
    return 'Unknown', None, 'Unknown'
        
        