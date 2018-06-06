#! /usr/bin/env python
# -*- coding:utf-8 -*-
# wzFelix created on 2018/6/4
import calPs
import numpy as np
import math
import scipy.integrate
import scipy.special
import scipy.misc
import time

class VANET:
    def __init__(self, car_num=200, DIFS=64, sigma=16, W=15, delta=0, Rd=24e+6, Ta=1, R=500, speed=120, pgi=0.5, n=1, x=400):
        self.car_num = car_num                  # No. of terminals，整个感知范围内的车辆数
        self.DIFS = DIFS                        # time period for a DCF inter-frame space
        self.sigma = sigma                      # slot time duration
        self.W = W                              # CSMA backoff window size 15~1024 =====================
        self.delta = delta                      # propagation delay
        self.Rd = Rd                            # data transmission rate ==================
        self.pgi = pgi                          # packet generation rate with possible choices: 1/(2~20) ==============
        self.Ta = Ta                            # app-level time interval
        self.R = R                              # Commuication range ======================
        self.speed = speed                      # Average vehicle speed
        self.x = x                              # 发送节点与接受节点的距离
        self.n = n                              # 保证接收包的个数
        self.NN = int(self.Ta / self.pgi)  # Ta时间内最多发送包的个数
        self.H = (128 + 272) * 1e+6 / self.Rd   # formula(5) E[PL]/Rd
        self.P = 1600 * 1e+6 / self.Rd          # formula(5) Lh/Rd
        self.lam = 1 / self.pgi                 # packet generation rate, pgi=packet generation iterval
        self.lamda = self.sigma / self.pgi / 1e+6  # Packet generation rate (unit: packets/slot)
        self.T = self.H + self.P + self.DIFS + self.delta  # backoff timer susbended a time priod of T, 原程序Tc=T
        self.Tss = math.floor((self.H + self.P) / self.sigma)
        self.Tcc = math.floor((self.T + self.sigma) / self.sigma)   # 公式（3） in reconsider vroadcast packet reception rates in ...
        self.beta = self.car_num / self.R / 2         # 车辆密度

        # 计算p0
        self.di = 1
        self.p1 = 1
        while self.di > 0.00001:
            self.p0 = self.p1
            self.tau = 2 * self.p0 / (self.W + 1)         # the packet transmission probability that a mobile vehicle transmits in a slot
            self.p_b = 1 - math.exp(-self.tau * self.car_num) # the probability that the channel is sensed busy by the tagged vehicle, self.car_num=2*self.beta*self.R

            # 差分法求导数
            self.z = np.array([1,1.00001])
            self.G_d = (1-self.p_b)*self.z+self.p_b*self.z**self.Tcc     # 公式（7） in MAC and application-level ...
            sum = np.array([0,0])
            order_Gd = self.G_d**0
            for i in range(self.W):
                # sum = sum+self.G_d ** i # 可以简化运算
                sum = sum + order_Gd
                order_Gd + order_Gd * self.G_d

            self.Q = self.z**self.Tss/self.W * sum
            # Compute service time by numerical way
            der = np.diff(self.Q) / np.diff(self.z)
            mus = 1 / der
            self.p1 = 1
            if self.lamda < mus:    # 区分两个lambda
                self.p1 = self.lamda / mus
            if self.p1 < 0:
                self.p1 = 0
            self.di = abs(self.p1 - self.p0)
        self.Ps = calPs.ps(self.x, self.lam, self.beta, self.T, self.R, self.tau, self.P+self.H)

        # 计算Pa
        sum_Pa = 0
        for i in range(self.n, (self.NN + 1)):
            sum_Pa = sum_Pa + scipy.misc.comb(self.NN, i) * self.Ps ** i * (1 - self.Ps) ** (self.NN - i)
        self.Pa = sum_Pa

if __name__ == '__main__':
    t1 = time.time()
    v = VANET()
    t2 = time.time()
    print(v.Ps, v.Pa, t2-t1)