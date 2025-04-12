library(tidyverse)

## ----------------------------------------------------------------------------
## RF below here
xv_dir = "./xv_output/o3_rf_2023/"

file_list = list.files(xv_dir)

my_split <- function(x) {
  split = strsplit(x, "_")
  return(split[[1]][1])
}


sites = unique(sapply(file_list, my_split))

all_df = NULL

for (site in sites) {
  print(site)
  file_list = list.files(xv_dir, pattern = site)
  out_df = NULL
  for (file in file_list) {
    
    sel_date = strsplit(file, "_")[[1]][3]
    sel_date = strsplit(sel_date, "\\.")[[1]][1]
    
    tmp_df = read.csv(paste0(xv_dir, file))
    tmp_df <- tmp_df %>% 
      filter(date == sel_date)
    
    out_df = rbind(out_df, tmp_df)
    
  }
  all_df = rbind(all_df, out_df)
}

## RMSE
sqrt(mean(all_df$adj^2))

my_rmse <- function(x) {
  return(sqrt(mean(x^2)))
}

my_rmse(all_df$adj)

table(all_df$date)

rmse_df <- all_df %>%
  group_by(date) %>%
  summarise(rmse = my_rmse(adj)) %>%
  ungroup()

ggplot(rmse_df, aes(x = date, y = rmse)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_hex()

plot_df <- data.frame(datetime = ymd_hms(rep(all_df$day_time, 2)),
                      site = rep(all_df$site.num, 2),
                      val = c(all_df$sample.measurement, all_df$yhat),
                      source = rep(c("Obs", "Pred"), each = nrow(all_df)))

plot_df <- plot_df %>%
  filter(datetime < ymd_hms("2023-06-20 01:00:00"))
# plot_df <- plot_df %>%
#   filter(datetime >= ymd_hms("2023-06-01 01:00:00"),
#          datetime <= ymd_hms("2023-06-07 23:00:00"))
ggplot(plot_df, aes(x = datetime, y = val, col = source)) +
  geom_line() +
  facet_wrap(~site)

## ----------------------------------------------------------------------------
## QRF below here
xv_dir = "./xv_output/o3_qrf_2023/"

file_list = list.files(xv_dir)

my_split <- function(x) {
  split = strsplit(x, "_")
  return(split[[1]][1])
}


sites = unique(sapply(file_list, my_split))

all_df = NULL

for (site in sites) {
  print(site)
  file_list = list.files(xv_dir, pattern = site)
  out_df = NULL
  for (file in file_list) {
    
    sel_date = strsplit(file, "_")[[1]][3]
    sel_date = strsplit(sel_date, "\\.")[[1]][1]
    
    tmp_df = read.csv(paste0(xv_dir, file))
    
    tmp_df <- tmp_df %>% 
      filter(date == sel_date)
    
    out_df = rbind(out_df, tmp_df)
    
  }
  all_df = rbind(all_df, out_df)
}

## RMSE
sqrt(mean(all_df$adj^2))

my_rmse <- function(x) {
  return(sqrt(mean(x^2)))
}

my_rmse(all_df$adj)

table(all_df$date)

rmse_df <- all_df %>%
  group_by(date) %>%
  summarise(rmse = my_rmse(adj)) %>%
  ungroup()

ggplot(rmse_df, aes(x = date, y = rmse)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_hex()

plot_df <- data.frame(datetime = ymd_hms(rep(all_df$day_time, 2)),
                      site = rep(all_df$site.num, 2),
                      val = c(all_df$sample.measurement, all_df$yhat),
                      source = rep(c("Obs", "Pred"), each = nrow(all_df)))

plot_df <- plot_df %>%
  filter(datetime < ymd_hms("2023-06-20 01:00:00"))
# plot_df <- plot_df %>%
#   filter(datetime >= ymd_hms("2023-06-01 01:00:00"),
#          datetime <= ymd_hms("2023-06-07 23:00:00"))
ggplot(plot_df, aes(x = datetime, y = val, col = source)) +
  geom_line() +
  facet_wrap(~site)

## ----------------------------------------------------------------------------
## BN below here
xv_dir = "./xv_output/o3_bn_2023/"

file_list = list.files(xv_dir, pattern = "csv")

my_split <- function(x) {
  split = strsplit(x, "_")
  return(split[[1]][1])
}


sites = unique(sapply(file_list, my_split))

all_df = NULL

for (file in file_list) {
  
  sel_date = strsplit(file, "_")[[1]][3]
  sel_date = strsplit(sel_date, "\\.")[[1]][1]
  
  tmp_df = read.csv(paste0(xv_dir, file))
  
  all_df = rbind(all_df, tmp_df)
  
}

## RMSE
sqrt(mean(all_df$adj^2))

my_rmse <- function(x) {
  return(sqrt(mean(x^2)))
}

my_rmse(all_df$adj)

table(all_df$date)

rmse_df <- all_df %>%
  group_by(date) %>%
  summarise(rmse = my_rmse(adj)) %>%
  ungroup()

ggplot(rmse_df, aes(x = date, y = rmse)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_point()

ggplot(all_df, aes(x = sample.measurement, y = yhat)) +
  geom_hex()

plot_df <- data.frame(datetime = ymd_hms(rep(all_df$day_time, 2)),
                      site = rep(all_df$site.num, 2),
                      val = c(all_df$sample.measurement, all_df$yhat),
                      source = rep(c("Obs", "Pred"), each = nrow(all_df)))

plot_df <- plot_df %>%
  filter(datetime < ymd_hms("2023-06-20 01:00:00"))
# plot_df <- plot_df %>%
#   filter(datetime >= ymd_hms("2023-06-01 01:00:00"),
#          datetime <= ymd_hms("2023-06-07 23:00:00"))
ggplot(plot_df, aes(x = datetime, y = val, col = source)) +
  geom_line() +
  facet_wrap(~site)

