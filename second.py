# -*- coding: utf-8 -*-
"""my.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hx2D7pJpsAdGJx90vXo5SRmCq9iyOo-M
"""



# %pwd

# Commented out IPython magic to ensure Python compatibility.
import math
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.datasets import fetch_california_housing
import pandas as pd
import numpy as np
from matplotlib import style
import seaborn as sns
#sets matplotlib to inline and displays graphs below the corresponding cell.
# %matplotlib inline
style.use('fivethirtyeight')
sns.set(style = 'whitegrid', color_codes=True)
import warnings
warnings.filterwarnings('ignore')
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

"""**process patients dataset before training**
New column age, healthcare_coverage_ratio
"""

def patients_reader(data, goal):
  data.DEATHDATE.fillna("2021-01-01", inplace = True)
  data.DEATHDATE = pd.to_datetime(data["DEATHDATE"])
  data.BIRTHDATE = pd.to_datetime(data["BIRTHDATE"])
  data['age'] = data.DEATHDATE - data.BIRTHDATE
  data['age'] = data.age.astype('timedelta64[Y]').astype('int')
  data['healthcare_coverage_ratio'] = data.HEALTHCARE_COVERAGE / data.HEALTHCARE_EXPENSES
  data["dataset"] = goal
  data.MARITAL.fillna("S", inplace = True)
  data.drop_duplicates(inplace = True)
  data = data[['Id', 'age', 'MARITAL', 'RACE', 'ETHNICITY', 'GENDER', 'CITY', 'COUNTY', 'healthcare_coverage_ratio']]
  data = data.rename(columns = {"Id": "patient"})
  return data

patients = pd.read_csv("covid/100k_synthea_covid19_csv/patients.csv")
patients_test = pd.read_csv("covid/10k_synthea_covid19_csv/patients.csv")
patients = patients_reader(patients, "train")
patients_test = patients_reader(patients_test, "test")
print(patients)

def mode_finder(x):
  m = pd.Series.mode(x)
  return m.values[0] if not m.empty else np.nan

#careplan
careplan_df = pd.read_csv("covid/100k_synthea_covid19_csv/careplans.csv")
careplan_df_test = pd.read_csv("covid/10k_synthea_covid19_csv/careplans.csv")
careplan_df.DESCRIPTION = careplan_df.DESCRIPTION.apply(lambda x: x.replace("(", ""))
careplan_df.DESCRIPTION = careplan_df.DESCRIPTION.apply(lambda x: x.replace(")", ""))

careplan_df_test.DESCRIPTION = careplan_df_test.DESCRIPTION.apply(lambda x: x.replace("(", ""))
careplan_df_test.DESCRIPTION = careplan_df_test.DESCRIPTION.apply(lambda x: x.replace(")", ""))

#careplan
careplan_df = pd.read_csv("covid/100k_synthea_covid19_csv/careplans.csv")
careplan_df_test = pd.read_csv("covid/10k_synthea_covid19_csv/careplans.csv")
careplan_df.DESCRIPTION = careplan_df.DESCRIPTION.apply(lambda x: x.replace("(", ""))
careplan_df.DESCRIPTION = careplan_df.DESCRIPTION.apply(lambda x: x.replace(")", ""))

careplan_df_test.DESCRIPTION = careplan_df_test.DESCRIPTION.apply(lambda x: x.replace("(", ""))
careplan_df_test.DESCRIPTION = careplan_df_test.DESCRIPTION.apply(lambda x: x.replace(")", ""))


