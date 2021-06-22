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
from sklearn.metrics import f1_score, recall_score, precision_score, accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb
np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_colwidth',1000)

pip freeze > requirements.txt

main_path = 'drive/MyDrive/Colab Notebooks/dsai_hw4/dataset'

orders_DF = pd.read_csv(os.path.join(main_path, 'orders.csv'))  
prior_order_DF = pd.read_csv(os.path.join(main_path, 'order_products__prior.csv')) 
train_order_DF = pd.read_csv(os.path.join(main_path, 'order_products__train.csv')) 
products_DF = pd.read_csv(os.path.join(main_path, 'products.csv'))

orders_prior = orders_DF.loc[np.where(orders_DF['eval_set'] == 'prior')]
orders_train = orders_DF.loc[np.where(orders_DF['eval_set'] == 'train')]
orders_test  = orders_DF.loc[np.where(orders_DF['eval_set'] == 'test')] 
print('Prior case:', len(orders_prior))
print('Train case:', len(orders_train))
print('Test case:', len(orders_test))

# in this cell we can prove that test_set is get the all the test's user of its eval_set=prior and evaL_set=test to become test_set
previous_order_of_test = []
order_of_test = []

# get all the previous orders of test_orders, and keep in previous_order_of_test list
for i in range(orders_DF['order_id'].count()):
  if orders_DF['eval_set'][i] == 'test':
    previous_order_id = orders_DF['order_id'][i-1]
    test_order_id = orders_DF['order_id'][i]
    previous_order_of_test.append([previous_order_id, orders_DF['user_id'][i-1]])
    order_of_test.append([test_order_id, orders_DF['user_id'][i]])
    
previous_order_of_test = np.array(previous_order_of_test)
order_of_test = np.array(order_of_test)
print(previous_order_of_test.shape)
print(order_of_test.shape)
previous_order_of_test = pd.DataFrame(previous_order_of_test, columns = ['order_id','user_id'])
order_of_test = pd.DataFrame(order_of_test, columns = ['order_id','user_id'])
# print('Previous_order_of_test:')
# previous_order_of_test
# print('Order_of_test:')
# order_of_test

test_data = orders_DF.merge(previous_order_of_test, how='inner', on=['order_id','user_id'])
# print(test_data.shape)
test_data = test_data.merge(prior_order_DF, how='inner', on='order_id')
test_data = test_data.merge(products_DF, how='left', on='product_id')
# print(test_data.shape)



# test_data['aisle_id'].value_counts()
# for row in test_data.iterrows():
#   if test_data['user_id'][row]

test_data = test_data[['user_id','order_id','product_id','add_to_cart_order','order_number','eval_set','order_dow','order_hour_of_day','days_since_prior_order','aisle_id','department_id','reordered']]
test_data = test_data.sort_values(by=['user_id','order_id','product_id'])
# print(test_data.head(10))
test_data = test_data.set_index(['user_id','product_id'])
# print(test_data.head(10))
# print(test_data.shape)
# test_data

# later move up
# aisle_count = test_data[test_data['user_id']==4]['aisle_id'].value_counts()
# print(aisle_count.sort_values())
# aisle_prefer_list.insert([aisle_count[:][:3]])
# print(aisle_prefer_list)

train_data = orders_DF.merge(train_order_DF, how='inner', on='order_id')
train_data = train_data.merge(products_DF, how='left', on='product_id')
train_data = train_data[['user_id','order_id','product_id','add_to_cart_order','order_number','eval_set','order_dow','order_hour_of_day','days_since_prior_order','aisle_id','department_id','reordered']]
train_data = train_data.set_index(['user_id','product_id'])
# print(train_data.head(10))
# print(train_data.shape)
# train_data

train_data = train_data.drop(['eval_set','order_id'], axis=1)
X = train_data[['add_to_cart_order','order_number','order_dow','order_hour_of_day','days_since_prior_order','aisle_id','department_id']]
Y = train_data['reordered'].astype(np.int)

x_train, x_validate, y_train, y_validate = train_test_split(X,Y , test_size = 0.2, random_state=42)
print('x_train:')
print(x_train.shape)
print('y_train:')
print(y_train.shape)
print('x_validate:')
print(x_validate.shape)
print('y_validate:')
print(y_validate.shape)

test_data = test_data.drop(['eval_set','order_id'], axis=1)
x_test = test_data[['add_to_cart_order','order_number','order_dow','order_hour_of_day','days_since_prior_order','aisle_id','department_id']]
y_test = test_data['reordered'].astype(np.int)

parameters = {'eval_metric':'logloss', 
              'max_depth':'5', 
              'colsample_bytree':'0.5',
              'subsample':'0.80',
              'gpu_id':'0',
              'tree_method':'gpu_hist'
             }

print(x_train.shape)
print(y_train.shape)
XGB = xgb.XGBClassifier(objective='binary:logistic', parameters=parameters, num_boost_round=50)
model = XGB.fit(x_train, y_train)
print(model)
xgb.plot_importance(model)
model.get_xgb_params()

y_pred = model.predict(x_validate)
acc = accuracy_score(y_validate, y_pred)
fl_score = f1_score(y_validate, y_pred)

print('===Validate_set===')
print('Acc:',acc)
print('F1score:',fl_score)
print(y_pred.shape)

y_pred = model.predict(x_test)
acc = accuracy_score(y_test, y_pred)
fl_score = f1_score(y_test, y_pred)
print('===Test_set===')
print('Acc:',acc)
print('F1score:',fl_score)
print(y_pred.shape)

# prepare submission's dataframe
submission_table = orders_DF.loc[orders_DF['eval_set'] == 'test', ['user_id','order_id']]
# print(submission_table.head(10))

y_pred = pd.DataFrame(y_pred, columns=['reordered'])

test_data2 = test_data.drop(['reordered'], axis=1)
test_data2 = test_data2.reset_index()
test_data2['reordered'] = y_pred
# print(test_data2.head(10))
# test_data2 = test_data2.set_index(['user_id','product_id'])


submission_table = submission_table.merge(test_data2, how='left', on='user_id')
# print(submission_table)
submission_table = submission_table[['order_id','product_id','reordered']]
# print(submission_table)

output_result = dict()
for row in submission_table.itertuples():
  if row.reordered == 1:
    try:
      output_result[row.order_id] += ' ' + str(row.product_id)
    except:
      output_result[row.order_id] = str(row.product_id)

for order in submission_table.order_id:
  if order not in output_result:
    output_result[order] = 'None'

submission = pd.DataFrame.from_dict(output_result, orient='index')
submission.reset_index(inplace=True)
submission.columns = ['order_id','products']
# print(submission.head(50))
# submission
submission.to_csv('submission.csv',index=False)