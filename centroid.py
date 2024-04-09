import random as rd
import matplotlib.pyplot as plt

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

def make_matrix(values, clusters, size):
    mat = []
    for i in range(size):
        mat.append([])
        for j in range(size):
            if j == size/2:
                mat[i].append('|')
            elif i == size/2:
                mat[i].append('-')
            else:
                mat[i].append('.')


    return mat

def print_matrix(mat):
    for line in mat:
        print('\n', end = '')
        for char in line:
            print(char, end = '')




ix = []
iy = []

#++
for _ in range(5):
    x = rd.randint(30, 50)
    y = rd.randint(30, 50)
    ix.append(x)
    iy.append(y)


#+-
for _ in range(5):
    x = rd.randint(30, 50)
    y = (-1)*rd.randint(30, 50)
    ix.append(x)
    iy.append(y)


#--
for _ in range(5):
    x = (-1)*rd.randint(30, 50)
    y = (-1)*rd.randint(30, 50)
    ix.append(x)
    iy.append(y)


#-+
for _ in range(5):
    x = (-1)*rd.randint(30, 50)
    y = rd.randint(30, 50)
    ix.append(x)
    iy.append(y)


individuals = []
for i in range(len(ix)):
    individuals.append((ix[i], iy[i]))

centroids = k_means(individuals, (100, 100))

cx = []
cy = []

for c in centroids:
    cx.append(c[0])
    cy.append(c[1])

plt.figure(figsize=(12,8))
ax = plt.gca()

ax.set_xlim((-100, 100))
ax.set_ylim((-100, 100))

plt.grid()
plt.plot(ix, iy, 'o')
plt.plot(cx, cy, 'x')
plt.show()