def careplan_reader(data, goal):
  data = data[['PATIENT', 'START', 'STOP', 'DESCRIPTION', 'REASONDESCRIPTION']]
  data.columns = ['patient', 'careplan_start', 'careplan_end', 'careplan_desc', 'careplan_reason']
  if goal == 'train':
    for i in data.careplan_desc.value_counts().index[:10]:
      name = i
      #print(data.careplan_desc.astype(str).str.contains(i[:15]))
      
      data.loc[data.careplan_desc.astype(str).str.contains(i[:15]), name] = 1
      #print(data.loc)
      data[name] = data.groupby("patient")[name].transform("max")
      data[name].fillna(0, inplace = True)
  else:
    for i in careplan_df.careplan_desc.value_counts().index[:10]:
      name =  i
      
      data.loc[data.careplan_desc.astype(str).str.contains(i[:15]), name] = 1
      data[name] = data.groupby("patient")[name].transform("max")
  
      data[name].fillna(0, inplace = True)
  data["patient's most seen careplan"] = data.groupby("patient")["careplan_desc"].transform(mode_finder)
  data = data.loc[data.careplan_reason == "COVID-19"].reset_index(drop = True)
  data["dataset"] = goal
  data.drop_duplicates(inplace = True)
  return data

careplan_df = careplan_reader(careplan_df, "train")
careplan_df_test = careplan_reader(careplan_df_test, "test")
careplan_df = pd.merge(careplan_df, patients, on = 'patient', how = 'left')
careplan_df_test = pd.merge(careplan_df_test, patients_test,  on='patient', how = "left")
print(careplan_df)
print(careplan_df_test)

#Conditions
conditions_df = pd.read_csv("covid/100k_synthea_covid19_csv/conditions.csv")
conditions_df_test = pd.read_csv("covid/10k_synthea_covid19_csv/conditions.csv")

conditions_df['DESCRIPTION'] = conditions_df['DESCRIPTION'].str.replace("(","")
conditions_df['DESCRIPTION'] = conditions_df['DESCRIPTION'].str.replace(")","")
                                                                           
conditions_df_test['DESCRIPTION'] = conditions_df_test['DESCRIPTION'].str.replace("(","")
conditions_df_test['DESCRIPTION'] = conditions_df_test['DESCRIPTION'].str.replace(")","")
features = conditions_df.DESCRIPTION.value_counts().index[:40]

def condition_reader(data, train = True):
    data = data[["PATIENT", "START", "STOP", "DESCRIPTION"]]
    data.columns = ["patient", "condition_start", "condition_stop", "condition_desc"]
    data.condition_start = pd.to_datetime(data.condition_start)
    data.condition_stop = pd.to_datetime(data.condition_stop)
    if train == True:
        for i in features:
            name = "patient's_condition_of_" + i
            data.loc[data.condition_desc.astype(str).str.contains(i[:10]), name] = 1
            data[name] = data.groupby("patient")[name].transform("max")
            data[name].fillna(0, inplace = True)
    else:
        for i in features:
            name = "patient's_condition_of_" + i
            data.loc[data.condition_desc.astype(str).str.contains(i[:10]), name] = 1
            data[name] = data.groupby("patient")[name].transform("max")
            data[name].fillna(0, inplace = True)
        
    data["patient's most seen condition"] = data.groupby("patient")["condition_desc"].transform(mode_finder)
    data["condition_duration"] = (data.condition_stop - data.condition_start).dt.days
    data["patient_condition_count"] = data.groupby("patient")["condition_desc"].transform("count") # how many conditions?
    data["patient_condition_unique"] = data.groupby("patient")["condition_desc"].transform("nunique") # how many unique conditions?
    data["patient_condition_days_avg"] = data.groupby("patient")["condition_duration"].transform("mean") # avg. day under conditions?
    data["patient_condition_days_sum"] = data.groupby("patient")["condition_duration"].transform("sum")
    data.drop_duplicates(subset = "patient", inplace = True) 
    return data

conditions_df = condition_reader(conditions_df)
conditions_df_test = condition_reader(conditions_df_test)
print(conditions_df)

needed_columns = []
for i in conditions_df.columns:
  if "patient" in i:
    needed_columns.append(i)
conditions_df = conditions_df[needed_columns].drop_duplicates()
conditions_df_test = conditions_df_test[needed_columns].drop_duplicates()
print(conditions_df)

conditions_df.head()

