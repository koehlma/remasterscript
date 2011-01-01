#!/bin/bash

cd ${1}
mount --bind /dev rootdir/dev
mount --bind /sys rootdir/sys
mount --bind /proc rootdir/proc
mkdir rootdir/mnt-system
mount --bind master rootdir/mnt-system
mv rootdir/etc/resolv.conf rootdir/etc/resolv.conf.bak
cp /etc/resolv.conf rootdir/etc/
exit 0
