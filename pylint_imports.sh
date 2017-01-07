#!/usr/bin/env bash
pylint -d I,E,W,R,C --enable import-error,no-name-in-module,missing-module-attribute BGSF/ | less -R
