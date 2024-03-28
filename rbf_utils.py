## -----------------------
## Load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import ensemble

## -----------------------
## Basis functions

## Function to make knots in 1D space/time [0, 1]. Pass vector of number of knots in 1D
def make_knots_time(n):
    knots = [np.linspace(0,1,int(i)) for i in n]
    return(knots)

## Function to make Gaussian BFs along one dimension
def get_basis_gaussian_1d(s, num_basis, knots, std_arr):
    N = len(s)
    phi = np.zeros((N, sum(num_basis)))
    K = 0
    for res in range(len(num_basis)):
        std = std_arr[res]
        for i in range(num_basis[res]):
            d = np.square(np.absolute(s-knots[res][i]))
            for j in range(len(d)):
                if d[j] >= 0 and d[j] <= 1:
                    phi[j,i + K] = np.exp(-0.5 * d[j]/(std**2))
                else:
                    phi[j,i + K] = 0
        K = K + num_basis[res]
    return(phi)

## Function to make knots in 2D space [0, 1]. Pass vector of number of knots in 2D (i.e. res of 5, pass 25)
def make_knots_space(n):
    knots = [np.linspace(0,1,int(np.sqrt(i))) for i in n]
    return knots

## Function to make Wendland BFs over two dimensions
def get_basis_wendland_2d(s, num_basis, knots_1d):
    ## Get weights from Wendland kernel
    N = len(s)
    K = 0
    phi = np.zeros((N, sum(num_basis)))
    for res in range(len(num_basis)):
        theta = 1/np.sqrt(num_basis[res])*2.5
        knots_s1, knots_s2 = np.meshgrid(knots_1d[res],knots_1d[res])
        knots = np.column_stack((knots_s1.flatten(),knots_s2.flatten()))
        for i in range(num_basis[res]):
            d = np.linalg.norm(s-knots[i,:],axis=1)/theta
            for j in range(len(d)):
                if d[j] >= 0 and d[j] <= 1:
                    phi[j,i + K] = (1-d[j])**6 * (35 * d[j]**2 + 18 * d[j] + 3)/3
                else:
                    phi[j,i + K] = 0
        K = K + num_basis[res]
    return(phi)

