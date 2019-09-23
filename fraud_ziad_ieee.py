# -*- coding: utf-8 -*-
"""Fraud_Ziad_IEEE.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lCsEiws8woEYsbeuphy_TYiIbG1NMUL6
"""

# Run this cell to mount your Google Drive.
from google.colab import drive
drive.mount('/content/drive')

import os
os.chdir('/content/drive/My Drive/Kaggle Detection Fraud/IEEE Fraud Detection/ieee-fraud-detection')

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
RANDOM_SEED = 2019

train_transaction = pd.read_csv('train_transaction.csv', index_col='TransactionID')
test_transaction = pd.read_csv('test_transaction.csv', index_col='TransactionID')

train_identity = pd.read_csv('train_identity.csv', index_col='TransactionID')
test_identity = pd.read_csv('test_identity.csv', index_col='TransactionID')

sample_submission = pd.read_csv('sample_submission.csv', index_col='TransactionID')

train = train_transaction.merge(train_identity, how='left', left_index=True, right_index=True)
test = test_transaction.merge(test_identity, how='left', left_index=True, right_index=True)

print(train.shape)
print(test.shape)

y_train = train[['TransactionDT', 'isFraud']]
del train_transaction, train_identity, test_transaction, test_identity

"""# Steps to do with the variables
 0. Replace empty card with bfill method  : Done
 1. Create the date  : Done
 2. Fill the Other type for mobile / desktop and banking type  : Done
 2. Transaction Amount Averaged ( mean and std per group) : Done
 3. ID Columns that need to be analyzed ( Proxy , IP country , ISP etc ...)  : To be done
 4. C Columns count to be summed and std  : Done
 5. D Columns to be also averaged : Done
 7. Country of IP and country of address  : Done
 8. Number of decimals in a transaction  : To be Done
 9. V columns with decimals to be averaged by card / deducted from transactions  : To be Done
 10. V columns with count to take std by group and take care of NAN : To be Done
 11. Email Domains  : Done
 12. Clean Device Info / Type of Mobile etc ... : To be done
"""

import datetime

START_DATE = '2017-12-01'
startdate = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
train["Date"] = train['TransactionDT'].apply(lambda x: (startdate + datetime.timedelta(seconds=x)))

train['_Weekdays'] = train['Date'].dt.dayofweek
train['_Hours'] = train['Date'].dt.hour
train['_Days'] = train['Date'].dt.day


START_DATE = '2017-12-01'
startdate = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
test["Date"] = test['TransactionDT'].apply(lambda x: (startdate + datetime.timedelta(seconds=x)))

test['_Weekdays'] = test['Date'].dt.dayofweek
test['_Hours'] = test['Date'].dt.hour
test['_Days'] = test['Date'].dt.day

train[[ 'card2' , 'card3' , 'card4' , 'card5' , 'card6']] = train[['card1' , 'card2' , 'card3' , 'card4' , 'card5' , 'card6']].groupby('card1').fillna(method = 'bfill')
test[[ 'card2' , 'card3' , 'card4' , 'card5' , 'card6']] = test[['card1' , 'card2' , 'card3' , 'card4' , 'card5' , 'card6']].groupby('card1').fillna(method = 'bfill')

C_col = [col for col in train if col.startswith('C')]
for C in C_col:
    train[C + '_to_mean_card1'] = train[C] / train.groupby(['card1'])[C].transform('mean')
    train[C + 'mean_card1'] = train.groupby(['card1'])[C].transform('mean')
    test[C + '_to_mean_card1'] = test[C] / test.groupby(['card1'])[C].transform('mean')
    test[C + 'mean_card1'] = test.groupby(['card1'])[C].transform('mean')

train.loc[(train.id_31.notna()) & (train.DeviceType.isna()), 'DeviceType'] = 'desktop'
test.loc[(test.id_31.notna()) & (test.DeviceType.isna()), 'DeviceType'] = 'desktop'

train.loc[(train.id_01.notna()) & (train.DeviceType.isna()), 'DeviceType'] = 'other'
test.loc[(test.id_01.notna()) & (test.DeviceType.isna()), 'DeviceType'] = 'other'

