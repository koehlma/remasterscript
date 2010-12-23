#!/bin/bash
gcc -Wall -O2 -s -o extract_compressed_fs extract_compressed_fs.c -lz
gcc -Wall -O2 -s -o create_compressed_fs create_compressed_fs.c -lz
