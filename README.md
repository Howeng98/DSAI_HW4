# DSAI_HW4  Instacart Matket Basket Analysis

report link : https://drive.google.com/file/d/1JnWbQoqiQV2CXxa3LJdPzi0VyxGclkF6/view

competition link: https://www.kaggle.com/c/instacart-market-basket-analysis


## Environment

  - **Ubuntu 20.04LTS**
  - **XGBoost (model)**
  - **Google Colab**


## Build

請把各種csv的資料集用名叫dataset的文件夾統一管理，且放至與dsai_hw4.py同一個目錄下

```
python3 dsai_hw4.py
```

## Training Data

串接各種csv，整合後以兩個**index** ( ``user_id`` , ``product_id`` ) 以及七個features為 ``training features``。

<p align="center">
  <img src='https://user-images.githubusercontent.com/44123278/122802610-1e7a8380-d2f8-11eb-907d-dbdde5548bf4.PNG'>
</p>


## Test Data

以``eval_set``為**test**的前一個``prior``為**purchase history**

<p align="center">
  <img src='https://user-images.githubusercontent.com/44123278/122802786-5e416b00-d2f8-11eb-9f55-a3193363752c.PNG'>
</p>

## Output

<p align="center">
  <img src='https://user-images.githubusercontent.com/44123278/122801284-7e702a80-d2f6-11eb-8ee8-b5be0cde752e.png'>
</p>

<p align="center">
  <img src='https://user-images.githubusercontent.com/44123278/122801138-57b1f400-d2f6-11eb-8a49-a69cd946a157.PNG'>
</p>
