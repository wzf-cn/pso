#! /usr/bin/env python
# -*- coding:utf-8 -*-
# wzFelix created on 2018/6/5
import csma_broad_dsrc
import numpy as np

class BIRD:
    def __init__(self):
        # get random variables and generate a bird
        range_pgi = np.array([1/30, 0.5])
        range_Rd = np.array([3, 54])    # need times 1e+6
        range_W = np.array([15, 1024])
        # range_R = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
        self.pgi = (range_pgi[1] - range_pgi[0]) * np.random.rand() + range_pgi[0]
        self.Rd = ((range_Rd[1] - range_Rd[0]) * np.random.rand() + range_Rd[0])
        self.W = (range_W[1] - range_W[0]) * np.random.rand() + range_W[0]
        self.v = np.array([0, 0, 0])    # velocities of pgi, Rd and W
        self.position = np.array([self.pgi, self.Rd, self.W])
        self.pbest = self.position.copy()

    def update_bird(self, gbest):
        self.update_velocity(gbest=gbest)
        self.update_position()

    def update_velocity(self, c1=0, c2=2, gbest=None):
        # update velocity of the bird
        if gbest is None:
            gbest = self.pbest.copy()
        w = 0.4
        self.v = w * self.v + c1 * np.random.rand() * (self.pbest - self.position) + c2 * np.random.rand() * (gbest - self.position)

    def update_position(self):
        # update position of the bird
        self.position = self.position + self.v  # 后续工作需要进一步规整为可用值

    def update_pbest(self):
        self.pbest = self.position.copy()

    def cal_pa(self, n=1):
        bird = csma_broad_dsrc.VANET(pgi=self.position[0], Rd=self.position[1], W=self.position[2], n=n)
        self.pa = bird.Pa

class SWARM:
    def __init__(self, threshold=0.95, birds_num=50, least_package_receive=1, distance=400):
        self.swarm = []
        for i in range(birds_num):
            self.swarm.append(BIRD())
        self.threshold = threshold
        self.n = least_package_receive
        self.x = distance
        self.satisfied_bird = []

    def find_bird_satisfied_threshold(self):
        for i in self.swarm:
            if i.cal_pa(self.n) >= self.threshold:
                self.satisfied_bird.append(i)

    def bird_has_smallest_pgi(self):
        return smallest_pgi, position

    def minimize_pgi(self, iterations):
        for i in range(iterations):
            self.satisfied_bird = []
            self.find_bird_satisfied_threshold()
            current_pgi, current_position = self.bird_has_smallest_pgi()
            if