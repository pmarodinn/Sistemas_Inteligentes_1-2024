# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the explorer goes back to the base.

import sys
import os
import random
import math
from abc import ABC, abstractmethod
import time
from search import search
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return (False, self.items.pop())
        return (True, (0, 0))

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    def __init__(self, env, config_file, manager):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()
        self.set_state(VS.ACTIVE)  
        self.manager = manager
        self.x = 0
        self.y = 0
        self.map = Map()
        self.victims = []
        self.explored = []
        self.finished = False
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, [])
        self.comeback_plan = []
        self.coming_back = False

    # returns the next directions, whether it returned to the previous position, and whether the base was reached
    def get_next_position(self) -> tuple[int, int, bool, bool]:
        obstacles = self.check_walls_and_lim()
        for dir in self.directions:
            dx, dy = Explorer.AC_INCR[dir]
            next_tile = (self.x + dx, self.y + dy)
            if obstacles[dir] != VS.CLEAR:
                self.map.add(next_tile, VS.OBST_WALL, VS.NO_VICTIM, []) 
                continue
            if next_tile not in self.explored:
                self.explored.append(next_tile)
                return (dx, dy, False, False)

        stack_empty, (next_x, next_y) = self.walk_stack.pop()
        next_x *= -1
        next_y *= -1
        return (next_x, next_y, True, stack_empty)
    
    def explore(self):
        # popped_stack indica se a proxima posicao é uma coordenada nova ou se o explorador desempilhou da walk_stack
        dx, dy, popped_stack, stack_empty = self.get_next_position()

        if stack_empty:
            self.finished = True
            return
        
        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        if result == VS.BUMPED:
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, [])

        if result == VS.EXECUTED:
            if not popped_stack:
                self.walk_stack.push((dx, dy))

            self.x += dx
            self.y += dy          

            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                victim = {
                    "seq": vs[0],
                    "position": (self.x, self.y),
                    "data": {
                        "qPA": vs[3],
                        "pulse": vs[4],
                        "respiratory_freq": vs[5],
                    },
                }
                self.victims.append(victim)
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            self.map.add((self.x, self.y), difficulty, seq, [])

        return

    def come_back(self):
        print("COMING BACK")
        print(self.comeback_plan)
        if len(self.comeback_plan) == 0:
            return

        (dx, dy, f) = self.comeback_plan.pop(0)

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            self.x += dx
            self.y += dy
        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        comeback_plan, required_time = search(self, self.map, (self.x, self.y), (0, 0))
        if required_time < self.get_rtime() - 40 and not self.finished:
            self.explore()
            return True

        self.coming_back = True
        self.comeback_plan = comeback_plan

        if self.coming_back:
            self.come_back()

            if self.x == 0 and self.y == 0:
                self.manager.add_victims(self.victims)
                self.manager.add_map(self.map)
                return False
            return True

        return True

