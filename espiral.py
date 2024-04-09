import os
import math
from vs.AbstAgent import AbstAgent
from vs.Environment1 import Environment
from sklearn.cluster import DBSCAN


class ExplorerAgent(AbstAgent):
    def __init__(self, name, config_file):
        super().__init__(name, config_file)
        self.explored_cells = set()  # Conjunto de células já exploradas
        self.victim_locations = []  # Lista de localizações das vítimas encontradas
        self.current_position = (0, 0)  # Posição atual do agente
        self.direction = 0  # Direção atual do agente (0: direita, 1: baixo, 2: esquerda, 3: cima)
        self.grid_width = Environment.GRID_WIDTH  # Largura do grid
        self.grid_height = Environment.GRID_HEIGHT  # Altura do grid
        self.time_limit = self.config['time_limit']  # Limite de tempo de exploração
        self.communication_channel = []  # Canal de comunicação com os agentes socorristas

    def deliberate(self):
        """
        Método principal do agente, chamado a cada ciclo de deliberação.
        Se o tempo de uso for menor que o limite de tempo, o agente continua explorando.
        Caso contrário, o agente encerra sua atividade.
        """
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
            dx, dy = self.get_next_move(self.get_unified_map())
            self.move(dx, dy)
            self.current_position = (self.current_position[0] + dx, self.current_position[1] + dy)
        self.communicate_victim_locations()

    def get_next_move(self, unified_map):
        """
        Método responsável por determinar a próxima posição a ser explorada.
        O agente se move para a célula não explorada mais próxima de uma área com vítimas.
        """
        min_distance = float('inf')
        best_move = (0, 0)
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            new_x = self.current_position[0] + dx
            new_y = self.current_position[1] + dy
            if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height and (new_x, new_y) not in self.explored_cells:
                distance = self.get_nearest_victim_distance(new_x, new_y, unified_map)
                if distance < min_distance:
                    min_distance = distance
                    best_move = (dx, dy)
        return best_move

    def get_nearest_victim_distance(self, x, y, unified_map):
        """
        Método auxiliar que calcula a distância da célula (x, y) à célula ocupada mais próxima.
        """
        min_distance = float('inf')
        for i in range(self.grid_width):
            for j in range(self.grid_height):
                if unified_map[i][j] > 0:
                    distance = math.sqrt((x - i)**2 + (y - j)**2)
                    if distance < min_distance:
                        min_distance = distance
        return min_distance

    def communicate_victim_locations(self):
        """
        Método responsável por enviar as informações sobre as vítimas encontradas
        para o canal de comunicação, para que os agentes socorristas possam acessá-las.
        """
        for victim_pos in self.victim_locations:
            self.communication_channel.append(victim_pos)

