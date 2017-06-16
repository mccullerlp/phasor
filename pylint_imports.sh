#!/usr/bin/env bash
pylint -d I,E,W,R,pe_C --enable syntax-error,import-error,no-name-in-module,missing-module-attribute,syntax-error "$@" | less -R
