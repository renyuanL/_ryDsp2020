# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 09:09:45 2020

@author: renyu
"""
import numpy as np
import matplotlib.pyplot as pl
import scipy.signal as sp

x=[1,2,3,4,5,6,7,8,9,0,0,0]


n= np.arange(10)
x= np.cos(2*np.pi*1/10*n)

x= np.array(x)
#x= np.concatenate((x,np.zeros(x.size)))

n= np.arange(x.size)
#%%
m= 2*n+1

m[m >= x.size]= -1
m[m <  0]=       0

y= x[m]


#%%
n= np.arange(100)
#x= np.cos(2*np.pi*1/10*n)
#x= (1/10)**n * n**10

a= 10.0
x= a**(-n) * n**(a-1)

f= .01
x=   np.cos(2*np.pi*f*n)\
   + np.cos(2*np.pi*f*2*n)\
   + np.cos(2*np.pi*f*3*n)

x[-1]=0
   
n= np.arange(x.size)

def mod(m):
    '''
    修飾 m 的範圍，
    使得它保持在 0 <= mod <= m.size-1
    m<0 時，設 mod = -1
    m>= m.size時，設 mod = -1
    '''
    mod= m
    mod[mod >= m.size]= -1 # the last point
    mod[mod <  0]=      -1 # 0
    mod= mod.astype(int)
    return mod

y1= x[mod((n-10)*2)]
y2= x[mod((n+10)//2)]
y3= x[mod((n**1.05))]

pl.plot(n,x,'x-',
        n,y1,'o:',
        n,y2,'^:',
        #n,y3,'s:'
        )

pl.grid('on')
#%%
#%%
def delta(n):
    x= np.zeros(n.size)
    x[0]= 1
    return x

def step(n):
    x= np.ones(n.size)
    return x


N=20
n= np.arange(N+1) # 0,...,N
x= delta(n)
y1= x[mod(n-1)]
y2= x[mod(n-2)]
y3= 1/3*y1+2/3*y2
y4= y3[mod(n-4)]

w= 5
y5= np.sinc(n/w)
y6= y5[mod((n-2)*2)]

pl.plot(n,x,'x-',
        n,y1,'o:',
        n,y2,'^:',
        n,y3,'s:',
        n,y4,'v:',
        n,y5,'o--',
        n,y6,'^--'
        )

pl.grid('on')












#%%
#%%
#%%
N= 10
n= np.arange(-N,N+1)
#x= np.cos(2*np.pi*1/10*n)
#x= (1/10)**n * n**10

a=2
b=3

x= n**a * np.exp(-n/b)

'''
f= .1
x=   np.cos(2*np.pi*f*n)\
   + np.cos(2*np.pi*f*2*n)\
   + np.cos(2*np.pi*f*3*n)

#x[-1]=0
   
#n= np.arange(x.size)
'''
x=step(n)

def mod(m, periodic=False):
    '''
    修飾 m 的範圍，
    使得它保持在 0 <= mod <= m.size-1
    m<0 時，設 mod = -1
    m>= m.size時，設 mod = -1
    '''
    assert m.dtype == int
    
    if periodic==True:
        mod= m%m.size
    else:    
        mod= m
        mod[mod >= m.size]= -1 # the last point
        mod[mod <  0]=      -1 # 0
    return mod

y1= x[n-2]

y2= x[n+2]
#y3= x[mod((n**1.05))]

pl.plot(n,x,'x-',
        n,y1,'o:',
        n,y2,'^:',
        #n,y3,'s:'
        )

pl.grid('on')
#%%



