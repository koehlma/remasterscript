#!/bin/bash

cd ${1}
cd minirt
find . | cpio -oH newc | gzip -9 >../master/boot/isolinux/minirt.gz
cd ../
rm -rf minirt
exit 0
