#Program  to convert lightgbm models to tensorflow lite format


import numpy as np
import lightgbm as lgb
from hummingbird.ml import convert, load
import torch
import onnx
from torch.utils.mobile_optimizer import optimize_for_mobile
import xgboost as xgb


training_data = np.load('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/training_featuresv7.npz')
X_train = training_data['data']
print(X_train[0])

#load the model
loaded_model = lgb.Booster(model_file='/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v7/lightgbm_modelv7v15.model')

#get the number of features from the model
num_features = loaded_model.num_feature()

print("Number of features: "+ str(num_features))

#reshape the input data to match the expected shape of the model
X_train = X_train.reshape(-1, num_features)

# Convert the model to PyTorch
model = convert(loaded_model, 'pytorch')

input_shape = (1, num_features) 
dummy_input = torch.randn(input_shape, requires_grad=True)

print(type(model))

#save the pytorch model
torch.save(model, 'modelTester.pt')

#convert model to onnx
input_shape = (1, num_features) 
dummy_input = torch.randn(input_shape, requires_grad=True)
model_onnx = torch.onnx.export(model.model, dummy_input, "modelv9.onnx")

#Now use the onnx2tf library to convert the onnx model to tensorflow through the command line!