medications_df = pd.read_csv("covid/100k_synthea_covid19_csv/medications.csv")
medications_df_test = pd.read_csv("covid/10k_synthea_covid19_csv/medications.csv")
features = medications_df.DESCRIPTION.value_counts().index[:30]

def medication_reader(data, train = True):
    
    data = data[["PATIENT", "START", "STOP", "DESCRIPTION", "TOTALCOST", "REASONDESCRIPTION"]]
    data.columns = ["patient", "med_start", "med_stop", "med_desc", "med_total_cost", "med_reason"]
    data.med_start = pd.to_datetime(data.med_start)
    data.med_stop = pd.to_datetime(data.med_stop)
    data.med_desc = data.med_desc.replace([")", "("], "")
    if train == True:
        for i in features:
            name = "patient's_medication_of_" + i
            data.loc[data.med_desc.astype(str).str.contains(i[:15]), name] = 1
            data[name] = data.groupby("patient")[name].transform("max")
            data[name].fillna(0, inplace = True)
    else:
        for i in features:
            name = "patient's_medication_of_" + i
            data.loc[data.med_desc.astype(str).str.contains(i[:15]), name] = 1
            data[name] = data.groupby("patient")[name].transform("max")
            data[name].fillna(0, inplace = True)
        
    data["patient's most used medication"] = data.groupby("patient")["med_desc"].transform(mode_finder)
    data["patient's most usage reason"] = data.groupby("patient")["med_reason"].transform(mode_finder)
    data["med_duration"] = (data.med_stop - data.med_start).dt.days + 1
    data["total_med_duration_of_patient"] = data.groupby("patient")["med_duration"].transform("sum")
    data["total_med_cost_of_patient"] = data.groupby("patient")["med_total_cost"].transform("sum")
    data["total_med_count_of_patient"] = data.groupby("patient")["med_desc"].transform("count")
    data["total_unique_med_of_patient"] = data.groupby("patient")["med_desc"].transform("nunique")
    data.drop_duplicates(subset = "patient", inplace = True) 
    return data
        

medications_df = medication_reader(medications_df)
medications_df_test = medication_reader(medications_df_test, train = "False")
print(medications_df)

needed_columns = []
for i in medications_df.columns:
    if "patient" in i:
        needed_columns.append(i)
medications_df = medications_df[needed_columns].drop_duplicates()
medications_df_test = medications_df_test[needed_columns].drop_duplicates()

#Observations
observations_df = pd.read_csv("covid/100k_synthea_covid19_csv/observations.csv").sample(frac = 0.001)
observations_df_test = pd.read_csv("covid/10k_synthea_covid19_csv/observations.csv").sample(frac = 0.001)
observations_df_test.DESCRIPTION = observations_df_test.DESCRIPTION.replace([")", "/", "[", "/", "]",  "#","("], "")
observations_df.DESCRIPTION = observations_df.DESCRIPTION.replace([")", "/", "[", "/", "]",  "#","("], "")
observations_df["DESCRIPTION"] = observations_df["DESCRIPTION"].str.strip()     
observations_df["DESCRIPTION"] = observations_df["DESCRIPTION"].str.replace(' ', '_')         
observations_df["DESCRIPTION"] = observations_df["DESCRIPTION"].str.replace(r"[^a-zA-Z\d\_]+", "")    
observations_df["DESCRIPTION"] = observations_df["DESCRIPTION"].str.replace(r"[^a-zA-Z\d\_]+", "")
features = observations_df.DESCRIPTION.value_counts().index[:30]

