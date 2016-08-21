library(ggplot2)
library(VIM)
library(mice)
library(vcd)
require(car)
library(tabplot)
library(PerformanceAnalytics)
library(MASS)
library(glmnet)

# ===============================================================================================
setwd("~/movie")
movies = read.csv("movie_metadata.csv")

# ===============================================================================================
# EDA
summary(movies)
sapply(movies, sd)
hist(movies$num_critic_for_reviews)

# ===============================================================================================
# investigate missingness

length(complete.cases(movies))
aggr(movies, numbers=T, prop=F, sortVars=T, labels=names(movies)) # change 'prop' to T to see ratio

## Matrix plot. Red for missing values, Darker values are high values.
matrixplot(movies, interactive=T, sortby="imdb_score")

## Margin plot. Red dots have at least one missing. No observation with two missing values here.
marginplot(movies[,c("gross", "imdb_score")])

md.pattern(movies) # hard to interpret due to too many variables

# findings
# 'gross' has the most amount of missingness.

# ===============================================================================================
scattmatrixMiss(movies[, 1:5], interactive = F)

hist(movies$imdb_score, breaks=30)
plot(density(movies$imdb_score))
abline(v=mean(movies$imdb_score), lty=2)

hist(movies$title_year)

boxplot(imdb_score ~ title_year, data=movies, col="bisque", las=2)
title("IMDB score vs movie year")

# imdb_score vs country
reordered_country = with(movies, reorder(country, -imdb_score, median))
boxplot(imdb_score ~ reordered_country, data=movies, lwd=0.5, col="bisque", las=2)
#stripchart(imdb_score ~ reordered_country, data=movies, vertical=T, add=T, pch=1, col='grey')
title("IMDB score vs country")

reordered_language = with(movies, reorder(language, -imdb_score, median))
boxplot(imdb_score ~ reordered_language, data=movies, lwd=0.5, col="bisque", las=2)
#stripchart(imdb_score ~ reordered_language, data=movies, vertical=T, add=T, pch=1, col='grey')
title("IMDB score vs language")

# not informative
#boxplot(imdb_score ~ aspect_ratio, data=movies, lwd=0.5, col="bisque", las=2)
#stripchart(imdb_score ~ aspect_ratio, data=movies, vertical=T, add=T, pch=1, col='grey')
#title("IMDB score vs aspect ratio")

boxplot(imdb_score ~ color, data=movies, lwd=0.5, col="bisque", las=2)
stripchart(imdb_score ~ color, data=movies, vertical=T, add=T, pch=1, col='grey')
title("IMDB score vs color")

reordered_content_rating = with(movies, reorder(content_rating, -imdb_score, median))
boxplot(imdb_score ~ reordered_content_rating, data=movies, lwd=0.5, col="bisque", las=2)
stripchart(imdb_score ~ reordered_content_rating, data=movies, vertical=T, add=T, pch=1, col='grey')
title("IMDB score vs content rating")

# ===============================================================================================
# top actors
library(googleVis)
library(dplyr)
m1 = movies %>% select(actor_1_name, actor_1_facebook_likes) %>% 
    group_by(actor_1_name) %>% summarize(appear.count=n())

m2 = left_join(movies, m1, by="actor_1_name")
m3 = m2 %>% select(actor_1_name, actor_1_facebook_likes, appear.count) %>%
    distinct %>% arrange(desc(appear.count))

hist(m3$appear.count, breaks=30)

Bubble <- gvisBubbleChart(m3, idvar="actor_1_name", 
                          xvar="appear.count", yvar="actor_1_facebook_likes",
                          sizevar="appear.count",
                          #colorvar="title_year",
                          options=list(
                              #hAxis='{minValue:75, maxValue:125}',
                              width=1000, height=800
                          )
                          )
plot(Bubble)

# ===============================================================================================
# pairwise Relationships

# does not work!
#mosaic(movies[, categorical_variables], legend=TRUE)