train['TransactionAmt_to_mean_CARD'] = train['TransactionAmt'] / train.groupby(['card1'])['TransactionAmt'].transform('mean')
train['Transaction_mean_CARD'] = train.groupby(['card1'])['TransactionAmt'].transform('mean')
test['TransactionAmt_to_mean_CARD'] = test['TransactionAmt'] / test.groupby(['card1'])['TransactionAmt'].transform('mean')
test['Transaction_mean_CARD'] = test.groupby(['card1'])['TransactionAmt'].transform('mean')

D_col = ['D1', 'D3', 'D4', 'D5', 'D6', 'D8', 'D9', 'D10', 'D11', 'D13', 'D14','D15']
for D in D_col:
    train[D + '_to_mean_card1'] = train[D] / train.groupby(['card1'])[D].transform('mean')
    train[D + 'mean_card1'] = train.groupby(['card1'])[D].transform('mean')
    test[D + '_to_mean_card1'] = test[D] / test.groupby(['card1'])[D].transform('mean')
    test[D + 'mean_card1'] = test.groupby(['card1'])[D].transform('mean')

train[['P_emaildomain_1', 'P_emaildomain_2', 'P_emaildomain_3']] = train['P_emaildomain'].str.split('.', expand=True)
train[['R_emaildomain_1', 'R_emaildomain_2', 'R_emaildomain_3']] = train['R_emaildomain'].str.split('.', expand=True)
test[['P_emaildomain_1', 'P_emaildomain_2', 'P_emaildomain_3']] = test['P_emaildomain'].str.split('.', expand=True)
test[['R_emaildomain_1', 'R_emaildomain_2', 'R_emaildomain_3']] = test['R_emaildomain'].str.split('.', expand=True)

# PROXY Value  = id_23
train.loc[(train.id_31.notna()) & (train.id_23.isna()), 'id_23'] = 'IP_PROXY:NOPROXY'
test.loc[(test.id_31.notna()) & (test.id_23.isna()), 'id_23'] = 'IP_PROXY:NOPROXY'

#Website Tracker id_32
train.loc[(train.id_31.notna()) & (train.id_32.isna()), 'id_32'] = -1
test.loc[(test.id_31.notna()) & (test.id_32.isna()), 'id_32'] = -1

# Mobile Fabricant id_13 : (49 ,52 , 64 Apple ? SAmsung ? )

#id_17 : Country IP and NAN
#Country of IP and mapping 
# First Part : 166.0 is not US = 87 
# 2nd part when 225 it is mostly NA and the rest are countries ( 225 and 87 )


# Create 3 categories : 
# 1 . NOT US IP with address in US
# 2 . NOT US country with US billing
# 3 . NO IP and US billing 
# 4 : Foreign transaction 
# 5 : NAn billing address

mask0 = ((train['id_17'] != 166.0) & (train['id_17'].notna())& (train['addr2'] == 87) & (train['id_31'].notna()))
mask1 = ((train['id_17'] == 166.0) & (train['addr2'] != 87) & (train['id_31'].notna()))
mask2 = ((train['id_17'] != 166.0) & (train['id_17'].notna()) & (train['addr2'] != 87) & (train['id_31'].notna()))
mask3 = train['id_31'].isna()
mask4 = ((train['id_17'] == 166.0) & (train['addr2'] == 87) & (train['id_31'].notna()))
mask5 = ((train['id_17'].isna()) & (train['addr2'] == 87) & (train['id_31'].notna()))

train['Country_IP'] = np.select([mask0, mask1 , mask2, mask3 , mask4 , mask5], 
                            [ 0, 1 , 2  , 3 , 4 , 5], 
                            default=np.nan)




mask0 = ((test['id_17'] != 166.0) & (test['id_17'].notna())& (test['addr2'] == 87) & (test['id_31'].notna()))
mask1 = ((test['id_17'] == 166.0) & (test['addr2'] != 87) & (test['id_31'].notna()))
mask2 = ((test['id_17'] != 166.0) & (test['id_17'].notna()) & (test['addr2'] != 87) & (test['id_31'].notna()))
mask3 = test['id_31'].isna()
mask4 = ((test['id_17'] == 166.0) & (test['addr2'] == 87) & (test['id_31'].notna()))
mask5 = ((test['id_17'].isna()) & (test['addr2'] == 87) & (test['id_31'].notna()))



