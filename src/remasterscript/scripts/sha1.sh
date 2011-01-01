#!/bin/bash

find $1 -type f -not -name sha1sums -not -name boot.cat -not -name isolinux.bin -exec sha1sum {} \; | sed "s\$${1}\$*\$g" >${2}
exit 0
