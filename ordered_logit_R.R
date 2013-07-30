require("MASS")
require('rms')
require("Zelig")
require("ZeligChoice")
setwd("/mnt/data1/BikeShare/")

# Every sixteen minute data
raw.data <- read.table("DC_station_24_reduced.csv",header = TRUE, sep = ',')
time_markers <- raw.data[,5:28]
month_markers <- raw.data[,29:ncol(raw.data)]
full_data <- raw.data[,1:4]


# Create lagged time variables to fit model
data_lagged = NULL
data_lagged$current_bikes = factor(full_data$bikes_available[1:(nrow(full_data)-3)], ordered = TRUE, levels = 0:15)
data_lagged$lagged_one = full_data$bikes_available[2:(nrow(full_data)-2)]
data_lagged$lagged_two = full_data$bikes_available[3:(nrow(full_data)-1)]
data_lagged$lagged_three = full_data$bikes_available[4:(nrow(full_data))]
data_lagged = data.frame(data_lagged)


model_data <- NULL
model_data <- data_lagged$lagged_three * time_markers[4:(nrow(full_data)),]
names(model_data) <- paste("X", names(model_data), sep="")
model_data <- cbind(data_lagged$lagged_two * time_markers[3:(nrow(full_data)-1),], model_data)
names(model_data) <- paste("X", names(model_data), sep="")
model_data <- cbind(data_lagged$lagged_one * time_markers[2:(nrow(full_data)-2),], model_data)

# We will include the month indicator for the month to be predicted
model_data <- cbind(model_data, month_markers[1:(nrow(full_data)-3),])

model_data$current_bikes = data_lagged$current_bikes

col_idx <- grep("current_bikes", names(model_data))
model_data <- model_data[, c(col_idx, (1:ncol(model_data))[-col_idx])]
# Partition into training and testing data

errors = NULL
for(i in 1:10) {
train_sample <- sample(nrow(model_data),floor(4/5 * nrow(model_data)))
train_data <- model_data[train_sample,]
test_data <- model_data[-train_sample,]

ordered_logit = lrm(formula = current_bikes ~ ., data = train_data)
pred.out <- predict(ordered_logit, test_data, type = "fitted.ind")
predictions <- apply(pred.out, 1, which.max)-1

pred_full_level <- rep('balanced',length(test_data$current_bikes))

pred_full_level[which(predictions<3)] = 'empty'
pred_full_level[which(predictions>12)] = 'full'

true_full_level <- rep('balanced',length(test_data$current_bikes))

true_full_level[which(test_data$current_bikes<3)] = 'empty'
true_full_level[which(test_data$current_bikes>12)] = 'full'
errors = c(errors, sum(true_full_level != pred_full_level)/length(true_full_level))
# Gives 0.1068587 error rate without month info
# With months gives 0.1069128 error.... weird.
}



