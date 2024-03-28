set.seed(42)
library(tidyverse)
library(sf)

dat <- read.csv("data/EBUS/ebus_min_2023_07.csv")

dat$times <- ymd_hms(dat$times)
dat2 <- dat %>%
  filter(month(times) == 7, day(times) == 10) %>%
  select(LON, LAT, times, PM2.5) %>%
  mutate(times2 = as.numeric(times))

dat_sf <- st_as_sf(dat2, coords = c("LON", "LAT"))

plot(st_geometry(dat_sf))

library(tmap)
tm_shape(dat_sf) +
  tm_symbols(col = "times2")

tm_shape(dat_sf) +
  tm_symbols(col = "PM2.5", size = 0.1, alpha = 0.75)
