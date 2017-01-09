#!/usr/bin/env bash

FIXUP=(
    OpticalPortHolderOut \
    SignalPortHolderOut \
    OpticalOriented2PortMixin \
    OpticalNonOriented1PortMixin \
)
for THING in ${FIXUP[@]}; do
    sed -e "s/\([^.]\)\(${THING}\)/\1ports\.\2/g" -i *.py
done
