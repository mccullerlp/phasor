
import numpy as np
from numpy import pi

class PD1811Model(object):
    _m = np
    _AmpS12 = 70.0000000000000
    _C_220nF = 2.20000000000000e-7
    _C_PD = 1.50000000000000e-10
    _C_hp = 5.00000000000000e-10
    _C_in_amp = 1.00000000000000e-11
    _LR_gnd = 1.00000000000000e6
    _L_gnd = 0.0000270000000000000
    _R_3_1Ohms = 3.10000000000000
    _R_5Ohms = 5
    _R_gnd = 0.500000000000000
    _Ramp_in = 60
    _Ramp_inPole = 1.00000000000000e6
    _Ramp_inZero = 1.00000000000000e6
    _Z_LM340 = 0

    def __init__(
        self, 
        F,
        AmpS12 = None,
        C_220nF = None,
        C_PD = None,
        C_hp = None,
        C_in_amp = None,
        LR_gnd = None,
        L_gnd = None,
        R_3_1Ohms = None,
        R_5Ohms = None,
        R_gnd = None,
        Ramp_in = None,
        Ramp_inPole = None,
        Ramp_inZero = None,
        Z_LM340 = None,
    ):
        self._F = F
        
        if AmpS12 is not None:
            self._AmpS12 = AmpS12
        if C_220nF is not None:
            self._C_220nF = C_220nF
        if C_PD is not None:
            self._C_PD = C_PD
        if C_hp is not None:
            self._C_hp = C_hp
        if C_in_amp is not None:
            self._C_in_amp = C_in_amp
        if LR_gnd is not None:
            self._LR_gnd = LR_gnd
        if L_gnd is not None:
            self._L_gnd = L_gnd
        if R_3_1Ohms is not None:
            self._R_3_1Ohms = R_3_1Ohms
        if R_5Ohms is not None:
            self._R_5Ohms = R_5Ohms
        if R_gnd is not None:
            self._R_gnd = R_gnd
        if Ramp_in is not None:
            self._Ramp_in = Ramp_in
        if Ramp_inPole is not None:
            self._Ramp_inPole = Ramp_inPole
        if Ramp_inZero is not None:
            self._Ramp_inZero = Ramp_inZero
        if Z_LM340 is not None:
            self._Z_LM340 = Z_LM340
        return
    
    _AmpS11 = None
    @property
    def AmpS11(self):
        if self._AmpS11 is None:
            self._AmpS11 = ((self._x3 - 50)/(self._x3 + 50))
        return self._AmpS11
    
    @AmpS11.setter
    def AmpS11(self, value):
        self._AmpS11 = value
        self._clear_cache()
        return
    
    _Z_DC = None
    @property
    def Z_DC(self):
        if self._Z_DC is None:
            self._Z_DC = (self.R_3_1Ohms + 1/(self._x1 + 1/(self.R_3_1Ohms + 1/(self._x1 + 1/self.R_5Ohms))))
        return self._Z_DC
    
    @Z_DC.setter
    def Z_DC(self, value):
        self._Z_DC = value
        self._clear_cache()
        return
    
    _Z_gnd = None
    @property
    def Z_gnd(self):
        if self._Z_gnd is None:
            self._Z_gnd = (self.LR_gnd*self._x17/(self.LR_gnd + self._x17) + self.R_gnd)
        return self._Z_gnd
    
    @Z_gnd.setter
    def Z_gnd(self, value):
        self._Z_gnd = value
        self._clear_cache()
        return
    
    _ampV_from_Iamp = None
    @property
    def ampV_from_Iamp(self):
        if self._ampV_from_Iamp is None:
            self._ampV_from_Iamp = (self.AmpS12*self._x15*(-50*1j + 100*pi*self.C_PD*self.F*self.Z_DC*self._x19 + 100*pi*self.C_PD*self.F*self.Z_LM340*self._x19 + 100*pi*self.F*self.Z_gnd*(self.C_PD + self.C_hp)))
        return self._ampV_from_Iamp
    
    @ampV_from_Iamp.setter
    def ampV_from_Iamp(self, value):
        self._ampV_from_Iamp = value
        self._clear_cache()
        return
    
    _ampV_from_Ipd = None
    @property
    def ampV_from_Ipd(self):
        if self._ampV_from_Ipd is None:
            self._ampV_from_Ipd = (self.C_hp*self.Z_gnd*self._x16)
        return self._ampV_from_Ipd
    
    @ampV_from_Ipd.setter
    def ampV_from_Ipd(self, value):
        self._ampV_from_Ipd = value
        self._clear_cache()
        return
    
    _ampV_from_VR_trans = None
    @property
    def ampV_from_VR_trans(self):
        if self._ampV_from_VR_trans is None:
            self._ampV_from_VR_trans = (0)
        return self._ampV_from_VR_trans
    
    @ampV_from_VR_trans.setter
    def ampV_from_VR_trans(self, value):
        self._ampV_from_VR_trans = value
        self._clear_cache()
        return
    
    _ampV_from_Vamp = None
    @property
    def ampV_from_Vamp(self):
        if self._ampV_from_Vamp is None:
            self._ampV_from_Vamp = (-self._x16*(-self.C_hp - self.C_in_amp + self.Z_DC*self._x20 + self.Z_LM340*self._x20 - self._x18*self._x6))
        return self._ampV_from_Vamp
    
    @ampV_from_Vamp.setter
    def ampV_from_Vamp(self, value):
        self._ampV_from_Vamp = value
        self._clear_cache()
        return
    
    @property
    def AmpS12(self):
        return self._AmpS12
    
    @AmpS12.setter
    def AmpS12(self, value):
        self._AmpS12 = value
        self._clear_cache()
        return
    
    @property
    def C_220nF(self):
        return self._C_220nF
    
    @C_220nF.setter
    def C_220nF(self, value):
        self._C_220nF = value
        self._clear_cache()
        return
    
    @property
    def C_PD(self):
        return self._C_PD
    
    @C_PD.setter
    def C_PD(self, value):
        self._C_PD = value
        self._clear_cache()
        return
    
    @property
    def C_hp(self):
        return self._C_hp
    
    @C_hp.setter
    def C_hp(self, value):
        self._C_hp = value
        self._clear_cache()
        return
    
    @property
    def C_in_amp(self):
        return self._C_in_amp
    
    @C_in_amp.setter
    def C_in_amp(self, value):
        self._C_in_amp = value
        self._clear_cache()
        return
    
    @property
    def LR_gnd(self):
        return self._LR_gnd
    
    @LR_gnd.setter
    def LR_gnd(self, value):
        self._LR_gnd = value
        self._clear_cache()
        return
    
    @property
    def L_gnd(self):
        return self._L_gnd
    
    @L_gnd.setter
    def L_gnd(self, value):
        self._L_gnd = value
        self._clear_cache()
        return
    
    @property
    def R_3_1Ohms(self):
        return self._R_3_1Ohms
    
    @R_3_1Ohms.setter
    def R_3_1Ohms(self, value):
        self._R_3_1Ohms = value
        self._clear_cache()
        return
    
    @property
    def R_5Ohms(self):
        return self._R_5Ohms
    
    @R_5Ohms.setter
    def R_5Ohms(self, value):
        self._R_5Ohms = value
        self._clear_cache()
        return
    
    @property
    def R_gnd(self):
        return self._R_gnd
    
    @R_gnd.setter
    def R_gnd(self, value):
        self._R_gnd = value
        self._clear_cache()
        return
    
    @property
    def Ramp_in(self):
        return self._Ramp_in
    
    @Ramp_in.setter
    def Ramp_in(self, value):
        self._Ramp_in = value
        self._clear_cache()
        return
    
    @property
    def Ramp_inPole(self):
        return self._Ramp_inPole
    
    @Ramp_inPole.setter
    def Ramp_inPole(self, value):
        self._Ramp_inPole = value
        self._clear_cache()
        return
    
    @property
    def Ramp_inZero(self):
        return self._Ramp_inZero
    
    @Ramp_inZero.setter
    def Ramp_inZero(self, value):
        self._Ramp_inZero = value
        self._clear_cache()
        return
    
    @property
    def Z_LM340(self):
        return self._Z_LM340
    
    @Z_LM340.setter
    def Z_LM340(self, value):
        self._Z_LM340 = value
        self._clear_cache()
        return
    
    @property
    def F(self):
        return self._F
    
    @F.setter
    def F(self, value):
        self._F = value
        self._clear_cache()
        return
    
    __x0 = None
    @property
    def _x0(self):
        if self.__x0 is None:
            self.__x0 = (2.0*pi)
        return self.__x0
    
    @_x0.setter
    def _x0(self, value):
        self.__x0 = value
        self._clear_cache()
        return
    
    __x1 = None
    @property
    def _x1(self):
        if self.__x1 is None:
            self.__x1 = (1j*self.C_220nF*self.F*self._x0)
        return self.__x1
    
    @_x1.setter
    def _x1(self, value):
        self.__x1 = value
        self._clear_cache()
        return
    
    __x10 = None
    @property
    def _x10(self):
        if self.__x10 is None:
            self.__x10 = (self.C_in_amp*self._x8)
        return self.__x10
    
    @_x10.setter
    def _x10(self, value):
        self.__x10 = value
        self._clear_cache()
        return
    
    __x11 = None
    @property
    def _x11(self):
        if self.__x11 is None:
            self.__x11 = (self.AmpS11 - 1)
        return self.__x11
    
    @_x11.setter
    def _x11(self, value):
        self.__x11 = value
        self._clear_cache()
        return
    
    __x12 = None
    @property
    def _x12(self):
        if self.__x12 is None:
            self.__x12 = (self.Z_gnd*self._x11)
        return self.__x12
    
    @_x12.setter
    def _x12(self, value):
        self.__x12 = value
        self._clear_cache()
        return
    
    __x13 = None
    @property
    def _x13(self):
        if self.__x13 is None:
            self.__x13 = (self.C_hp*self._x12)
        return self.__x13
    
    @_x13.setter
    def _x13(self, value):
        self.__x13 = value
        self._clear_cache()
        return
    
    __x14 = None
    @property
    def _x14(self):
        if self.__x14 is None:
            self.__x14 = (2*pi*self.C_PD*self.F*(2*pi*1j*self.F*(-self._x10 + self._x13 - self._x9) + self._x11 + self._x4*self._x7))
        return self.__x14
    
    @_x14.setter
    def _x14(self, value):
        self.__x14 = value
        self._clear_cache()
        return
    
    __x15 = None
    @property
    def _x15(self):
        if self.__x15 is None:
            self.__x15 = (1/(1j*self.AmpS11 + 1j*self._x6*self._x7 - 1j + 2*pi*self.F*(-self.C_PD*self._x12 + self._x10 - self._x13 + self._x9) - self.Z_DC*self._x14 - self.Z_LM340*self._x14))
        return self.__x15
    
    @_x15.setter
    def _x15(self, value):
        self.__x15 = value
        self._clear_cache()
        return
    
    __x16 = None
    @property
    def _x16(self):
        if self.__x16 is None:
            self.__x16 = (100*pi*self.AmpS12*self.F*self._x15)
        return self.__x16
    
    @_x16.setter
    def _x16(self, value):
        self.__x16 = value
        self._clear_cache()
        return
    
    __x17 = None
    @property
    def _x17(self):
        if self.__x17 is None:
            self.__x17 = (1j*self.F*self.L_gnd*self._x0)
        return self.__x17
    
    @_x17.setter
    def _x17(self, value):
        self.__x17 = value
        self._clear_cache()
        return
    
    __x18 = None
    @property
    def _x18(self):
        if self.__x18 is None:
            self.__x18 = (2*pi*1j*self.F*self.Z_gnd)
        return self.__x18
    
    @_x18.setter
    def _x18(self, value):
        self.__x18 = value
        self._clear_cache()
        return
    
    __x19 = None
    @property
    def _x19(self):
        if self.__x19 is None:
            self.__x19 = (self.C_hp*self._x18 + 1)
        return self.__x19
    
    @_x19.setter
    def _x19(self, value):
        self.__x19 = value
        self._clear_cache()
        return
    
    __x2 = None
    @property
    def _x2(self):
        if self.__x2 is None:
            self.__x2 = (1.0*1j*self.F)
        return self.__x2
    
    @_x2.setter
    def _x2(self, value):
        self.__x2 = value
        self._clear_cache()
        return
    
    __x20 = None
    @property
    def _x20(self):
        if self.__x20 is None:
            self.__x20 = (2*pi*self.C_PD*self.F*(-1j*self._x5 + 2*pi*self.F*self.Z_gnd*self._x4))
        return self.__x20
    
    @_x20.setter
    def _x20(self, value):
        self.__x20 = value
        self._clear_cache()
        return
    
    __x3 = None
    @property
    def _x3(self):
        if self.__x3 is None:
            self.__x3 = (self.Ramp_in*(self.Ramp_inZero + self._x2)/(self.Ramp_inPole + self._x2))
        return self.__x3
    
    @_x3.setter
    def _x3(self, value):
        self.__x3 = value
        self._clear_cache()
        return
    
    __x4 = None
    @property
    def _x4(self):
        if self.__x4 is None:
            self.__x4 = (self.C_hp*self.C_in_amp)
        return self.__x4
    
    @_x4.setter
    def _x4(self, value):
        self.__x4 = value
        self._clear_cache()
        return
    
    __x5 = None
    @property
    def _x5(self):
        if self.__x5 is None:
            self.__x5 = (self.C_hp + self.C_in_amp)
        return self.__x5
    
    @_x5.setter
    def _x5(self, value):
        self.__x5 = value
        self._clear_cache()
        return
    
    __x6 = None
    @property
    def _x6(self):
        if self.__x6 is None:
            self.__x6 = (self.C_PD*self._x5 + self._x4)
        return self.__x6
    
    @_x6.setter
    def _x6(self, value):
        self.__x6 = value
        self._clear_cache()
        return
    
    __x7 = None
    @property
    def _x7(self):
        if self.__x7 is None:
            self.__x7 = (200*pi**2*self.F**2*self.Z_gnd*(self.AmpS11 + 1))
        return self.__x7
    
    @_x7.setter
    def _x7(self, value):
        self.__x7 = value
        self._clear_cache()
        return
    
    __x8 = None
    @property
    def _x8(self):
        if self.__x8 is None:
            self.__x8 = (50*self.AmpS11 + 50)
        return self.__x8
    
    @_x8.setter
    def _x8(self, value):
        self.__x8 = value
        self._clear_cache()
        return
    
    __x9 = None
    @property
    def _x9(self):
        if self.__x9 is None:
            self.__x9 = (self.C_hp*self._x8)
        return self.__x9
    
    @_x9.setter
    def _x9(self, value):
        self.__x9 = value
        self._clear_cache()
        return
    
    _cache_variables = (    
        '_ampV_from_Vamp','_ampV_from_VR_trans','_ampV_from_Iamp','_Z_gnd','_ampV_from_Ipd',
        '_AmpS11','_Z_DC','_PD1811Model__x20','_PD1811Model__x19','_PD1811Model__x18',
        '_PD1811Model__x17','_PD1811Model__x16','_PD1811Model__x15','_PD1811Model__x14','_PD1811Model__x13',
        '_PD1811Model__x12','_PD1811Model__x11','_PD1811Model__x10','_PD1811Model__x9','_PD1811Model__x8',
        '_PD1811Model__x7','_PD1811Model__x6','_PD1811Model__x5','_PD1811Model__x4','_PD1811Model__x3',
        '_PD1811Model__x2','_PD1811Model__x1','_PD1811Model__x0',
    )
    
    def _clear_cache(self):
        for varname in self._cache_variables:
            try:
                delattr(self, varname)
            except AttributeError:
                pass
        return
    
