#!/bin/sh

cc -march=native -O2 -fPIC -shared -o calc/calc_power.o calc/calc_power.c
cc -march=native -O2 -fPIC -shared -o calc/calc_pdiff.o calc/calc_pdiff.c
