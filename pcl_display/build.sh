#! /bin/bash
rm -rf build
mkdir build
cd build
cmake \
-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
..
make -j4