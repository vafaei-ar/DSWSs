##!/home/gf/packages/anaconda3/bin/python
import matplotlib as mpl
mpl.use('agg')

#from numpy import sqrt as sq
#from numpy import *
import numpy as np

#x = [1,2,3]
#x = [[1,2,3],[1,2,3],[1,2,3],[1,2,3]]
#x = [1,2,3,[1,2]]

#x = np.array([[1,2,3,4],[-1,6,9,4]])
#x = x.T
#x = np.array([1,2,3,np.array([1,2])])
#print(x.shape)
#print(x.dtype)
#print(type(x))
#print(x*x)

#x = np.random.randint(0,100,(10,10))
#x = np.zeros((10,10))
#for i in range(2,10,3):
#    x[i,i]=1
#print(range(3,10))
#print(type(range(3,10)))
#for i in range(3,10):
#    for j in range(10):
#        x[i,j]=1

#for i in range(3,10,3):
#    x[i,:]=1

#try:
#    print(x.shape)
#except:
#    print('The variable is not array.')

#print(x)

import matplotlib.pylab as plt

x = np.arange(0,10,0.1)
#print(x)
#print(x.shape)
y = np.sin(x)

plt.plot(x,y)
#plt.show()
plt.savefig('1.jpg')


