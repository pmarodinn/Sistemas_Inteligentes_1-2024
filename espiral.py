import os
import math
from vs.AbstAgent import AbstAgent
from vs.Environment1 import Environment

class ExplorerAgent(AbstAgent):
    def __init__(self, name, config_file):
        super().__init__(name, config_file)
        self.explored_cells = set()
        self.victim_locations = []
        self.current_position = (0, 0)
        self.direction = 0  # 0: right, 1: down, 2: left, 3: up
    
    def deliberate(self):
        if self.time_used < self.time_limit:
            self.explore()
        else:
            self.set_state('ENDED')
    
    def explore(self):
        if self.current_position not in self.explored_cells:
            self.explored_cells.add(self.current_position)
            x, y = self.current_position
            if self.read_victim_signals(x, y):
                self.victim_locations.append((x, y))
            dx, dy = self.get_next_move()
            self.move(dx, dy)
            self.current_position = (self.current_position[0] + dx, self.current_position[1] + dy)
    
    def get_next_move(self):
        dx, dy = 0, 0
        if self.direction == 0:  # right
            dx, dy = 1, 0
        elif self.direction == 1:  # down
            dx, dy = 0, 1
        elif self.direction == 2:  # left
            dx, dy = -1, 0
        elif self.direction == 3:  # up
            dx, dy = 0, -1

        if self.current_position[0] + dx < 0 or self.current_position[0] + dx >= Environment.GRID_WIDTH or \
                self.current_position[1] + dy < 0 or self.current_position[1] + dy >= Environment.GRID_HEIGHT:
            self.direction = (self.direction + 1) % 4
        return dx, dy

class RescuerAgent(AbstAgent):
    def __init__(self, name, config_file):
        super().__init__(name, config_file)
        self.victim_clusters = []
    
    def deliberate(self):
        if self.time_used < self.time_limit:
            self.rescue_victims()
        else:
            self.set_state('ENDED')
    
    def rescue_victims(self):
        unified_map = self.get_unified_map()
        self.victim_clusters = self.cluster_victims(unified_map)
        self.assign_victim_clusters()
        for cluster in self.victim_clusters:
            for victim_pos in cluster:
                x, y = victim_pos
                self.move_to(x, y)
                self.provide_first_aid(x, y)
    
    def get_unified_map(self):
        # Implementação para unificar os mapas dos exploradores (por exemplo, considerando a probabilidade de ocorrência de vítimas)
        unified_map = [[0] * Environment.GRID_HEIGHT for _ in range(Environment.GRID_WIDTH)]
        for explorer in self.environment.agents:
            for x, y in explorer.victim_locations:
                unified_map[x][y] += 1  # Incrementa a contagem de vítimas na posição (x, y)
        return unified_map
    
    def cluster_victims(self, victim_map):
        # Implementação de um algoritmo de clustering (por exemplo, K-Means ou DBSCAN)
        # Aqui, vamos simplesmente criar um cluster para cada célula com uma vítima
        clusters = []
        for x in range(Environment.GRID_WIDTH):
            for y in range(Environment.GRID_HEIGHT):
                if victim_map[x][y] > 0:
                    clusters.append([(x, y)])
        return clusters
    
    def assign_victim_clusters(self):
        # Atribui os clusters de vítimas aos agentes socorristas
        rescuers = [agent for agent in self.environment.agents if isinstance(agent, RescuerAgent)]
        for i, cluster in enumerate(self.victim_clusters):
            rescuer = rescuers[i % len(rescuers)]  # Atribui de forma circular
            rescuer.victim_clusters.append(cluster)

def main():
    env = Environment()
    explorer_agent = ExplorerAgent('Explorer', 'explorer_config.txt')
    rescuer_agent = RescuerAgent('Rescuer', 'rescuer_config.txt')
    env.add_agent(explorer_agent)
    env.add_agent(rescuer_agent)
    env.run()

if __name__ == "__main__":
    main()
