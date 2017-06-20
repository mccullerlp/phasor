#!/usr/bin/env bash
pylint -d ps_In,E,W,R,pe_C --enable syntax-error,import-error,no-name-in-module,missing-module-attribute,syntax-error "$@" | less -R
