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
    LEFT=${THING##}
    RIGHT=${THING//.*\.//}
    echo -e "s/\([^.]\)\(${RIGHT}\)/\1${LEFT}\.\2/g" -i *.py
done
