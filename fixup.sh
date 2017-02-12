#!/usr/bin/env bash

#declarative.Bunch \
#    declarative.dproperty \
#    declarative.mproperty \
#    declarative.NOARG     \
#    declarative.OverridableObject \
#    declarative.RelayBool \
#    declarative.RelayValue \
#    declarative.RelayValueRejected \
#    declarative.min_max_validator \
#    declarative.min_max_validator_int \
#    declarative.callbackmethod \
#    declarative.RelayValueCoerced \

FIXUP=(
        optics.Mirror \
        optics.PD \
        optics.MagicPD \
        optics.Space \
        optics.Laser \
        optics.HiddenVariableHomodynePD \
        optics.VacuumTerminator \
        optics.PD \
        signals.SignalGenerator \
        signals.DistributionAmplifier \
        signals.SummingAmplifier \
        signals.TransferFunctionSISO \
        signals.TransferFunctionSISOMechSingleResonance \
        readouts.DCReadout \
        readouts.ACReadout \
        readouts.ACReadoutCLG \
        readouts.HomodyneACReadout \
        base.SystemElementBase \
        base.OOA_ASSIGN \
        base.Frequency \
)
for THING in ${FIXUP[@]}; do
    _IFS=$IFS
    IFS=. TST=(${THING})
    IFS="$_IFS"
    LEFT=${TST[0]}
    RIGHT=${TST[1]}
    for FILE in $(grep --exclude='*.pyc' -l -e "\([^.a-zA-Z0-9]\)\(${RIGHT}\)" -r *)
    do
        sed -e "s/\([^.a-zA-Z0-9]\)\(${RIGHT}\)\([^.a-zA-Z0-9]\)/\1${LEFT}\.\2\3/g" -i "$FILE"
    done
done
