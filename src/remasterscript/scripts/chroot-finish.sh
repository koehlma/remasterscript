#!/bin/bash

cd ${1}
umount rootdir/dev
umount rootdir/sys
umount rootdir/proc
umount rootdir/mnt-system
rm -rf rootdir/mnt-system
mv rootdir/etc/resolv.conf.bak rootdir/etc/resolv.conf
exit 0
