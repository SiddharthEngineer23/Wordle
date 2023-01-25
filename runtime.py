from datetime import datetime, timedelta
from predictor import Predictor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

class Runtime(object):

    def __init__(self, preload = True):

        #regression model for runtime of wordle.expected_valid_size()
        self.ev_model = self.model(preload)
    
    #builds regression model for runtime of wordle.expected_valid_size()
    def model(self, preload):
        poly_features, train_y = self.data(preload) #training data

        regr = LinearRegression() #linear model
        regr.fit(poly_features, train_y)

        return regr
    
    #returns training dataset for rv_runtime_model
    def data(self, preload):

        #feature for prediction is valid size
        x_list = np.loadtxt("input/runtime-train-x.txt", dtype = int)
        train_x = x_list.reshape(-1, 1)
        interaction = PolynomialFeatures(degree = 2, include_bias=False)
        poly_features = interaction.fit_transform(train_x)

        if preload: #use already executed data
            train_y = np.loadtxt("output/runtime-train-y.txt", dtype = float).tolist()
        else: #find runtime based on current environment
            train_y = self.true_y(x_list)
            np.savetxt("output/runtime-train-y.txt", np.array(train_y), fmt='%i')
        
        return poly_features, train_y
    
    #generate list of y values given list of x values
    #for first half use valid == True, for second half use valid == False
    def true_y(self, x_list):
        y_list = []

        for i in x_list:
            wordle = Predictor() #preloading
            wordle.valid = wordle.reduce_size(i)

            t0 = datetime.now() #find runtime
            table = wordle.expected_valid_size(valid = True, word_freq = False)
            diff = datetime.now() - t0

            microseconds = (pow(10, 6) * diff.seconds) + diff.microseconds
            y_list.append(microseconds) #save data
        
        return y_list

    #returns predicted runtime of self.reduction_values
    def prediction(self, valid_size):
        poly = PolynomialFeatures(degree=2, include_bias=False)
        poly_x = poly.fit_transform(np.array([valid_size]).reshape(-1, 1))
        runtime_microseconds = self.ev_model.predict(poly_x)[0] #predict using poly regression

        output = str(timedelta(microseconds = runtime_microseconds).seconds) + " seconds"

        return output