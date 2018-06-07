#! /usr/bin/env python
# -*- coding:utf-8 -*-
# wzFelix created on 2018/6/5
import csma_broad_dsrc
import numpy as np
import copy

class BIRD:
    def __init__(self):
        # get random variables and generate a bird
        self.range_pgi = np.array([1/30, 0.5])
        self.range_Rd = np.array([3, 54])    # need times 1e+6
        self.range_W = np.array([15, 1024])
        self.range_all = np.array([self.range_pgi, self.range_Rd, self.range_W])
        # range_R = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
        self.pgi = (self.range_all[0][1] - self.range_all[0][0]) * np.random.rand() + self.range_all[0][0]
        self.Rd = ((self.range_all[1][1] - self.range_all[1][0]) * np.random.rand() + self.range_all[1][0])
        self.W = (self.range_all[2][1] - self.range_all[2][0]) * np.random.rand() + self.range_all[2][0]
        self.v = np.array([0, 0, 0])    # velocities of pgi, Rd and W
        self.position = np.array([self.pgi, self.Rd, self.W])
        self.pbest_position = self.position.copy()

    def move_to_best_bird(self, gbest_position):
        self.update_velocity(gbest_position=copy.deepcopy(gbest_position))
        self.update_position()

    def update_velocity(self, c1=2, c2=2, gbest_position=None):
        # update velocity of the bird
        if gbest_position is None:   # gbest is a list
            gbest_position = copy.deepcopy(self.pbest_position)
        w = 0.4
        self.v = w * self.v + c1 * np.random.rand() * (self.pbest_position - self.position) + c2 * np.random.rand() * (gbest_position - self.position)

    def update_position(self):
        # update position of the bird
        self.position = self.position + self.v  # 后续工作需要进一步规整为可用值
        for index, val in enumerate(self.position):
            if val > self.range_all[index][1]:
                self.position[index] = self.range_all[index][1]
            elif val < self.range_all[index][0]:
                self.position[index] = self.range_all[index][0]

    def cal_pa(self, n=1):
        bird = csma_broad_dsrc.VANET(pgi=self.position[0], Rd=self.position[1]*1e6, W=self.position[2], n=n)
        self.pa = bird.Pa
        return self.pa

class SWARM:
    def __init__(self, threshold=0.95, birds_num=50, least_package_receive=1, distance=400):
        self.birds_num = int(birds_num)
        self.init_swarm()
        self.threshold = threshold
        self.n = least_package_receive
        self.x = distance
        self.satisfied_birds = []    # 元素为满足要求的粒子
        self.is_first_iteration = False
        # self.pa = 0
        self.gbest_bird = None
        self.history_of_best_bird = []

    def init_swarm(self):
        self.swarm = []     # 元素为粒子实例
        for i in range(self.birds_num):
            self.swarm.append(BIRD())

    def find_satisfied_threshold_birds(self):
        # 元素为满足要求的粒子
        # self.satisfied_birds = []
        # for i in self.swarm:
        #     if i.cal_pa(n=self.n) >= self.threshold:
        #         self.satisfied_birds.append(i)
        self.satisfied_birds = [copy.deepcopy(bird) for bird in self.swarm if bird.cal_pa(n=self.n) >= self.threshold]
        # print('find a {num} birds satisfied the threshold'.format(num=len(self.satisfied_birds)))
        # for i in self.satisfied_birds:
        #     print('bird\'s pgi = {pgi}'.format(pgi=i.pgi))
        # with open('log.txt','a+') as f:
        #     f.write('find a {num} birds satisfied the threshold'.format(num=len(self.satisfied_birds)))
        #     for i in self.satisfied_birds:
        #         f.writelines('bird\'s pgi = {pgi}\n'.format(pgi=i.pgi))

    def find_smallest_pgi_bird(self):
        # smallest_pgi_bird = copy.deepcopy(self.satisfied_birds[0])
        # for bird in self.satisfied_birds:
        #     if bird.pgi < smallest_pgi_bird.pgi:
        #         smallest_pgi_bird = copy.deepcopy(bird)
        # return smallest_pgi_bird
        return copy.deepcopy(min(self.satisfied_birds, key=lambda x:x.pgi))

    def minimize_pgi(self, iterations=50, first_round_nums=50):
        for i in range(iterations):
            if i == 0:  # 如果为第一次迭代，须确保self.satisfied_bird不为空
                for times in range(first_round_nums):
                    self.init_swarm()
                    self.find_satisfied_threshold_birds()
                    if len(self.satisfied_birds) == 0:
                        print('this is {times} times run without a bird meets the Pa requirements'.format(times=times+1))
                        biggest_Pa_bird = copy.deepcopy(max(self.swarm, key=lambda x:x.pa))
                        print('the biggest Pa is {0}, but the threshold is {1}'.format(biggest_Pa_bird.pa, self.threshold))
                        continue
                    else:
                        print('this is {times} times iterarion,\nthere are {num} bird(s) meet the Pa requirements'.format(times=times + 1, num=len(self.satisfied_birds)))
                        break
            else:
                # 根据上一轮结果更新所有粒子的位置
                for bird in self.swarm:
                    bird.move_to_best_bird(gbest_position=self.gbest_bird.position)
                self.find_satisfied_threshold_birds()

            if self.gbest_bird is None:  # 第一次循环gbest_bird为空
                self.gbest_bird = copy.deepcopy(self.satisfied_birds[0])
            current_smallest_pgi_bird = copy.deepcopy(self.find_smallest_pgi_bird())

            # 更新全局最优粒子
            if current_smallest_pgi_bird.pgi < self.gbest_bird.pgi:
                self.gbest_bird = copy.deepcopy(current_smallest_pgi_bird)

            # 更新各个粒子的自身最优位置
            for bird in self.satisfied_birds:
                if bird.pgi < bird.pbest_position[0]:
                    bird.pbest_position = copy.deepcopy(bird.position)

            # with open('log.txt','a+') as f:
            #     f.writelines('the {time} iteration\n'.format(time=i))
            #     for bird in self.swarm:
            #         f.writelines("pgi = {pgi}, Rd = {Rd}, W = {W}\n".format(pgi=bird.position[0], Rd=bird.position[1], W=bird.position[2]))


if __name__ == "__main__":
    """
    QoS requirements of three typical safety-related applications:
    cooperation collision warning (CCW)    Pa>= 99.0% with d = 400 m and n = 1
    slow vehicle indication(SVI)           Pa>= 99.9% with d = 100 m and n = 3
    rear-end collision warning(RCW)        Pa>= 99.9% with d = 50  m and n = 5
    """
    # ccw = SWARM(threshold=0.99, birds_num=50, least_package_receive=1, distance=400)
    # ccw.minimize_pgi(iterations=50)

    svi = SWARM(threshold=0.999, birds_num=50, least_package_receive=3, distance=100)
    svi.minimize_pgi(iterations=50)

    # 暂时无法满足
    # rcw = SWARM(threshold=0.999, birds_num=50, least_package_receive=5, distance=50)
    # rcw.minimize_pgi(iterations=50, first_round_nums=1000)
