library(tidyverse)

all_files = list.files("./output/", pattern = "adj*")

out_df = NULL

for (i in all_files) {
  tmp_df = read.csv(paste0("./output/", i))
  out_df = rbind(out_df, tmp_df)
}

write.csv(out_df, "./output/all_adj.csv", row.names = FALSE)

out_df$time = ymd_hms(out_df$time)

  