"""
Class and methods for mppt tracker(s)
"""

class MPPT:
    """
    MPPT class
    """

    def __init__(self,
                 V0 = 0,
                 I0 = 0,
                 step = 0.5     # increment or decrement step size
                 ):

        self.v_k1 = V0
        self.i_k1 = I0
        self.v_ref = V0
        self.step = step


    def _inc_cond(self, v, i):
        """
        Modified incremental conductance
        Shang, L., Guo, H. & Zhu, W. An improved MPPT control strategy based on incremental conductance algorithm.
        Prot Control Mod Power Syst 5, 14 (2020). https://doi.org/10.1186/s41601-020-00161-z
        :param v:
        :param i:
        :return:
        """
        dv = v - self.v_k1
        di = i - self.i_k1
        self.v_k1 = v
        self.i_k1 = i
        if dv == 0:
            if di == 0:
                return self.v_ref
            else:
                if di > 0:
                    self.v_ref += self.step
                    return self.v_ref
                else:
                    self.v_ref -= self.step
                    return self.v_ref
        else:
             l = i + (v * di/dv)
             if l == 0:
                 return self.v_ref
             else:
                 if l > 0:
                     if dv*di > 0:
                         if dv > 0:
                             self.v_ref += self.step
                             return self.v_ref
                         else:
                             self.v_ref -= self.step
                             return self.v_ref
                     else:
                         self.v_ref += self.step
                         return self.v_ref

                 self.v_ref -= self.step
                 return self.v_ref

    def inc_cond(self, v, i):
        self._inc_cond(v,i)
        if self.v_ref < 0:
            self.v_ref = 0
        return self.v_ref

