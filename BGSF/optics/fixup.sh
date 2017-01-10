#!/usr/bin/env bash

FIXUP=(
    MechanicalPortHolderIn \
    MechanicalPortHolderOut \
    OpticalDegenerate4PortMixin \
)
for THING in ${FIXUP[@]}; do
    sed -e "s/\([^.]\)\(${THING}\)/\1ports\.\2/g" -i *.py
done
