#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -shared -fPIC -o _erdos_fast.so _erdos_fast.c
echo "Built _erdos_fast.so"
