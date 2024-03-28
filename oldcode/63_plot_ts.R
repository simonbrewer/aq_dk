library(tidyverse)
library(patchwork)

out_df = read.csv("./output/all_adj.csv")
out_df$time = ymd_hms(out_df$time)
out_df$time2 = round(out_df$time, unit = "hour")
out_df$time2 = as.POSIXct(out_df$time2)

out_ts = out_df %>%
  group_by(time2) %>%
  summarise(val = mean(val, na.rm = TRUE),
            yhat = mean(yhat, na.rm = TRUE),
            adj = mean(adj, na.rm = TRUE))

p1 = ggplot(out_ts, aes(x = time2)) +
  geom_line(aes(y = val)) +
  scale_x_datetime("Date") +
  scale_y_continuous("ppm") +
  theme_bw()

p2 = ggplot(out_ts, aes(x = time2)) +
  geom_line(aes(y = yhat)) +
  scale_x_datetime("Date") +
  scale_y_continuous("ppm") +
  theme_bw()

p3 = ggplot(out_ts, aes(x = time2)) +
  geom_line(aes(y = adj)) +
  # geom_smooth(aes(y = adj)) +
  scale_x_datetime("Date") +
  scale_y_continuous(expression(delta~ppm)) +
  theme_bw()

tmp_ts = data.frame(time = rep(out_ts$time2, 2),
                    val = c(out_ts$val, out_ts$yhat),
                    type =rep(c("Obs", "Pred"), each = nrow(out_ts)))
p4 = ggplot(tmp_ts, aes(x = time, y = val, col = type)) +
  geom_line() +
  scale_x_datetime("Date") +
  scale_y_continuous("ppm") +
  theme_bw()

p4 / p3


