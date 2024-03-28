library(tidyverse)
library(neuralnet)

X <- read.csv("./rbfs/phi_reduce.csv")
y <- read.csv("./rbfs/y.csv")
names(y) <- c("yid", "y")

all_df <- cbind(X[, -1], y = y[, -1])

fit <- neuralnet(y ~ ., all_df, 
                 hidden = c(16, 8), 
                 linear.output = TRUE,
                 lifesign = "full", 
                 stepmax = 5e3)