ms_all_rows = movies[, c("imdb_score",
                "director_facebook_likes", 
                "cast_total_facebook_likes", 
                #"actor_1_facebook_likes",
                #"actor_2_facebook_likes",
                #"actor_3_facebook_likes",
                #"movie_facebook_likes", 
                "facenumber_in_poster",
                "gross",
                "budget")]
ms = na.omit(ms_all_rows)

# ===============================================================================================
# all best movies, their year, actors

# all worst movies, their year, actors

# ===============================================================================================
# do k-means clustering



# ===============================================================================================
# EDA on smaller data
cor(ms)
plot(ms, pch='.')
chart.Correlation(ms) 
# very informative! It shows that cast_total_facebook_likes has high correlation with actor_1_facebook_likes

msc = movies[, c("color",
    "duration",
    "content_rating",
    "language",
    "country",
    "aspect_ratio",
    "title_year",
    "imdb_score"
)]


scatterplotMatrix(ms, pch=".")

hist(movies$director_facebook_likes, breaks=30)
plot(density(na.omit(movies$director_facebook_likes)))


# ===============================================================================================
# https://cran.r-project.org/web/packages/tabplot/vignettes/tabplot-vignette.html
tableplot(ms, sortCol="imdb_score") # gives you a sorted image according to class
tableplot(msc, sortCol="country") # gives you a sorted image according to class

# ===============================================================================================
# faces in poster
hist(movies$facenumber_in_poster, breaks=50)


# ===============================================================================================
# build word cloud using plot keywords for best movies and worst movies
# http://datascienceplus.com/building-wordclouds-in-r/

view_model = function(model) {
    par(mfrow=c(2,2)) # Change the panel layout to 2 x 2
    plot(model)
    par(mfrow=c(1,1)) # Change back to 1 x 1
}

# ===============================================================================================
# fit multiple linear regression model
model.saturated = lm(imdb_score ~ ., data = ms)
summary(model.saturated)
view_model(model.saturated)
influencePlot(model.saturated)
vif(model.saturated) #Assessing the variance inflation factors for the variables in our model.
avPlots(model.saturated)

AIC(model.saturated)
BIC(model.saturated)

# ===============================================================================================
#We can use stepwise regression to help automate the variable selection process.
#Here we define the minimal model, the full model, and the scope of the models
#through which to search:
model.empty = lm(imdb_score ~ 1, data = ms) #The model with an intercept ONLY.
model.full = lm(imdb_score ~ ., data = ms) #The model with ALL variables.
scope = list(lower = formula(model.empty), upper = formula(model.full))
forwardAIC = step(model.empty, scope, direction = "forward", k = 2)

summary(forwardAIC)
view_model(forwardAIC)
influencePlot(forwardAIC)
vif(forwardAIC)
avPlots(forwardAIC)
confint(forwardAIC) # note if those intervals contain 0.

# ===============================================================================================
bc = boxCox(forwardAIC)
lambda = bc$x[which(bc$y == max(bc$y))] # Extracting the best lambda value
imdb_score.bc = (ms$imdb_score^lambda - 1)/lambda
model.bc = lm(imdb_score.bc ~ gross + director_facebook_likes + facenumber_in_poster + 
                  cast_total_facebook_likes, data=ms)

summary(model.bc)
view_model(model.bc)
influencePlot(model.bc)
vif(model.bc)
avPlots(model.bc)
confint(model.bc) # note if those intervals contain 0.

# boxcox can make model looks better! But I lose many predictors

# ===============================================================================================
# movie prediction
movies_with_good_variables = movies[, c("imdb_score",
                 "director_facebook_likes", 
                 "cast_total_facebook_likes", 
                 "actor_1_facebook_likes",
                 "actor_2_facebook_likes",
                 "actor_3_facebook_likes",
                 "movie_facebook_likes", 
                 "facenumber_in_poster",
                 "gross",
                 "budget")]
