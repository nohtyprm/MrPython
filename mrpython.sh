#!/bin/bash

python3 "$(dirname $(readlink -f))"/mrpython/Application.py $*
