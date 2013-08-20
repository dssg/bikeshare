library(ggplot2)
mse = sqrt(c(7.9036757471653702, 13.581129739842908, 23.315972323027047, 27.788117933581713, 37.022093998483889))
minutes = c(15,30,45,60,120)

mse_object = as.data.frame(cbind(minutes, mse))
colnames(mse_object) = c('x','y')

p <- ggplot(mse_object, aes(x,y))
p + geom_point(data = mse_object, color = 'blue', size = 3) + labs(x = 'Minutes Past Current Time', y = 'Average Prediction Error (Number of Bikes)', title = "Square Root of Mean Squared Error \n Between Predicted and Actual Number of Bikes") + scale_x_continuous(breaks=c(15,30,45,60,75,90,105,120))
