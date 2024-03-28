## Run loop through june / july 2023

## -----------------------
## Load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import datetime
from sklearn import ensemble

## -----------------------
## Prep grid (mostly for bounds)
grid_gdf = gpd.read_file("./data/coarse_grid_pts/grid_pts_coarse.shp")
grid_gdf = grid_gdf.set_crs(4326, allow_override=True)
grid_gdf = grid_gdf.to_crs(32612)

## Grid min/max (replaced by set limits below)
grid_crds = grid_gdf.get_coordinates()
min_x = grid_crds.x.min()
max_x = grid_crds.x.max()
min_y = grid_crds.y.min()
max_y = grid_crds.y.max()

## Updated to help estimate of basis functions
min_x = 393500
max_x = 453500
min_y = 4472000
max_y = 4532000
print(min_x, max_x, min_y, max_y)

## Standardize coordinates
grid_crds['normalized_east'] = (grid_crds['x']-min_x)/(max_x - min_x)
grid_crds['normalized_north'] = (grid_crds['y']-min_y)/(max_y-min_y)

## -----------------------
## Air monitor data
aq_df = pd.read_csv("./data/loop_test/summer23_ozone_stationary.csv")
aq_df['day_time'] = pd.to_datetime(aq_df['day_time']).dt.tz_localize(None)
## add the timezone:
aq_df['day_time'] = aq_df['day_time'] + pd.Timedelta(hours=7)

## Convert to geopandas
aq_gdf = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(aq_df.longitude, aq_df.latitude, crs="EPSG:4326"), data=aq_df
)
aq_gdf = aq_gdf.to_crs(32612)

## Standardize coordinates
aq_crds = aq_gdf.get_coordinates()
lon = aq_crds.x
lat = aq_crds.y
aq_df['normalized_east'] = (lon-min_x)/(max_x - min_x)
aq_df['normalized_north'] = (lat-min_y)/(max_y-min_y)

## -----------------------
## EBus data
ebus = pd.read_csv("./data/loop_test/ebus_2023_06-07.csv", header = [0,1],  
                 na_values = -9999.00)
ebus2_df = pd.DataFrame({
    'time': pd.to_datetime(ebus.iloc[:,1]),
    'lon': ebus.iloc[:,3],
    'lat': ebus.iloc[:,2]
    })
ebus2_df['val'] = ebus['O3'] / 1000

## Convert to geopandas
ebus2_gdf = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(ebus2_df.lon, ebus2_df.lat, crs="EPSG:4326"), data=ebus2_df
)
ebus2_gdf = ebus2_gdf.to_crs(32612)

## Standardize coordinates
ebus2_crds = ebus2_gdf.get_coordinates()
lon = ebus2_crds.x
lat = ebus2_crds.y
ebus2_df['normalized_east'] = (lon-min_x)/(max_x - min_x)
ebus2_df['normalized_north'] = (lat-min_y)/(max_y-min_y)

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

## Create knots for time basis - 14 day basis function (/2 for 7 day)
num_basis_t = [10,20,56]
std_arr_t = [0.3,0.15,0.05]
knots_1d_t = make_knots_time(num_basis_t)

## Knots for spatial dimension (from STDK example)
num_basis_s = [7**2,13**2,25**2] ## For 60km grid this is 10/5/2.5 resolution
knots_1d_s = make_knots_space(num_basis_s)
    

from functools import reduce
def expand_grid(*arrs):
    ncols = len(arrs)
    nrows = reduce(lambda x, y: x * y, map(len, arrs), 1)
    
    return np.array(np.meshgrid(*arrs)).reshape(ncols, nrows).T

plt.plot(grid_crds['normalized_east'], grid_crds['normalized_north'], 'bo', markersize=1)
plt.plot(ebus2_df['normalized_east'], ebus2_df['normalized_north'], 'ro', markersize=2)
plt.plot(aq_df['normalized_east'], aq_df['normalized_north'], 'go')

x = expand_grid(knots_1d_s[0], knots_1d_s[0])
plt.plot(x[:,0], x[:,1], 'kx', markersize=8)
x = expand_grid(knots_1d_s[1], knots_1d_s[1])
plt.plot(x[:,0], x[:,1], 'rx', markersize=5)
x = expand_grid(knots_1d_s[2], knots_1d_s[2])
plt.plot(x[:,0], x[:,1], 'gx', markersize=2)
plt.show()

#plt.plot(knots_1d_t[0], 'kx', markersize = 8)
#plt.plot(knots_1d_t[1], 'rx', markersize = 5)
#plt.plot(knots_1d_t[2], 'gx', markersize = 2)
#lt.show()