def observation_reader(data,  train = True):
    data = data[["DATE", "PATIENT", "DESCRIPTION", "VALUE"]]
    data.columns = ["obs_date", "patient", "obs_desc", "obs_value"]
    data.obs_value.fillna(0, inplace = True)
    data.obs_desc = data.obs_desc.replace([")", "("], "")

    if train == True:
        for i in features:
            name = "patient's_observation_of_" + i
            data.loc[data.obs_desc.astype(str).str.contains(i[:15]), name] = data.loc[data.obs_desc.astype(str).str.contains(i[:15])].groupby("patient")["obs_value"].transform(mode_finder)
            #data[name] = data.groupby("patient")[name].transform("max")
            data[name].fillna(0, inplace = True)
            
    else:
        for i in features:
            name = "patient's_observation_of_" + i
            data.loc[data.obs_desc.astype(str).str.contains(i[:15]), name] = data.loc[data.obs_desc.astype(str).str.contains(i[:15])].groupby("patient")["obs_value"].transform(mode_finder)
            #data[name] = data.groupby("patient")[name].transform("max")

            data[name].fillna(0, inplace = True)
    
    data["patient's most seen observation"] = data.groupby("patient")["obs_desc"].transform(mode_finder)

    data["patient_obs_count"] = data.groupby("patient")["obs_desc"].transform("count")
    data["patient_obs_count_unique"] = data.groupby("patient")["obs_desc"].transform("nunique")   
    data.drop_duplicates(subset = "patient", inplace = True) 
    return data

observations_df = observation_reader(observations_df)
observations_df_test = observation_reader(observations_df_test, train =  "False")

needed_columns = []
for i in observations_df.columns:
    if "patient" in i:
        needed_columns.append(i)
observations_df = observations_df[needed_columns].drop_duplicates()
observations_df_test = observations_df_test[needed_columns].drop_duplicates()
observations_df.head()

encounters = pd.read_csv("covid/100k_synthea_covid19_csv/encounters.csv")
encounters_test = pd.read_csv("covid/10k_synthea_covid19_csv/encounters.csv")

features = encounters.DESCRIPTION.value_counts().index[:15]

def encounters_reader(data, train = True):
    data = data[["PATIENT", "ENCOUNTERCLASS", "DESCRIPTION"]]
    data["unique_encounters_per_patient"] = data.groupby("PATIENT")["DESCRIPTION"].transform("nunique")
    data = data.rename(columns = {"PATIENT": "patient"})
    if train == True:
      for i in features:
          name = i
          data.loc[data.DESCRIPTION.astype(str).str.contains(i[:15]), name] = 1
          data[name] = data.groupby("patient")[name].transform("max")
          data[name].fillna(0, inplace = True)
      for i in data.ENCOUNTERCLASS.unique():
          name = i
          data.loc[data.ENCOUNTERCLASS.astype(str).str.contains(i[:15]), name] = 1
          data[name] = data.groupby("patient")[name].transform("sum")
          data[name].fillna(0, inplace = True)
    else:
      for i in features:
          name =  i
          data.loc[data.DESCRIPTION.astype(str).str.contains(i[:15]), name] = 1
          data[name] = data.groupby("patient")[name].transform("sum")
          data[name].fillna(0, inplace = True)
      for i in devices.ENCOUNTERCLASS.unique():
          name = i
          data.loc[data.ENCOUNTERCLASS.astype(str).str.contains(i[:15]), name] = 1
          data[name] = data.groupby("patient")[name].transform("sum")
          data[name].fillna(0, inplace = True)
    
    data["patient's most seen encounter"] = data.groupby("patient")["DESCRIPTION"].transform(mode_finder)

    return data

encounters_df = encounters_reader(encounters)
encounters_df_test = encounters_reader(encounters_test)
encounters_df.head()

merged_train= pd.merge(careplan_df, conditions_df, on = ["patient"])
merged_train= pd.merge(merged_train, observations_df, on = ["patient"])
merged_train= pd.merge(merged_train, medications_df, on = ["patient"])

merged_train.columns

merged_train.info()

merged_train

merged_test= pd.merge(careplan_df_test, conditions_df_test, on = ["patient"])
merged_test= pd.merge(merged_test, observations_df_test, on = ["patient"])
merged_test= pd.merge(merged_test, medications_df_test, on = ["patient"])

