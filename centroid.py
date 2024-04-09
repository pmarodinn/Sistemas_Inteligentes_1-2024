import random as rd
import matplotlib.pyplot as plt
import numpy as np

def k_means(individuals, size ,clusters = 4, max_iter = 100):
    
    #initiate centroids
    centroids = []
    for _ in range(clusters):
        cx = rd.randint((-1)*size[0], size[0]-1)
        cy = rd.randint((-1)*size[1], size[1]-1)

        centroids.append([cx, cy, []])
    
    changed = True
    it = 0

    while it < max_iter and changed:
        changed = False

        #Clears the individual list of each centroid
        for c in centroids:
            c[2].clear()

        #Finds the closest centroid to each individual
        for ind in individuals:
            min_dist = -1
            closest = -1
            
            # find the closest centroid to that individual
            for i, c in enumerate(centroids):
                c_dist = (c[0] - ind[0])**2 +  (c[1] - ind[1])**2
                if c_dist < min_dist or min_dist == -1:
                    min_dist = c_dist
                    closest = i

            centroids[closest][2].append(ind)

        
        #Calculates the new position for each centroid
        for c in centroids:
            n = len(c[2])
            x, y = 0, 0
            old_x, old_y = c[0], c[1]
            for ind in c[2]:
                x += ind[0]
                y += ind[1]
            
            if n != 0:
                c[0] = x/n
                c[1] = y/n
                if c[0] != old_x or c[1] != old_y:
                    changed = True
            else:
                c[0] = rd.randint((-1)*size[0]/2, size[0]/2)
                c[1] = rd.randint((-1)*size[1]/2, size[1]/2)
            

        it += 1

    return centroids

## Testing for the k_mean algorithm

ix = []
iy = []

# #++
# for _ in range(5):
#     x = rd.randint(30, 50)
#     y = rd.randint(30, 50)
#     ix.append(x)
#     iy.append(y)
#
#
# #+-
# for _ in range(5):
#     x = rd.randint(30, 50)
#     y = (-1)*rd.randint(30, 50)
#     ix.append(x)
#     iy.append(y)
#
#
# #--
# for _ in range(5):
#     x = (-1)*rd.randint(30, 50)
#     y = (-1)*rd.randint(30, 50)
#     ix.append(x)
#     iy.append(y)
#
#
# #-+
# for _ in range(5):
#     x = (-1)*rd.randint(30, 50)
#     y = rd.randint(30, 50)
#     ix.append(x)
#     iy.append(y)
#

for _ in range(30):
    ix.append(rd.randint(-90, 90))
    iy.append(rd.randint(-90, 90))

individuals = []
for i in range(len(ix)):
    individuals.append((ix[i], iy[i]))

centroids = k_means(individuals, (100, 100))

cx = np.zeros(len(centroids))
cy = np.zeros(len(centroids))

for i in range(len(centroids)):
    cx[i] = centroids[i][0]
    cy[i] = centroids[i][0]

plt.figure(figsize=(12,8))
ax = plt.gca()

ax.set_xlim([-100, 100])
ax.set_ylim([-100, 100])

plt.grid()
plt.plot(ix, iy, 'o')
plt.plot(cx, cy, 'x')
plt.show()