mvs = na.omit(movies_with_good_variables)
x = as.matrix(mvs[, -1])
y = mvs[, 1]

##########################
#####Ridge Regression#####
##########################

# Fitting the ridge regression. Alpha = 0 for ridge regression.
grid = 10^seq(5, -2, length = 100)
ridge.models = glmnet(x, y, alpha = 0, lambda = grid)
dim(coef(ridge.models)) #20 different coefficients, estimated 100 times --once each per lambda value.
coef(ridge.models) #Inspecting the various coefficient estimates.

# Visualizing the ridge regression shrinkage.
plot(ridge.models, xvar = "lambda", label = TRUE, main = "Ridge Regression")

# Creating training and testing sets. Here we decide to use a 70-30 split with approximately 70% of our data in the training 
# set and 30% of our data in the test set.
set.seed(0)
train = sample(1:nrow(x), 7*nrow(x)/10)
test = (-train)
y.test = y[test]

length(train)/nrow(x)
length(y.test)/nrow(x)

#Instead of arbitrarily choosing random lambda values and calculating the MSE
#manually, it's a better idea to perform cross-validation in order to choose
#the best lambda over a slew of values.

#Running 10-fold cross validation.
set.seed(0)
cv.ridge.out = cv.glmnet(x[train, ], y[train], lambda = grid, alpha = 0, nfolds = 10)
plot(cv.ridge.out, main = "Ridge Regression\n")
bestlambda.ridge = cv.ridge.out$lambda.min
bestlambda.ridge
log(bestlambda.ridge)

#What is the test MSE associated with this best value of lambda?
ridge.bestlambdatrain = predict(ridge.models, s = bestlambda.ridge, newx = x[test, ])
mean((ridge.bestlambdatrain - y.test)^2)

#Refit the ridge regression on the overall dataset using the best lambda value
#from cross validation; inspect the coefficient estimates.
ridge.out = glmnet(x, y, alpha = 0)
predict(ridge.out, type = "coefficients", s = bestlambda.ridge)

#Let's also inspect the MSE of our final ridge model on all our data.
ridge.bestlambda = predict(ridge.out, s = bestlambda.ridge, newx = x)
mean((ridge.bestlambda - y)^2)


##########################
#####Lasso Regression#####
##########################

#Fitting the lasso regression. Alpha = 1 for lasso regression.
lasso.models = glmnet(x, y, alpha = 1, lambda = grid)

dim(coef(lasso.models)) #20 different coefficients, estimated 100 times --
#once each per lambda value.
coef(lasso.models) #Inspecting the various coefficient estimates.

#Instead of arbitrarily choosing random lambda values and calculating the MSE
#manually, it's a better idea to perform cross-validation in order to choose
#the best lambda over a slew of values.

#Running 10-fold cross validation.
set.seed(0)
cv.lasso.out = cv.glmnet(x[train, ], y[train], lambda = grid, alpha = 1, nfolds = 10)
plot(cv.lasso.out, main = "Lasso Regression\n")
bestlambda.lasso = cv.lasso.out$lambda.min
bestlambda.lasso
log(bestlambda.lasso)

#What is the test MSE associated with this best value of lambda?
lasso.bestlambdatrain = predict(lasso.models, s = bestlambda.lasso, newx = x[test, ])
mean((lasso.bestlambdatrain - y.test)^2)

#Here the MSE is much lower at approximately 89,452; a further improvement
#on that which we have seen above.

#Refit the lasso regression on the overall dataset using the best lambda value
#from cross validation; inspect the coefficient estimates.
lasso.out = glmnet(x, y, alpha = 1)
predict(lasso.out, type = "coefficients", s = bestlambda.lasso)

#Let's also inspect the MSE of our final lasso model on all our data.
lasso.bestlambda = predict(lasso.out, s = bestlambda.lasso, newx = x)
mean((lasso.bestlambda - y)^2)

