## Run loop through june / july 2023

## -----------------------
## Load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import datetime
from sklearn import ensemble
import rbf_utils

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
# aq_df = pd.read_csv("./data/loop_test/summer23_ozone_stationary.csv")
aq_df = pd.read_csv("./data/aq2023/stationary_o3_2.csv")
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

#plt.plot(grid_crds['normalized_east'], grid_crds['normalized_north'], 'bo', markersize=1)
#plt.plot(ebus2_df['normalized_east'], ebus2_df['normalized_north'], 'ro', markersize=2)
#plt.plot(aq_df['normalized_east'], aq_df['normalized_north'], 'go')
#plt.show()

aq_sites = aq_df['site.num'].unique()
aq_sites

for site in aq_sites:
    print("## -------------- ##")
    print(f"Running site: {site}")
    train = aq_df[aq_df['site.num'] != site]
    # train = aq_df
    print(f"Train dims {train.shape}")
    test = aq_df[aq_df['site.num'] == site]
    print(f"Test dims {test.shape}")
    all_days = aq_df.date.unique()
    all_days = all_days[6:]
    for i in all_days:
        print("## -------------- ##")
        print(f"Running for {i}")
        target_date = pd.to_datetime(i)
        start_date = target_date - pd.to_timedelta(7, unit='d')

        ## ------------------------------------------------------------------------
        ## Extract monitor data
        print("Prepping training data")
        start_date_train = target_date - pd.to_timedelta(7, unit='d')
        stop_date_train = target_date + pd.to_timedelta(1, unit='d')
        train_sub = train[(train['day_time'] >= start_date_train) & (train['day_time'] < stop_date_train)].copy()

        day_time = train_sub['day_time'].astype('int64') / 1e9 ## Time in nanoseconds
        min_t = day_time.min()
        max_t = day_time.max()
        train_sub['normalized_time'] = (day_time - min_t) / (max_t-min_t)

        ## Create knots for time basis - 14 day basis function (/2 for 7 day)
        num_basis_t = [10,20,56]
        std_arr_t = [0.3,0.15,0.05]
        knots_1d_t = rbf_utils.make_knots_time(num_basis_t)

        ## Create time basis for monitor data
        s = np.array(train_sub['normalized_time']).reshape(len(train_sub),1)
        phi_t1 = rbf_utils.get_basis_gaussian_1d(s, num_basis_t, knots_1d_t, std_arr_t)

        ## Knots for spatial dimension (from STDK example)
        num_basis_s = [7**2,13**2,25**2] ## For 60km grid this is 10/5/2.5 resolution
        knots_1d_s = rbf_utils.make_knots_space(num_basis_s)
        
        ## Create time basis for monitor data
        s = np.vstack((train_sub['normalized_east'],train_sub['normalized_north'])).T
        phi_s1 = rbf_utils.get_basis_wendland_2d(s, num_basis_s, knots_1d_s)

        phi_1 = np.hstack((phi_t1,phi_s1))
        idx_zero = np.array([], dtype=int)
        for i in range(phi_1.shape[1]):
            if sum(phi_1[:,i]!=0)==0:
                idx_zero = np.append(idx_zero,int(i))
        
        phi_1_reduce = np.delete(phi_1,idx_zero,1)
        print(f"Phi_1: {phi_1_reduce.shape}")

        ## ------------------------------------------------------------------------
        ## EBus data
        print("Prepping testing data")
        # start_date_pred = target_date - pd.to_timedelta(1, unit='d')
        # stop_date_pred = target_date + pd.to_timedelta(1, unit='d')
        # ebus2_df_sub = ebus2_df[(ebus2_df['time'] >= target_date) & (ebus2_df['time'] < stop_date_pred)].copy()

        # day_time = ebus2_df_sub['time'].astype('int64') / 1e9 ## Time in nanoseconds
        # ebus2_df_sub['normalized_time'] = (day_time - min_t) / (max_t-min_t)

        start_date_pred = target_date - pd.to_timedelta(1, unit='d')
        stop_date_pred = target_date + pd.to_timedelta(1, unit='d')
        test_sub = test[(test['day_time'] >= start_date_pred) & (test['day_time'] < stop_date_pred)].copy()

        day_time = test_sub['day_time'].astype('int64') / 1e9 ## Time in nanoseconds
        # min_t = day_time.min()
        # max_t = day_time.max()
        test_sub['normalized_time'] = (day_time - min_t) / (max_t-min_t)

        s = np.array(test_sub['normalized_time']).reshape(len(test_sub),1)
        phi_t2 = rbf_utils.get_basis_gaussian_1d(s, num_basis_t, knots_1d_t, std_arr_t)

        s = np.vstack((test_sub['normalized_east'],test_sub['normalized_north'])).T
        phi_s2 = rbf_utils.get_basis_wendland_2d(s, num_basis_s, knots_1d_s)

        phi_2 = np.hstack((phi_t2,phi_s2))
        phi_2_reduce = np.delete(phi_2,idx_zero,1)
        print(f"Phi_2: {phi_2_reduce.shape}")
        
        if (phi_2_reduce.shape[0] > 1):
            ## ------------------------------------------------------------------------
            ## Random forest
            print("Running RF model")
            ## Create arrays for training RF
            X_train = phi_1_reduce
            y_train = train_sub['sample.measurement'].values

            ## Create and train
            aq_rf = ensemble.RandomForestRegressor()
            aq_rf.fit(X_train, y_train)

            ## Predict for EBus
            X_pred = phi_2_reduce
            test_sub['yhat'] = aq_rf.predict(X_pred)
            test_sub['adj'] = test_sub['sample.measurement'] - test_sub['yhat']

            ## Write out
            print(i)
            test_sub.to_csv("./xv_output/o3_rf/" + str(site) + "_adj_" + str(target_date.date()) + ".csv", sep=',', index=False)

        #plt.plot(ebus2_df_sub['val'])
        #plt.plot(ebus2_df_sub['yhat'])
        #plt.show()
        #plt.plot(ebus2_df_sub['yhat']-ebus2_df_sub['val'])
        #plt.show()
        #plt.plot(aq_df_sub.normalized_time, y_train, 'bo', markersize = 0.5)
        #plt.plot(ebus2_df_sub.normalized_time, y_pred)
        #plt.plot(ebus2_df_sub.normalized_time, ebus2_df_sub['yhat'])
        #plt.show()
        #break
