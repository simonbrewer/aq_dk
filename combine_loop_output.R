library(tidyverse)


all_vars = c("o3", "pm25", "tmp")

for (j in all_vars) {
  print(j)
  var_dir = paste0("./output/", j, "/")
  all_files = list.files(var_dir, pattern = "adj*")
  
  out_df = NULL
  
  for (i in all_files) {
    tmp_df = read.csv(paste0(var_dir, i))
    out_df = rbind(out_df, tmp_df)
  }
  
  write.csv(out_df, paste0(var_dir, "/all_adj.csv"), row.names = FALSE)
  
}

out_df$time = ymd_hms(out_df$time)

  