test['Country_IP'] = np.select([mask0, mask1 , mask2, mask3 , mask4 , mask5], 
                            [ 0, 1 , 2  , 3 , 4 , 5], 
                            default=np.nan)

"""## V Col treatment"""

V_col = [col for col in train if col.startswith('V')]
train[V_col].describe(include = "all")

percent_missing = train[V_col].isnull().sum() * 100 / len(train[V_col])
missing_value_df = pd.DataFrame({'column_name': V_col,
                                 'percent_missing': percent_missing})

V_to_keep = list(missing_value_df[missing_value_df['percent_missing'] < 25]['column_name'])

V_to_remove = list(missing_value_df[missing_value_df['percent_missing'] >= 25]['column_name'])

for V in V_to_keep:

  train[V + '_to_mean_CARD1'] = train[V] / train.groupby(['card1'])[V].transform('mean')
  #train[V + '_mean_CARD1'] = train.groupby(['card1'])[V].transform('mean')
  test[V + '_to_mean_CARD1'] = test[V] / test.groupby(['card1'])[V].transform('mean')
  #test[V + '_mean_CARD1'] = test.groupby(['card1'])[V].transform('mean')

train = train.drop(V_to_remove , axis = 1)
test = test.drop(V_to_remove , axis  = 1)

train = train.drop(V_to_keep , axis = 1)
test = test.drop(V_to_keep , axis  = 1)

#upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

# Find index of feature columns with correlation greater than 0.95
#V_to_drop = [column for column in upper.columns if any(upper[column] > 0.98)]

train.shape

#one_value_cols = [col for col in V_col if train[col].nunique() <= 1]
#one_value_cols_test = [col for col in V_col if test[col].nunique() <= 1]
#one_value_cols == one_value_cols_test


#%%
#many_null_cols = [col for col in V_col if train[col].isnull().sum() / train.shape[0] > 0.9]
#many_null_cols_test = [col for col in V_col if test[col].isnull().sum() / test.shape[0] > 0.9]


#%%
#big_top_value_cols = [col for col in V_col if train[col].value_counts(dropna=False, normalize=True).values[0] > 0.9]
#big_top_value_cols_test = [col for col in V_col if test[col].value_counts(dropna=False, normalize=True).values[0] > 0.9]


#%%
#cols_to_drop = list(set(many_null_cols + many_null_cols_test +
                        #big_top_value_cols +
                       # big_top_value_cols_test +
                        #one_value_cols+ one_value_cols_test))
#len(cols_to_drop)

# 9. V columns with decimals to be averaged by card / deducted from transactions  : To be Done
# 10. V columns with count to take std by group and take care of NAN : To be Done

# Correlation columns to remove > 0.98
# Create counts for some V values of count and some V values of acrual values
# Create new colummn where some V decimal values - Transaction Amount + Average / STD

V_float = ['V263' , 'V264' , 'V265' , 'V267' , 'V268' , 'V270' , 'V271' , 'V272' , 'V273' , 'V274' , 'V275' , 'V277'  ,'V307' ,  'V312' , 'V313' , 'V314' , 'V315']

for V in V_float:

    train[V + 'diff_TransactionAmt'] = train[V] - train['TransactionAmt']
    test[V + 'diff_TransactionAmt'] = test[V] - test['TransactionAmt']

V_diff_col = train.columns[train.columns.str.contains(pat = 'diff_TransactionAmt')]

for V in V_diff_col:

  train[V + 'diff_to_mean_CARD'] = train[V] / train.groupby(['card1'])[V].transform('mean')
  train[V + 'diff_mean_CARD'] = train.groupby(['card1'])[V].transform('mean')
  test[V + 'diff_to_mean_CARD'] = test[V] / test.groupby(['card1'])[V].transform('mean')
  test[V + 'diff_mean_CARD'] = test.groupby(['card1'])[V].transform('mean')

#id_01 to id_11

