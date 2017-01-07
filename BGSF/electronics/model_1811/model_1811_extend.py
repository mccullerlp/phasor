from model_1811 import PD1811Model
from YALL.utilities.numerics.dispatched import abs_sq, sqrt
import copy


class PD1811ModelExt(PD1811Model):

    _cache_variables = PD1811Model._cache_variables + (
        '_NIpd_sq_from_SN',
        '_NIpd_from_SN',
        '_NVamp_sq_from_SN',
        '_NVamp_from_SN',
        '_NVamp_sq_from_ampI',
        '_NVamp_from_ampI',
        '_NVamp_sq_from_ampV',
        '_NVamp_from_ampV',
        '_NVamp_sq_from_R_trans',
        '_NVamp_from_R_trans',
        '_NVamp_sq_total',
        '_NVamp_total',
    )

    def copy(self, **kwargs):
        new = copy.deepcopy(self)
        for n, val in kwargs.items():
            getattr(new, n) #just check if the thing exists
            setattr(new, n, val)
        return new

    _VDC = 0
    @property
    def VDC(self):
        return self._VDC

    @VDC.setter
    def VDC(self, val):
        self._VDC = val
        self._clear_cache()

    _NIpd_sq_from_SN = None
    @property
    def NIpd_sq_from_SN(self):
        if self._NIpd_sq_from_SN is None:
            self._NIpd_sq_from_SN = (2 * (self.VDC / 10) / 6.24e18)
        return self._NIpd_sq_from_SN

    _NIpd_from_SN = None
    @property
    def NIpd_from_SN(self):
        if self._NIpd_from_SN is None:
            self._NIpd_from_SN = sqrt(self.NIpd_sq_from_SN)
        return self._NIpd_from_SN

    _NVamp_sq_from_SN = None
    @property
    def NVamp_sq_from_SN(self):
        if self._NVamp_sq_from_SN is None:
            self._NVamp_sq_from_SN = self.NIpd_sq_from_SN * abs_sq(self.ampV_from_Ipd)
        return self._NVamp_sq_from_SN

    _NVamp_from_SN = None
    @property
    def NVamp_from_SN(self):
        if self._NVamp_from_SN is None:
            self._NVamp_from_SN = sqrt(self.NVamp_sq_from_SN)
        return self._NVamp_from_SN

    _noise_ampI = 3.5e-12
    @property
    def noise_ampI(self):
        return self._noise_ampI

    @noise_ampI.setter
    def noise_ampI(self, val):
        self._noise_ampI = val
        self._clear_cache()

    _NVamp_sq_from_ampI = None
    @property
    def NVamp_sq_from_ampI(self):
        if self._NVamp_sq_from_ampI is None:
            self._NVamp_sq_from_ampI = abs_sq(self.noise_ampI * self.ampV_from_Iamp)
        return self._NVamp_sq_from_ampI

    _NVamp_from_ampI = None
    @property
    def NVamp_from_ampI(self):
        if self._NVamp_from_ampI is None:
            self._NVamp_from_ampI = sqrt(self.NVamp_sq_from_ampI)
        return self._NVamp_from_ampI

    _noise_ampV = 1.2e-9
    @property
    def noise_ampV(self):
        return self._noise_ampV

    @noise_ampV.setter
    def noise_ampV(self, val):
        self._noise_ampV = val
        self._clear_cache()

    _NVamp_sq_from_ampV = None
    @property
    def NVamp_sq_from_ampV(self):
        if self._NVamp_sq_from_ampV is None:
            self._NVamp_sq_from_ampV = abs_sq(self.noise_ampV * self.ampV_from_Iamp)
        return self._NVamp_sq_from_ampV

    _NVamp_from_ampV = None
    @property
    def NVamp_from_ampV(self):
        if self._NVamp_from_ampV is None:
            self._NVamp_from_ampV = sqrt(self.NVamp_sq_from_ampV)
        return self._NVamp_from_ampV

    _NVamp_sq_from_R_trans= None
    @property
    def NVamp_sq_from_R_trans(self):
        if self._NVamp_sq_from_R_trans is None:
            self._NVamp_sq_from_R_trans = (4.07e-9)**2 * (self.R_trans / 1e3) * abs_sq(self.ampV_from_VR_trans)
        return self._NVamp_sq_from_R_trans

    _NVamp_from_R_trans = None
    @property
    def NVamp_from_R_trans(self):
        if self._NVamp_from_R_trans is None:
            self._NVamp_from_R_trans = sqrt(self.NVamp_sq_from_R_trans)
        return self._NVamp_from_R_trans

    _NVamp_sq_total = None
    @property
    def NVamp_sq_total(self):
        if self._NVamp_sq_total is None:
            self._NVamp_sq_total = self.NVamp_sq_from_SN + self.NVamp_sq_from_ampI + self.NVamp_sq_from_ampV
        return self._NVamp_sq_total 

    _NVamp_total = None
    @property
    def NVamp_total(self):
        if self._NVamp_total is None:
            self._NVamp_total = sqrt(self.NVamp_sq_total)
        return self._NVamp_total 

