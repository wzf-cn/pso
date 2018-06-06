#! /usr/bin/env python
# -*- coding:utf-8 -*-
# wzFelix created on 2018/6/4
import math
import scipy.integrate
import scipy.special

def ps(x, lam, beta, T, R, tau, PH):
    # ps is PRP

    PH1 = 1 - x*lam*beta*T*1e-6*(1+math.exp(-beta*R*tau))/2

    PH2 = math.exp(-lam*beta*x*PH*1e-6)    # 未统一单位

    nT = beta*tau*(R-x) - 0.5*lam*beta**2*tau*T*1e-6*(R-x)**2*0.5*(1+math.exp(-beta*R*tau))
    n_sum = nT + beta*R*tau
    Pconc = math.exp(-n_sum)

    m = 1.
    if x < 50:
        m = 3.
    elif x < 150:
        m = 1.5
    f = lambda z: z**(m-1) * math.exp(-x**2*m*z)
    inte = scipy.integrate.quad(f, 0, 1./(R**2))[0]
    PF = 1 - ((x**2)*m)**m/scipy.special.gamma(m)*inte

    return PH1*PH2*Pconc*PF