# Some values to be kept : id_01 , id_11 , id_12 
# replace NAN when device is found or not . 
id_to_drop = ['id_02' , 'id_03' , 'id_04' , 'id_05' ,'id_06' , 'id_07' ,'id_08' , 'id_09' , 'id_10' ]

# Found not found sections 
# Found_Col = list the columns where found /not found new and clean NA 
Found_col = ['id_12' , 'id_15' , 'id_16' , 'id_28' , 'id_29' , 'id_34' , 'id_35' , 'id_36' , 'id_37' , 'id_38' ]

#Decimal values in order to get number of decimal points after transaction amount
# We can std / average based on group


def change(hoge):
    num = 3
    hoge = int(hoge*1000)
    while(hoge % 10 ==0):
        num = num-1
        hoge = hoge /10
    if num<0:
        num = 0
    return num
  
  
train["TransactionAmt_decimal"] = train["TransactionAmt"].map(change)
test["TransactionAmt_decimal"] = test["TransactionAmt"].map(change)

# 12. Clean Device Info / Type of Mobile etc ...

#Take copies of dataframes
df_train = train.copy()
df_test = test.copy()

df_train.shape

#To drop columns

cols_to_drop = list(set(D_col + C_col + id_to_drop))
len(cols_to_drop)

df_train = df_train.drop(cols_to_drop, axis=1)
df_test = df_test.drop(cols_to_drop, axis=1)

"""To drop addr1 
To check dist 1 and dist 2 
to check V value and drop : 
Correlations 
High NAN values
Sum / average of counts of V1, V2 etc ....

1.   List item
2.   List item

> Indented block

> Indented block

> Indented block

> Indented block
"""

to_drop = ['card1' , 'id_12',  'id_14', 'id_15', 'id_16', 'id_17', 'id_18', 'id_19', 'id_20', 'id_21', 'id_22', 'id_24', 'id_25', 'id_26', 'id_27', 'id_28', 'id_29' ,
           'id_33', 'id_34', 'id_35', 'id_36', 'id_37', 'id_38','DeviceInfo' , 'addr1']

df_train = df_train.drop(to_drop, axis=1)
df_test = df_test.drop(to_drop, axis=1)

df_train['card5'].value_counts(dropna = False)

# Check card 2 , card 3 and card 5

#Label Encode categorical columns
cat_cols = [ 'id_23', 
            'id_30', 'id_31', 'id_32',  'DeviceType', 'ProductCD', 'card4', 'card6', 'M4'
            'card2', 'card3',  'card5', 'addr2', 'M1', 'M2', 'M3', 'M5', 'M6', 'M7', 'M8', 'M9',
            'P_emaildomain_1', 'P_emaildomain_2', 'P_emaildomain_3', 'R_emaildomain_1', 'R_emaildomain_2', 'R_emaildomain_3']
for col in cat_cols:
    if col in df_train.columns:
        le = LabelEncoder()
        le.fit(list(df_train[col].astype(str).values) + list(df_test[col].astype(str).values))
        df_train[col] = le.transform(list(df_train[col].astype(str).values))
        df_test[col] = le.transform(list(df_test[col].astype(str).values))

card_to_drop = ['card2' , 'card3' , 'card5']

df_train = df_train.drop(card_to_drop, axis=1)
df_test = df_test.drop(card_to_drop, axis=1)

df_train = df_train.drop('TransactionAmt', axis=1)
df_test = df_test.drop('TransactionAmt', axis=1)

corr_matrix = df_train[V_col].corr().abs()

upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

# Find index of feature columns with correlation greater than 0.95
V_to_drop = [column for column in upper.columns if any(upper[column] > 0.98)]

df_train = df_train.drop('Date' , axis = 1)
df_test = df_test.drop('Date' , axis = 1)

