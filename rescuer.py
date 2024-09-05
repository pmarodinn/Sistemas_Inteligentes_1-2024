##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim
### Not a complete version of DFS; it comes back prematuraly
### to the base when it enters into a dead end position


import json
import os
import random
from textwrap import indent
from time import sleep
import matplotlib.pyplot as plt

from pandas.core.reshape.merge import uuid
from map import Map
from search import search
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS, DATA
from genetic import (
    apply_natural_selection,
    eval_seq_light,
    initialize_random,
    reproduce_pop,
    mutate_pop,
    select_best,
    apply_natural_selection,
    seq_list2dict,
)
from abc import ABC, abstractmethod
from cluster import k_means, save_clusters

GENERATIONS = 80
POP_SIZE = 300
PLOT_GEN_SCORE = False 
SAVE_RESC_SEQ = True

## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    seqs = 0
    def __init__(self, env, config_file):
        """
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map = Map()  # explorer will pass the map
        self.victims = {}  # list of found victims
        self.plan = []  # a list of planned actions
        self.plan_x = 0  # the x position of the rescuer during the planning phase
        self.plan_y = 0  # the y position of the rescuer during the planning phase
        self.plan_visited = set()  # positions already planned to be visited
        self.plan_rtime = self.TLIM  # the remaing time during the planning phase
        self.plan_walk_time = 0.0  # previewed time to walk during rescue
        self.x = 0  # the current x position of the rescuer when executing the plan
        self.y = 0  # the current y position of the rescuer when executing the plan
        self.map_qtd = 0  # the initial number of maps a rescuer has is 0
        

        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

    def go_save_victims(self, map, victims):
        """The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""

        print(f"\n\n*** R E S C U E R ***")
        self.map = map
        self.victims = victims
        import json

        #print(json.dumps(self.victims, indent=4))
        self.__planner()
        i = 1
        self.plan_x = 0
        self.plan_y = 0
        for a in self.plan:
            self.plan_x += a[0]
            self.plan_y += a[1]
            i += 1

        print(f"{self.NAME} END OF PLAN")

        self.set_state(VS.ACTIVE)

    def __depth_search(self, actions_res):
        enough_time = True
        for i, ar in enumerate(actions_res):

            if ar != VS.CLEAR:
                continue
            dx, dy = Rescuer.AC_INCR[i]  # get the increments for the possible action
            target_xy = (self.plan_x + dx, self.plan_y + dy)

            if not self.map.in_map(target_xy):
                continue

            if target_xy in self.plan_visited:
                continue

            self.plan_x += dx
            self.plan_y += dy
            difficulty, vic_seq, next_actions_res = self.map.get(
                (self.plan_x, self.plan_y)
            )
            if dx == 0 or dy == 0:
                step_cost = self.COST_LINE * difficulty
            else:
                step_cost = self.COST_DIAG * difficulty

            # print(f"{self.NAME}: difficulty {difficulty}, step cost {step_cost}")
            # print(f"{self.NAME}: accumulated walk time {self.plan_walk_time}, rtime {self.plan_rtime}")

            # check if there is enough remaining time to walk back to the base
            if self.plan_walk_time + step_cost > self.plan_rtime:
                enough_time = False
                # print(f"{self.NAME}: no enough time to go to ({self.plan_x}, {self.plan_y})")

            if enough_time:
                # the rescuer has time to go to the next position: update walk time and remaining time
                self.plan_walk_time += step_cost
                self.plan_rtime -= step_cost
                self.plan_visited.add((self.plan_x, self.plan_y))

                if vic_seq == VS.NO_VICTIM:
                    self.plan.append((dx, dy, False))  # walk only
                    # print(f"{self.NAME}: added to the plan, walk to ({self.plan_x}, {self.plan_y}, False)")

                if vic_seq != VS.NO_VICTIM:
                    # checks if there is enough remaining time to rescue the victim and come back to the base
                    if self.plan_rtime - self.COST_FIRST_AID < self.plan_walk_time:
                        print(f"{self.NAME}: no enough time to rescue the victim")
                        enough_time = False
                    else:
                        self.plan.append((dx, dy, True))
                        # print(f"{self.NAME}:added to the plan, walk to and rescue victim({self.plan_x}, {self.plan_y}, True)")
                        self.plan_rtime -= self.COST_FIRST_AID

            # let's see what the agent can do in the next position
            if enough_time:
                self.__depth_search(
                    self.map.get((self.plan_x, self.plan_y))[2]
                )  # actions results
            else:
                return

    def __a_star(self):
        sorted_victims = sorted(self.victims, key=lambda x: x["severity"])
        if len(sorted_victims) == 0:
            return

        population = initialize_random(self.victims, POP_SIZE)
        scores = []
        mean_gen_scores = []
        for i in range(GENERATIONS):
            scores.clear()
            gen_score = 0
            for sequence in population:
                score = eval_seq_light(sequence, self.victims)
                gen_score += score 
                scores.append((score, sequence))

            gen_score = gen_score/POP_SIZE
            mean_gen_scores.append(gen_score)
            selected = select_best(scores)
            children = reproduce_pop(selected)
            population = selected + children
            mutate_pop(population)
        
        if PLOT_GEN_SCORE:
            plt.plot(mean_gen_scores)
            plt.grid()
            plt.xlabel("Geração")
            plt.ylabel("Score médio")
            plt.show()
        
        best = apply_natural_selection(population,self.victims)
        best = best[1]
        best = seq_list2dict(best, self.victims)
        if SAVE_RESC_SEQ:
            self.save_resc_seq(best)

        current_pos = (0, 0)
        for victim in best:
            next_plan, time_required = search(
                self.COST_LINE,
                self.COST_DIAG,
                self.map,
                current_pos,
                victim["position"],
            )
            comeback_plan, time_to_go_back = search(
                self.COST_LINE, self.COST_DIAG, self.map, victim["position"], (0, 0)
            )
            time_required += self.COST_FIRST_AID
            if (
                self.plan_walk_time + time_required + time_to_go_back
                > self.plan_rtime - 40
            ):
                continue
            self.plan_walk_time += time_required
            self.plan = self.plan + next_plan
            current_pos = victim["position"]

        comeback_plan, time_to_go_back = search(
            self.COST_LINE, self.COST_DIAG, self.map, current_pos, (0, 0)
        )
        self.plan = self.plan + comeback_plan

        #print(self.plan)
        return

    def __planner(self):
        """A private method that calculates the walk actions in a OFF-LINE MANNER to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""

        """ This plan starts at origin (0,0) and chooses the first of the possible actions in a clockwise manner starting at 12h.
        Then, if the next position was visited by the explorer, the rescuer goes to there. Otherwise, it picks the following possible action.
        For each planned action, the agent calculates the time will be consumed. When time to come back to the base arrives,
        it reverses the plan."""

        # This is a off-line trajectory plan, each element of the list is a pair dx, dy that do the agent walk in the x-axis and/or y-axis.
        # Besides, it has a flag indicating that a first-aid kit must be delivered when the move is completed.
        # For instance (0,1,True) means the agent walk to (x+0,y+1) and after walking, it leaves the kit.

        self.plan_visited.add(
            (0, 0)
        )  # always start from the base, so it is already visited
        self.__a_star()

    def deliberate(self) -> bool:
        """This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do"""

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
            # input(f"{self.NAME} has finished the plan [ENTER]")
            return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy, there_is_vict = self.plan.pop(0)
        # print(f"{self.NAME} pop dx: {dx} dy: {dy} vict: {there_is_vict}")

        # Walk - just one step per deliberation
        walked = self.walk(dx, dy)

        # Rescue the victim at the current position
        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            # print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")
            # check if there is a victim at the current position
            if there_is_vict:
                rescued = self.first_aid()  # True when rescued
                if rescued:
                    print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")
                else:
                    print(
                        f"{self.NAME} Plan fail - victim not found at ({self.x}, {self.x})"
                    )
        else:
            print(f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")
            print(walked)

        # input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

        return True

    def save_resc_seq(self, sequence):
        file_path = f"./data/sequence/seq{Rescuer.seqs}_{DATA.SCENARIO}.txt"
        Rescuer.seqs += 1
        with open(file_path, 'w', encoding='utf-8') as handler:
            for victim in sequence:
                handler.write(f"{victim["seq"]},{victim["position"][0]},{victim["position"][1]},{victim["severity"]}\n")