merged_train = merged_train.drop_duplicates(subset = ["patient", "total_med_duration_of_patient"]).reset_index(drop = True)
merged_test = merged_test.drop_duplicates(subset = ["patient", "total_med_duration_of_patient"]).reset_index(drop = True)

merged_test.info()

data = pd.concat([merged_train,merged_test]).reset_index(drop = True)

data.careplan_end = pd.to_datetime(data.careplan_end)
data.careplan_start = pd.to_datetime(data.careplan_start)

print("We have {} unique patients.".format(data.patient.nunique()))

data.fillna(0, inplace = True)

data = data.drop([ "careplan_desc", "careplan_reason"], 1)

data.info()

df = data.copy()
df.head()

df = df.sort_values("careplan_start")
df.careplan_end = pd.to_datetime(df.careplan_end, format='%Y-%m-%d', errors='coerce')
df.careplan_start = pd.to_datetime(df.careplan_start, format='%Y-%m-%d', errors='coerce')
df["careplan_duration"] = (df.careplan_end - df.careplan_start).dt.days
df = df.reset_index(drop = True)
df.head()

df["start_month"] = df.careplan_start.dt.month
df["start_day"] = df.careplan_start.dt.day_of_year
df["start_week"] = df.careplan_start.dt.day_of_week
df["start_year"] = df.careplan_start.dt.year

df = df.drop_duplicates(subset = ["patient"]).reset_index(drop = True)
df.head()

corr = df.corr()
corr.style.background_gradient(cmap='coolwarm')

nums = df.select_dtypes(include = np.number).columns.tolist()
print(nums)
NUMERIC_FEATURES=[]
for i in nums:
  if i not in ["careplan_duration", "duration", "CODE"]:
    NUMERIC_FEATURES.append(i)

cats = df.select_dtypes(exclude=np.number).columns.tolist()
CATEGORICAL_FEATURES = []
for i in cats:
  if i not in ["patient", "careplan_start", "careplan_end", "dataset", "START", "STOP", "ENCOUNTER"]:
    CATEGORICAL_FEATURES.append(i)

for i in list(df.select_dtypes(['object']).columns):
  df[i] = df[i].astype("category")


from tensorflow.keras.callbacks import EarlyStopping
from tabtransformertf.models.fttransformer import FTTransformerEncoder, FTTransformer
from tabtransformertf.utils.preprocessing import df_to_dataset

def cat_analyser(data, col, freq_limit = None):
    if freq_limit == None:
        freq_limit = data[col].nunique()
        if freq_limit >= 12:
            freq_limit = 12
    df_ = data.copy()
    sns.set(rc = {'axes.facecolor': 'gainsboro',
                  'figure.facecolor': 'gainsboro'})
    if freq_limit < 6 or col == "Year":
        if df_[col].nunique() > freq_limit:
            df_ = df_.loc[df_[col].isin(df_[col].value_counts(). \
                                        keys()[:freq_limit].tolist())]
        fig, ax = plt.subplots(nrows = 1, ncols = 2, figsize = (15,7))
        plt.tight_layout()
        #fig.suptitle(col, fontsize = 16)
        a = sns.countplot(data = df_,
                    x = col,
                    ax = ax[0],
                    palette= "viridis",
                    order =  df_[col].value_counts().index)
        a.set_title(col, fontsize = 15)
        ax[0].set_xlabel('')
        pie_cmap = plt.get_cmap("Set3")
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) 
        data[col].value_counts()[:freq_limit].plot.pie(autopct = '%1.1f%%',
                                        textprops = {'fontsize': 12},
                                        ax = ax[1],
                                        colors = pie_cmap(normalize(df_[col].value_counts())))
        ax[1].set_ylabel('')
    
        plt.show()
        sns.reset_orig()
    else:
        fig, ax = plt.subplots(nrows = 1, ncols = 2, figsize = (18, freq_limit*1.5))
        #ax.set_title(col, fontsize = 16)
        a = sns.countplot(data = df_,
                    y = col,
                    ax = ax[0],
                    palette= "viridis",
                    order =  df_[col].value_counts()[:freq_limit].index)
        a.tick_params(axis = "x", rotation = 90)
        a.set_title(col, fontsize = 15)
        ax[0].set_xlabel('')
        pie_cmap = plt.get_cmap("Set3")
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) 
        data[col].value_counts()[:freq_limit].plot.pie(autopct = '%1.1f%%',
                                        textprops = {'fontsize': 12},
                                        ax = ax[1],
                                        colors = pie_cmap(normalize(df_[col].value_counts())))
        ax[1].set_ylabel('')
        plt.show()
        plt.tight_layout()
        sns.reset_orig()