def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.        
    """
    start_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
    
    return df




X_train = reduce_mem_usage(df_train)
X_test = reduce_mem_usage(df_test)

df_test.index

X_train = X_train.sort_values('TransactionDT').drop([ 'TransactionDT'], axis=1)
y_train = y_train.sort_values('TransactionDT')['isFraud']
X_test = X_test.sort_values('TransactionDT').drop(['TransactionDT'], axis=1)

X_train = X_train.drop('isFraud' , axis = 1)

from sklearn.model_selection import StratifiedKFold
nfold = 5
skf = StratifiedKFold(n_splits=nfold, shuffle=True, random_state=42)

nfold = 5
oof = np.zeros(len(X_train))
predictions = np.zeros(len(X_test))
feature_importance_df = pd.DataFrame()
features = [c for c in X_train.columns]

params = {'num_leaves': 1000,
          'min_child_weight': 0.03454472573214212,
          'feature_fraction': 0.8,
          'bagging_fraction': 0.4181193142567742,
          'min_data_in_leaf': 106,
          'objective': 'binary',
          'max_depth': 20,
          'learning_rate': 0.05,
          "boosting_type": "gbdt",
          "bagging_seed": 11,
          "metric": 'auc',
          "verbosity": -1,
          'reg_alpha': 0.3899927210061127,
          'reg_lambda': 0.6485237330340494,
          'random_state': 47
         }

import lightgbm as lgb  
print('Light GBM Model')
for fold_, (trn_idx, val_idx) in enumerate(skf.split(X_train, y_train.values)):
    
    X_train1, y_train1 = X_train.iloc[trn_idx], y_train.iloc[trn_idx]
    X_valid, y_valid = X_train.iloc[val_idx], y_train.iloc[val_idx]
    
    print("Fold idx:{}".format(fold_ + 1))
    trn_data = lgb.Dataset(X_train1, label=y_train1)
    val_data = lgb.Dataset(X_valid, label=y_valid)
    
    clf = lgb.train(params, trn_data, 1000, valid_sets = [trn_data, val_data], verbose_eval=100, early_stopping_rounds = 50 )
    
    oof[val_idx] = clf.predict(X_train.iloc[val_idx], num_iteration=clf.best_iteration)
    
    fold_importance_df = pd.DataFrame()
    fold_importance_df["feature"] = features
    fold_importance_df["importance"] = clf.feature_importance()
    fold_importance_df["fold"] = fold_ + 1
    feature_importance_df = pd.concat([feature_importance_df, fold_importance_df], axis=0)
    
    predictions += clf.predict(X_test, num_iteration=clf.best_iteration)/nfold

predictions

fold_importance_df.sort_values(by = 'importance' , ascending = False)

import gc
gc.enable()
gc.collect()
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
EPOCHS = 3

y_preds = np.zeros(sample_submission.shape[0])
y_oof = np.zeros(X_train.shape[0])

X_train = X_train.drop(columns = ['P_emaildomain' , 'R_emaildomain' , 'M4'] , axis = 1)
X_test = X_test.drop(columns = ['P_emaildomain' , 'R_emaildomain' , 'M4'] , axis = 1)

X_train = X_train.fillna(-999)
X_test = X_test.fillna(-999)

print("xgbclassifier")

for tr_idx, val_idx in skf.split(X_train, y_train):
    clf =  xgb.XGBClassifier(
        n_estimators=1000,
        max_depth=9,
        learning_rate=0.048,
        subsample=0.85,
        colsample_bytree=0.85,
        missing=-999,
        reg_alpha=0.15,
        reg_lamdba=0.85,
      tree_method='gpu_hist')
    
    X_tr, X_vl = X_train.iloc[tr_idx, :], X_train.iloc[val_idx, :]
    y_tr, y_vl = y_train.iloc[tr_idx], y_train.iloc[val_idx]
    clf.fit(X_tr, y_tr.values.ravel() )
    y_pred_train = clf.predict_proba(X_vl)[:,1]
    y_oof[val_idx] = y_pred_train
    print('ROC AUC {}'.format(roc_auc_score(y_vl, y_pred_train)))
    
    y_preds+= clf.predict_proba(X_test)[:,1] / EPOCHS

X_test['Pred'] = y_preds

X_test['Pred'] = predictions

X_test.index

y_preds

y_pred_ziad =  X_test['Pred'].sort_index()

predictions

X_test = X_test.drop(columns = 'Pred' , axis = 1)

sample_submission['isFraud'] = predictions
sample_submission.to_csv('simple_xgboost_19092019_v3.csv')

y_preds