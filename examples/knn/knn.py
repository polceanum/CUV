import cuv_python as cp
import pyublas
import numpy as np

class KNN:
    def __init__(self, data, data_l, k):
        self.k      = k
        self.data   = cp.dev_tensor_float_cm(data)
        self.data_l = data_l
        self.dsq    = cp.dev_tensor_float(self.data.shape[0])
        cp.reduce_to_col(self.dsq,self.data,cp.reduce_functor.ADD_SQUARED)
    def get_distance_matrix(self, test):
        t   = cp.dev_tensor_float_cm(test)
        assert t.shape[1] == self.data.shape[1]
        tsq = cp.dev_tensor_float(t.shape[0])
        cp.reduce_to_col(tsq,t,cp.reduce_functor.ADD_SQUARED)
        p   = cp.dev_tensor_float_cm([self.data.shape[0], t.shape[0]])
        cp.prod(p, self.data, t, 'n','t',-2, 0)
        cp.matrix_plus_col(p,self.dsq)
        cp.matrix_plus_row(p,tsq)
        return p
    def run(self,test):
        p = self.get_distance_matrix(test)
        p *= -1.                # no argmin supported yet
        idx = cp.dev_tensor_uint(test.shape[0])
        cp.reduce_to_row(idx, p, cp.reduce_functor.ARGMAX)
        hidx  = idx.np.reshape(idx.shape[0])
        return self.data_l.reshape(self.data.shape[0])[hidx]