data = df.copy()
data = data.rename(columns = {"careplan_duration" : "duration"})
data = data.loc[data.duration > 0].reset_index(drop = True)

nums = data.select_dtypes(include=np.number).columns.tolist()
NUMERIC_FEATURES = []
for i in nums:
  if i not in ["careplan_duration", "duration", "CODE"]:
    NUMERIC_FEATURES.append(i)

cats = data.select_dtypes(exclude=np.number).columns.tolist()
CATEGORICAL_FEATURES = []
for i in cats:
  if i not in ["patient", "careplan_start", "careplan_end", "dataset", "START", "STOP", "ENCOUNTER"]:
    CATEGORICAL_FEATURES.append(i)

for i in list(data.select_dtypes(['object']).columns):
  data[i] = data[i].astype("category")

y = data['duration']
LABEL = "duration"

test_data = data.loc[data.dataset == 'test'].drop(["dataset"], 1).reset_index(drop=True)
train_data = data.loc[data.dataset == 'train'].drop(['dataset'], 1).reset_index(drop = True)

print(test_data.info())

train_data[CATEGORICAL_FEATURES] = train_data[CATEGORICAL_FEATURES].astype('str')
test_data[CATEGORICAL_FEATURES] = test_data[CATEGORICAL_FEATURES].astype('str')

train_data[NUMERIC_FEATURES] = train_data[NUMERIC_FEATURES].astype(float)
test_data[NUMERIC_FEATURES] = test_data[NUMERIC_FEATURES].astype(float)

X_train, X_val = train_test_split(train_data, test_size = 0.2)

sc = StandardScaler()
X_train.loc[:, NUMERIC_FEATURES] = sc.fit_transform(X_train[NUMERIC_FEATURES])
X_val.loc[:, NUMERIC_FEATURES] = sc.transform(X_val[NUMERIC_FEATURES])
test_data.loc[:, NUMERIC_FEATURES] = sc.transform(test_data[NUMERIC_FEATURES])

FEATURES = list(NUMERIC_FEATURES) + list(CATEGORICAL_FEATURES)

print(X_train)
print(X_val)

train_dataset = df_to_dataset(X_train[FEATURES + [LABEL]], LABEL)
val_dataset = df_to_dataset(X_val[FEATURES + [LABEL]], LABEL, shuffle=False)  # No shuffle
test_dataset = df_to_dataset(test_data[FEATURES + [LABEL]], shuffle=False) # No target, no shuffle

print(train_dataset)

ft_linear_encoder = FTTransformerEncoder(
    numerical_features = NUMERIC_FEATURES,
    categorical_features = CATEGORICAL_FEATURES,
    numerical_data = X_train[NUMERIC_FEATURES].values,
    categorical_data = X_train[CATEGORICAL_FEATURES].values,
    y = X_train[LABEL].values,
    numerical_embedding_type='linear',
    embedding_dim=32,
    depth=4,
    heads=8,
    attn_dropout=0.3,
    ff_dropout=0.3,
    explainable=True
)

ft_linear_transformer = FTTransformer(
    encoder=ft_linear_encoder,
    out_dim=1,
    out_activation="relu",
)

LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001
NUM_EPOCHS = 50

import tensorflow_addons as tfa
optimizer = tfa.optimizers.AdamW(
        learning_rate=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )


