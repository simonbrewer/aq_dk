library(tidyverse)
library(viridis)
library(colorspace)
library(sf)

slc_cnty = st_read("./data/SLC/Salt_lake.shp")

fishnet = slc_cnty %>%
  st_make_grid(cellsize = 0.01, what = "polygons") %>%
  st_as_sf() %>%
  rename(geometry = x) %>%
  mutate(fishnet_id = 1:n()) %>%
  dplyr::select(fishnet_id, geometry) 
# fishnet <- read_rds("./data/SLC/slc_fishnet.rds")

ggplot() +
  # Visualize fishnet with blue lines with no fill
  geom_sf(data = fishnet, fill = NA, color = "steelblue", size = 0.05) +
  # Visualize county subdivisions with black lines with no fille
  geom_sf(data = slc_cnty, fill = NA, color = "grey", linewidth = 2) +
  theme_void(base_size = 14)

out_df = read.csv("./output/all_adj.csv")

out_sf = st_as_sf(out_df, coords = c("lon", "lat"),
                  crs = st_crs(fishnet))

plot(st_geometry(out_sf))

tmp <- out_sf %>%
  st_join(fishnet) %>%
  as.data.frame() %>%
  group_by(fishnet_id) %>%
  summarize(obs = mean(val, na.rm = TRUE),
            pred = mean(yhat, na.rm = TRUE),
            av_adj = mean(adj, na.rm = TRUE),
            sd_adj = sd(adj, na.rm = TRUE)) %>%
  ungroup()

fishnet = fishnet %>%
  # Join in pvout fishnet grid averages
  left_join(by = "fishnet_id", y = tmp) %>%
  drop_na()

ggplot() +
  geom_sf(data = slc_cnty, fill = NA, color = "lightgray", linewidth = 2) +
  geom_sf(data = fishnet, mapping = aes(fill = obs), 
          color = "steelblue", size = 0.05) +
  scale_fill_viridis(option = "viridis") +
  theme_void(base_size = 14) 

ggplot() +
  geom_sf(data = slc_cnty, fill = NA, color = "lightgray", linewidth = 2) +
  geom_sf(data = fishnet, mapping = aes(fill = pred), 
          color = "steelblue", size = 0.05) +
  scale_fill_viridis(option = "viridis") +
  theme_void(base_size = 14) 

ggplot() +
  geom_sf(data = slc_cnty, fill = NA, color = "lightgray", linewidth = 2) +
  geom_sf(data = fishnet, mapping = aes(fill = av_adj), 
          color = "steelblue", size = 0.05) +
  scale_fill_continuous_diverging(palette = "Purple-Green") +
  theme_void(base_size = 14) 

ggplot() +
  geom_sf(data = slc_cnty, fill = NA, color = "lightgray", linewidth = 2) +
  geom_sf(data = fishnet, mapping = aes(fill = sd_adj), 
          color = "steelblue", size = 0.05) +
  scale_fill_viridis(option = "viridis") +
  theme_void(base_size = 14) 

