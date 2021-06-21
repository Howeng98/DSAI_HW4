# -*- coding: utf-8 -*-
"""DSAI_HW4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EmTaKnyWQK3hR4_BCBJpNAbQl6Kne1rX
"""

!nvidia-smi

from google.colab import drive
drive.mount('/content/drive')

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Flatten, Conv2D, MaxPool2D, BatchNormalization, Activation
from keras.optimizers import Adam, SGD
from sklearn.preprocessing import MinMaxScaler
from statistics import mean
from keras import backend as K
from sklearn.metrics import f1_score, recall_score, precision_score
from keras.callbacks import Callback
from sklearn.model_selection import train_test_split
from tqdm import tqdm 
from keras.utils import np_utils
import xgboost as xgb
np.set_printoptions(threshold=sys.maxsize)

main_path = 'drive/MyDrive/Colab Notebooks/dsai_hw4/dataset'

ordersDf = pd.read_csv(os.path.join(main_path, 'orders.csv'))  
priorDf = pd.read_csv(os.path.join(main_path, 'order_products__prior.csv')) 
trainDf = pd.read_csv(os.path.join(main_path, 'order_products__train.csv')) 
productDf = pd.read_csv(os.path.join(main_path, 'products.csv'))

rows, cols = (1000,50000)
x_train = [[0]*cols]*rows
for i in range(rows):
  order_id = trainDf['order_id'][i]  
  for j in range(100):
    if trainDf['order_id'][j] == order_id:
      product_id = trainDf['product_id'][j]
      x_train[i][product_id] = 1      
      
x_train = np.array(x_train)
print(x_train.shape)
####################################################

y_train  = [[0]*cols]*rows
for i in range(rows):
  order_id = trainDf['order_id'][i]
  for j in range(100):
    if trainDf['order_id'][j] == order_id:
      if trainDf['reordered'][j] == 1:
        product_id = trainDf['product_id'][j]
        y_train[i][product_id] = 1

y_train = np.array(y_train)
print(y_train.shape)
####################################################

previous_order_of_test = []
order_of_test = []

# get all the previous orders of test_orders, and keep in previous_order_of_test list
for i in range(ordersDf['order_id'].count()):
  if ordersDf['eval_set'][i] == 'test':
    previous_order_id = ordersDf['order_id'][i-1]
    test_order_id = ordersDf['order_id'][i]
    previous_order_of_test.append(previous_order_id)
    order_of_test.append(test_order_id)

previous_order_of_test = np.array(previous_order_of_test)
order_of_test = np.array(order_of_test)
print(previous_order_of_test.shape)
print(order_of_test.shape)
####################################################

# x_train, x_validate, y_train, y_validate = train_test_split(x_train, y_train, test_size=0.2, random_state=42)
# print(x_train.shape)
# print(y_train.shape)
# print(x_validate.shape)
# print(y_validate.shape)

# x_train = x_train[np.newaxis,:,:]
# y_train = y_train[np.newaxis,:,:]
# x_validate = x_validate[np.newaxis,:,:]
# y_validate = y_validate[np.newaxis,:,:]
# print(x_train.shape)
# print(y_train.shape)
# print(x_validate.shape)
# print(y_validate.shape)



x_test = [[0]*cols]*rows

for index in tqdm(range(0, rows)):  
  order_id = previous_order_of_test[index]
  target_orders = priorDf[priorDf['order_id']==order_id]
  # print(target_orders)
  for j in range(target_orders['order_id'].count()):
    x_test[index][target_orders.iat[j-1, 1]] = 1
  
x_test = np.array(x_test)
print(x_test.shape)

def build_model(shape):
  model = Sequential()
  # model.add(LSTM(units=20, input_shape=(shape[1],shape[2]), return_sequences=True, activation='tanh'))
  # model.add(Dropout(0.2))
  # model.add(LSTM(20, activation='tanh'))
  # model.add(Dropout(0.2))  
  # model.add(Dense(50000))   
  # model.summary()

  model.add(LSTM(20, input_shape=(shape[1], shape[2]), return_sequences=True))  
  model.add(Dropout(0.2))
  model.add(Activation("sigmoid"))
  
  model.add(LSTM(20, return_sequences=True))
  model.add(Dropout(0.2))
  # model.add(Activation("sigmoid"))
  # model.add(LSTM(20, return_sequences=True))
  # model.add(Dense(50000))
  model.add(Dense(50000, activation='sigmoid'))
  model.summary()
  return model    

# Build model
model = build_model(x_train.shape)

# Variables
epochs = 50
batch_size = 32
lr = 0.001

parameters = {'eval_metric':'logloss', 
              'max_depth':'5', 
              'colsample_bytree':'0.5',    # 0.4
              'subsample':'0.75',
              'gpu_id':'0',
              'tree_method':'gpu_hist'
             }
# X_train, y_train = x_train.drop('reordered', axis=1), x_train.reordered.astype(np.int)
print(x_train.shape)
print(y_train.shape)
XGB = xgb.XGBClassifier(objective='binary:logistic', parameters=parameters, num_boost_round=10)
model = XGB.fit(x_train, y_train)
xgb.plot_importance(model)

model.get_xgb_params()

print(x_train.shape)
print(y_train.shape)
print(x_validate.shape)
print(y_validate.shape)
reduce_lr = tf.keras.callbacks.LearningRateScheduler(lambda x: 1e-3 * 0.90 ** x)
# sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=1.0)
model.compile(loss='binary_crossentropy', optimizer='adam')
history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(x_validate, y_validate),shuffle=False, callbacks=[reduce_lr])

# Plotting
fig = plt.figure()
plt.plot()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='lower right')
plt.savefig('model_accuracy.png')
plt.show()

plt.plot()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.savefig('model_loss.png')
plt.show()

# from sklearn.ensemble import RandomForestClassifier
# print(x_train.shape)
# x_train = x_train.reshape(x_train.shape[0], x_train.shape[1]*x_train.shape[2])
# print(x_train.shape)
# # y_train = y_train[0]
# y_train = y_train.reshape(y_train.shape[0], y_train.shape[1]*y_train.shape[2])
# # x_validate  = x_validate[0]
# # y_validate  = y_validate[0]
# rfc = RandomForestClassifier()
# rfc.fit(x_train, y_train)
# # print('The accuracy of RFC:', rfc.score(x_validate,y_validate))

# x_test = x_test[np.newaxis,:,:]
print(x_test.shape)
x_test = x_test[np.newaxis,:,:]
result = model.predict(x_test)

print(result.shape)
count = 0
# print(result[0][:100])

for i in range(1000):
  for j in range(50000):
    if result[0][i][j] > 0.519:
      count = count + 1

print(count)
# print(result[0][0][329])

user_orders = [0]*80
print(ordersDf[ordersDf["eval_set"]=="train"].count())

for index in range(trainDf['order_id'].count()):
  if trainDf.iat[index, 0] != trainDf.iat[index-1, 0]:
    # print(trainDf.iat[index-1, 2])
    user_orders[trainDf.iat[index-1, 2]-1] = user_orders[trainDf.iat[index-1, 2]-1] +1

print(user_orders)

fig = plt.figure(figsize = (10, 5))
x = [0]*80

for index in range(1, 80):
  x[index-1] = index

ax = fig.add_axes([0,0,1,1])
ax.bar(x,user_orders)
ax.set_ylabel('times',fontsize= 12)
ax.set_xlabel('# of product',fontsize= 12)
ax.set_title('all # of product purchased in trainning orders')
plt.show()