import tensorflow as tf
ft_linear_transformer.compile(
    optimizer = optimizer,
    loss = {"output": tf.keras.losses.MeanSquaredError(name='mse'), "importances": None},
    metrics= {"output": [tf.keras.metrics.RootMeanSquaredError(name='rmse')], "importances": None},
)
early = EarlyStopping(monitor="val_output_loss", mode="min", patience=16, restore_best_weights=True)
callback_list = [early]

from mpi4py import MPI
import numpy as np
import tensorflow as tf

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(size)

if rank == 0:
   train_dataset_np = np.array(list(train_dataset.as_numpy_iterator()))
   val_dataset_np = np.array(list(val_dataset.as_numpy_iterator()))
   train_dataset_split = np.array_split(train_dataset_np, size)
   val_dataset_split = np.array_split(val_dataset_np, size)
else:
   train_dataset_split = None
   val_dataset_split = None
train_data = comm.scatter(train_dataset_split, root = 0)
val_data = comm.scatter(val_dataset_split, root = 0)
print("wow", type(train_data))
#print(train_data)
train_tf_dataset = tf.data.Dataset.from_tensor_slices(train_data)
val_tf_dataset = tf.data.Dataset.from_tensor_slices(val_data)
#train_tf_dataset = train_tf_dataset.shuffle(buffer_size = 10000)
train_tf_dataset = train_tf_dataset.prefetch(buffer_size = tf.data.experimental.AUTOTUNE)
val_tf_dataset = val_tf_dataset.prefetch(buffer_size = tf.data.experimental.AUTOTUNE)
ft_linear_history = ft_linear_transformer.fit(
    train_tf_dataset, 
    epochs=NUM_EPOCHS, 
    validation_data=val_tf_dataset,
    callbacks=callback_list)
print("rank:" , rank)




from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_absolute_percentage_error as mape
from sklearn.metrics import r2_score
if(rank == 0):
    linear_test_preds = ft_linear_transformer.predict(test_dataset)
    linear_rms = mean_squared_error(test_data[LABEL], linear_test_preds['output'].ravel(), squared = False)
    linear_mae = mae(test_data[LABEL], linear_test_preds['output'].ravel())

    test_copy = df.loc[(df.dataset == "test") & (df.careplan_duration.notnull())].copy()
    test_copy["preds"] = linear_test_preds['output'].ravel()
    test_copy["daily_preds_sum"] = test_copy.groupby("start_day")["preds"].transform("sum").astype(int)
    test_copy["daily_real_sum"] = test_copy.groupby("start_day")["careplan_duration"].transform("sum")
    temp = test_copy.drop_duplicates(subset = ["start_day", "daily_preds_sum", "daily_real_sum"])[["start_day", "daily_preds_sum", "daily_real_sum"]].sort_values("start_day")
    temp["daily_difference"] = abs(temp["daily_real_sum"] - temp["daily_preds_sum"])/temp.daily_real_sum
    plt.figure(figsize = (20,7))
    sns.lineplot(x = temp.start_day, y = temp.daily_difference)
    plt.title("Prediction / Real difference per days")
    plt.ylabel("% difference between real values and predictions ( Linear Encoding FT )")

    plt.figure(figsize = (20,7))
    sns.barplot(x = temp.daily_preds_sum[:20], y = temp.daily_real_sum[:20], palette = "inferno_r")
    plt.tight_layout()
    plt.yticks(np.arange(0,550,50))
    plt.title("Real / Predictions ( Linear Encoding FT )")
    plt.show()

    plt.figure(figsize = (20,7))
    sns.barplot(x = temp.start_day, y =temp.daily_difference, palette = "inferno_r")
    plt.tight_layout()
    plt.title("Daily differences between real values and predictions ( Linear Encoding FT )")

    results = pd.DataFrame({"mae" : [linear_mae],
                "rmse" : [linear_rms]}, index = ["Transformer - Linear Encoding"])
    results