class RescuerAgent(AbstAgent):
    def __init__(self, name, config_file):
        super().__init__(name, config_file)
        self.victim_clusters = []  # Lista de clusters de vítimas
        self.time_limit = self.config['time_limit']  # Limite de tempo de resgate
        self.communication_channel = []  # Canal de comunicação com os agentes exploradores
        self.current_position = (0, 0)  # Posição atual do agente

    def deliberate(self):
        """
        Método principal do agente, chamado a cada ciclo de deliberação.
        Se o tempo de uso for menor que o limite de tempo, o agente continua resgatando as vítimas.
        Caso contrário, o agente encerra sua atividade.
        """
        if self.time_used < self.time_limit:
            self.rescue_victims()
        else:
            self.set_state('ENDED')

    def rescue_victims(self):
        # Obtém as informações sobre as vítimas do canal de comunicação
        self.victim_locations = self.communication_channel.copy()
        self.communication_channel.clear()
        unified_map = self.get_unified_map()
        self.victim_clusters = self.cluster_victims(unified_map)
        self.prioritize_victim_clusters(unified_map)
        self.assign_victim_clusters()
        for cluster in self.victim_clusters:
            for victim_pos in cluster:
                x, y = victim_pos
                path = self.plan_optimal_path(self.current_position, (x, y), unified_map)
                self.follow_path(path)
                self.provide_first_aid(x, y)
                self.current_position = (x, y)

    def get_unified_map(self):
        """
        Método responsável por unificar os mapas individuais dos agentes exploradores.
        Nesta implementação, o mapa unificado é criado incrementando a contagem de vítimas
        em cada célula com base nas informações coletadas pelos exploradores.
        """
        unified_map = [[0] * Environment.GRID_HEIGHT for _ in range(Environment.GRID_WIDTH)]
        for explorer in self.environment.agents:
            for x, y in explorer.victim_locations:
                unified_map[x][y] += 1  # Incrementa a contagem de vítimas na posição (x, y)
        return unified_map

    def cluster_victims(self, victim_map):
        """
        Método responsável por agrupar as vítimas em clusters.
        Nesta implementação, é utilizado o algoritmo de clustering DBSCAN
        para agrupar as vítimas de forma mais robusta.
        """
        # Converter o mapa unificado em uma lista de coordenadas de vítimas
        victim_coords = [(x, y) for x in range(Environment.GRID_WIDTH) for y in range(Environment.GRID_HEIGHT) if victim_map[x][y] > 0]

        # Aplicar o algoritmo de clustering DBSCAN
        dbscan = DBSCAN(eps=2, min_samples=2).fit(victim_coords)
        clusters = [[] for _ in range(max(dbscan.labels_) + 1)]
        for i, label in enumerate(dbscan.labels_):
            if label != -1:  # Ignora os pontos classificados como ruído
                clusters[label].append(victim_coords[i])

        return clusters

    def prioritize_victim_clusters(self, victim_map):
        """
        Método responsável por ordenar os clusters de vítimas com base em heurísticas.
        Nesta implementação, a prioridade é dada aos clusters com maior número de vítimas
        e com menor distância média entre as vítimas.
        """
        self.victim_clusters.sort(key=lambda cluster: (-len(cluster), self.get_cluster_avg_distance(cluster, victim_map)))

    def get_cluster_avg_distance(self, cluster, victim_map):
        """
        Método auxiliar que calcula a distância média entre as vítimas de um cluster.
        """
        total_distance = 0
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                x1, y1 = cluster[i]
                x2, y2 = cluster[j]
                total_distance += math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return total_distance / (len(cluster) * (len(cluster) - 1) / 2)

    def assign_victim_clusters(self):
        """
        Método responsável por atribuir os clusters de vítimas aos agentes socorristas.
        Nesta implementação, os clusters são atribuídos de forma circular aos agentes socorristas.
        """
        rescuers = [agent for agent in self.environment.agents if isinstance(agent, RescuerAgent)]
        for i, cluster in enumerate(self.victim_clusters):
            rescuer = rescuers[i % len(rescuers)]  # Atribui de forma circular
            rescuer.victim_clusters.append(cluster)
"""
    def plan_optimal_path(self, start, end, unified_map):
       
        Método responsável por planejar a rota ótima entre a posição atual do agente
        e a posição da vítima, levando em conta os obstáculos no mapa unificado.
     
        return a_star_search(start, end, unified_map)
"""

    def follow_path(self, path):
        """
        Método responsável por seguir o caminho planejado até a vítima.
        """
        for x, y in path:
            self.move_to(x, y)

def main():
    env = Environment()
    explorer_config = {
        'time_limit': 100  # Tempo limite de exploração
    }
    rescuer_config = {
        'time_limit': 150  # Tempo limite de resgate
    }
    explorer_agent = ExplorerAgent('Explorer', explorer_config)
    rescuer_agent = RescuerAgent('Rescuer', rescuer_config)
    env.add_agent(explorer_agent)
    env.add_agent(rescuer_agent)
    env.run()

if __name__ == "__main__":
    main()
