library(ggplot2)

# the following mse calculations came from another script (/home/ubuntu/bikeshare/model/ipython_explore/poisson_web)
mse = sqrt(c(7.9036757471653702, 13.581129739842908, 23.315972323027047, 27.788117933581713, 37.022093998483889))
mse_ind = sqrt(c(0.041638038096159742, 0.048030072095611359, 0.065528378574539123, 0.097135731681747078, 0.14491540459024851))
minutes = c(15,30,45,60,120)


mse_object = as.data.frame(cbind(minutes, mse))
colnames(mse_object) = c('x','y')

mse_plot <- ggplot(mse_object, aes(x,y))
mse_plot + geom_point(data = mse_object, color = 'blue', size = 3) + labs(x = 'Minutes Past Current Time', y = 'Average Prediction Error (Number of Bikes)', title = "Square Root of Mean Squared Error \n Between Predicted and Actual Number of Bikes") + scale_x_continuous(breaks=c(15,30,45,60,75,90,105,120))

mse_ind_object = as.data.frame(cbind(minutes, mse_ind))
colnames(mse_ind_object) = c('x','y')

mse_ind_plot <- ggplot(mse_ind_object, aes(x,y))
mse_ind_plot + geom_point(data = mse_ind_object, color = 'blue', size = 3) + 
  labs(x = 'Minutes Past Current Time', y = 'Average Prediction Error in Terms of Probability', 
       title = "Square Root of Mean Squared Error of \n Probability(station is empty in next t minutes)") + scale_x_continuous(breaks=c(15,30,45,60,75,90,105,120))
