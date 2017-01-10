#!/usr/bin/env bash

FIXUP=(
        optics.Mirror \
        optics.PD \
        optics.MagicPD \
        optics.Space \
        optics.Laser \
        system.OpticalSystem \
        readouts.DCReadout \
        readouts.ACReadout \
)
for THING in ${FIXUP[@]}; do
    IFS='.' set $THING
    sed -e "s/\([^.]\)\(${2}\)/\1$1\.\2/g" -i *.py
done
