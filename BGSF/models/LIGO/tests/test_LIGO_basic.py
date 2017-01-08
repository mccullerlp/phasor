from __future__ import print_function
import BGSF.utilities.version as version
print(version.foundations_version())

from declarative.bunch import (
    Bunch,
)

from BGSF.optics import (
    OpticalFrequency,
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
    VacuumTerminator,
)

from BGSF.base import (
    Frequency,
)

from BGSF.signals import (
    SignalGenerator,
    Mixer,
    #RMSMixer,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
    ACReadout,
    NoiseReadout,
)

from BGSF.models.LIGO.ligo_sled import (
    LIGOBasicOperation
)


def test_LIGO_basic():
    sys = OpticalSystem(
        freq_order_max_default = 1,
    )
    sys.sled.det = LIGOBasicOperation()
    sol = sys.solve()

if __name__ == '__main__':
    test_LIGO_basic()
