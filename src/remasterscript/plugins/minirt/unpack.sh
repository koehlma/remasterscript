#!/bin/bash

cd ${1}
cp master/boot/isolinux/minirt.gz ./
gunzip minirt.gz
mv minirt minirt.cpio
mkdir minirt
cd minirt
cpio -imd --no-absolute-filenames <../minirt.cpio
rm -f ../minirt.cpio
exit 0
