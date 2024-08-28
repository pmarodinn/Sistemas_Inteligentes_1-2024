from cluster import k_means, save_clusters, save_map, load_map, load_clusters
from map import Map
import neural_network

from vs.constants import DEBUG

class Manager:
    def __init__(self, rescuer_list):
        self.rescuers = rescuer_list
        self.victims = []
        self.map = Map()
        self.map_qtd = 0

    def add_victims(self, victims):
        self.victims = self.victims + victims

    def add_map(self, map):
        match self.map_qtd:
            case 0:
                self.map = map
                self.map_qtd += 1
                print("EXPLORER 1 SENT MAP")
            case 1 | 2:
                self.map.union(map)
                self.map_qtd += 1
                print("EXPLORER 2 or 3 SENT MAP")
            case 3:
                self.map.union(map)
                self.map_qtd += 1
                print("EXPLORER 4 SENT MAP")
                if DEBUG.RESCUER:
                    print("DEBUG RESCUER MODE")
                    clusters = load_clusters()
                    self.map.map_data = load_map()
                    for cluster, rescuer in zip(clusters, self.rescuers):
                        rescuer.go_save_victims(self.map, cluster)
                else:
                    save_map(self.map)
                    self.dispatch_rescuers()

    def dispatch_rescuers(self):
        self.victims = [i for n, i in enumerate(self.victims) if i not in self.victims[n + 1:]]
        self.predict_victims_severity()
        print(self.victims)
        clusters = k_means(self.victims, max_iter = 300)
        for cluster, rescuer in zip(clusters, self.rescuers):
            rescuer.go_save_victims(self.map, cluster[2])
        save_clusters(clusters)

    def predict_victims_severity(self):
        neural_network.predict(self.victims)
