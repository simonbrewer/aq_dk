set.seed(42)
library(tidyverse)

monitors <- read.csv("./data/monitors.csv")

monitors <- monitors %>%
  select(udaq.site, lat, lon)

mytimes = seq(ymd_hms('2020-06-01 00:00:00'),ymd_hms('2023-08-31 24:00:00'),by='hours')

out_df <- data.frame(id = rep(monitors$udaq.site, each = length(mytimes)),
                     lat = rep(monitors$lat, each = length(mytimes)),
                     lon = rep(monitors$lon, each = length(mytimes)),
                     date = rep(mytimes, nrow(monitors)))
dcycle = 10 * sin(seq(0 - 0.5, 2*pi - 0.5, length.out = 24))

out_df$pm25 = rnorm(nrow(out_df))
out_df$pm25 = out_df$pm25 + dcycle
plot(out_df$pm25 + dcycle, type = 'l', xlim = c(0, 100))

write_csv(out_df, "./data/monitors_rnd.csv")
