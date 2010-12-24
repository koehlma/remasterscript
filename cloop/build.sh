#!/bin/bash
gcc -Wall -O2 -s -o extract_compressed_fs extract_compressed_fs.c -lz
cd cloop-2.634
make
cd ../
cp cloop-2.634/create_compressed_fs ./
