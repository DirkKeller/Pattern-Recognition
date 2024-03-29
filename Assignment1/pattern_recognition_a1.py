# -*- coding: utf-8 -*-
"""Pattern Recognition a1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TYFTmrfaYUCCen_WCF4ZoDhcpGyeP_jQ
"""

!pip install scikit-optimize

#!pip install scikit-optimize
import os
import cv2
import time
import random
import warnings
import numpy as np
import pandas as pd

from google.colab import drive
import matplotlib.pyplot as plt

from skopt import BayesSearchCV
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score
from statsmodels.stats.contingency_tables import mcnemar

warnings.filterwarnings(action='ignore', category=FutureWarning)
warnings.filterwarnings(action='ignore', category=UserWarning)

# Since the mnist.csv is soooooooo big, and it take a long time to upload it
# so you can just store it in your Google drive, and connect it with the following code, then you don't need to re-upload it every time
# (But you need to sign in every time)
drive.mount('/content/drive',force_remount=True)

# since we work in the Colab environment, but maybe sometimes will run in the local environment, so just check if the file exists.
if os.path.isfile("D:/mnist.csv"):
  path = 'D:/'
  mnist_data = pd.read_csv(filepath_or_buffer='D:/mnist.csv', header=0).values
elif os.path.isfile('/content/drive/MyDrive/mnist.csv'):
  path = '/content/drive/MyDrive/'
  mnist_data = pd.read_csv(filepath_or_buffer='/content/drive/MyDrive/mnist.csv', header=0).values
else:
  path = '/content/drive/MyDrive/Colab Notebooks/'
  mnist_data = pd.read_csv(filepath_or_buffer='/content/drive/MyDrive/Colab Notebooks/mnist.csv', header=0).values

labels = mnist_data[:,0] #np.array(mnist_data['label'])
digits = mnist_data[:,1:] #np.array(mnist_data.drop('label', axis=1))
# This part just the example of display an image of a digit
img_size = 28
plt.imshow(digits[0,:].reshape(img_size, img_size))
plt.show()

"""
Q1 & Q2：
"""
x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

temp = np.array(sum(digits)/len(digits))
temp.reshape(img_size, img_size)

plt.imshow(temp.reshape(img_size, img_size))
# plt.title('average pixel distribution')
plt.colorbar()
plt.show()

print("average useless variables:",sum(i==0 for i in temp))

temp = mnist_data
temp_y=[]
for i in range(10):
  temp_x = temp[temp[:,0] == i][:,1:]
  temp_x = np.array(sum(temp_x)/len(temp_x))
  temp_y.append(sum(j==0 for j in temp_x))
plt.bar(x,temp_y,label='useless variables distribution',color='#12D3B0',ec='k')
for a,b in zip(x,temp_y):
  plt.text(a,b,b,ha='center')

# plt.title('useless pixel for each class')
plt.ylabel('The number of uninformative pixels')
plt.xlabel('Numbers')
plt.show()



Y = []

for i in range(10):
    y = np.sum(labels == i)
    Y.append(y)

plt.bar(x,Y,label='class distribution',color='#12D3B0',ec='k')
plt.ylabel('numbers of classes')
plt.xlabel('Numbers')

for a,b in zip(x,Y):
  plt.text(a,b,b,ha='center')

plt.show()
# """
# Q2：
# """
# create ink feature
ink = np.array([sum(row) for row in digits])
# compute mean for each digit class
ink_mean = [np.mean(ink[labels == i]) for i in range(10)]

# compute standard deviation for each digit class
ink_std = [np.std(ink[labels == i]) for i in range(10)]

y = ink_mean
e = ink_std

# fig = plt.figure()

# ax1 = fig.add_subplot(111)
# _bars_ = ax1.bar(x,Y,label='class distribution',color='#12D3B0',ec='k')
# plt.ylabel('numbers of classes')


# ax2 = ax1.twinx()
# _errorbar_ = ax2.errorbar(x, y, e, linestyle='None', fmt='o:', label='ink mean and standard deviation ', ecolor='hotpink', mfc='wheat', mec='salmon')
plt.errorbar(x, y, e, linestyle='None', fmt='o:', label='ink mean and standard deviation ', ecolor='hotpink', mfc='wheat', mec='salmon')
plt.xlabel('Numbers')
plt.ylabel('ink mean and standard deviation')
plt.legend()

# lns = [_bars_,_errorbar_]
# labels_plot = [l.get_label() for l in lns]
# plt.legend(lns,labels_plot)
plt.tight_layout()
plt.show()

print(ink_mean)
print(ink_std)

"""
Q3：
"""
from skimage.feature import hog
list_hog_fd = []
for feature in digits:
  fd = hog(feature.reshape((28,28)),orientations=9, pixels_per_cell=(14,14),cells_per_block=(1,1))
  list_hog_fd.append(fd)
hog_features = np.array(list_hog_fd,'float64')

# An example
plt.imshow(digits[7,:].reshape(img_size, img_size))
plt.colorbar()
plt.show()
# plt.imshow(hog_features[7].reshape(6, 6))
# plt.colorbar()
# plt.show()

Y = []
x = [temp*5 for temp in range(36)]
for i in range(36):
    y = hog_features[7][i]
    Y.append(y)

plt.bar(x,Y,label='HOG value of number 3',color='#12D3B0',ec='k')
plt.ylabel('Amplitude')
plt.xlabel('Angle')
plt.legend()

hog_ink = np.array([sum(row) for row in hog_features])
len(hog_ink)

hog_ink_0 = []
hog_ink_1 = []
hog_ink_2 = []
hog_ink_3 = []
hog_ink_4 = []
hog_ink_5 = []
hog_ink_6 = []
hog_ink_7 = []
hog_ink_8 = []
hog_ink_9 = []
hog_ink_class = []
for count,i in enumerate(labels):
  if i == 0:
    hog_ink_0.append(hog_ink[count])
  if i == 1:
    hog_ink_1.append(hog_ink[count])
  if i == 2:
    hog_ink_2.append(hog_ink[count])
  if i == 3:
    hog_ink_3.append(hog_ink[count])
  if i == 4:
    hog_ink_4.append(hog_ink[count])
  if i == 5:
    hog_ink_5.append(hog_ink[count])
  if i == 6:
    hog_ink_6.append(hog_ink[count])
  if i == 7:
    hog_ink_7.append(hog_ink[count])
  if i == 8:
    hog_ink_8.append(hog_ink[count])
  if i == 9:
    hog_ink_9.append(hog_ink[count])
hog_ink_class.append(hog_ink_0)
hog_ink_class.append(hog_ink_1)
hog_ink_class.append(hog_ink_2)
hog_ink_class.append(hog_ink_3)
hog_ink_class.append(hog_ink_4)
hog_ink_class.append(hog_ink_5)
hog_ink_class.append(hog_ink_6)
hog_ink_class.append(hog_ink_7)
hog_ink_class.append(hog_ink_8)
hog_ink_class.append(hog_ink_9)

hog_ink_mean = [np.mean(i) for i in hog_ink_class]

# compute standard deviation for each digit class
hog_ink_std = [np.std(i) for i in hog_ink_class]

y = hog_ink_mean
e = hog_ink_std

# fig = plt.figure()

# ax1 = fig.add_subplot(111)
# _bars_ = ax1.bar(x,Y,label='class distribution',color='#12D3B0',ec='k')
# plt.ylabel('numbers of classes')


# ax2 = ax1.twinx()
# _errorbar_ = ax2.errorbar(x, y, e, linestyle='None', fmt='o:', label='ink mean and standard deviation ', ecolor='hotpink', mfc='wheat', mec='salmon')
#plt.errorbar(x, y, e, linestyle='None', fmt='o:', ecolor='hotpink' ,label='hog mean and standard deviation ' , mfc='wheat', mec='salmon')
#plt.xlabel('Numbers')
#plt.ylabel('HOG features mean and standard deviation')
#plt.legend()

Y = []

x = [temp*5 for temp in range(36)]

for i in range(36):

    y = hog_features[7][i]

    Y.append(y)


y =[0, '', 10, '', 20, '', 30, '', 40, '', 50, '', 60, '', 70, '', 80, '', 90, '', 100, '', 110, '', 120, '', 130, '', 140, '', 150, '', 160, '', 170, '']
print(len(y))
plt.figure(figsize=(6, 5))
plt.bar(np.arange(36), Y, facecolor='turquoise', edgecolor='turquoise', width=1.0)
plt.xticks(np.arange(36), y, rotation=45)
plt.xlabel('Angle')
plt.ylabel('Amplitude')

len(np.arange(0, 180, 5))

""" Q4 """

# # Features
# ink = np.array([sum(row) for row in digits])
# hog_ink = np.array([sum(row) for row in hog_features])

# # Hold-out test set: Train/test split
# data = train_test_split(digits, labels, test_size=.119047619047619, random_state=5, shuffle=True)

# """ Define the parameter values and distributions"""
# # Logistic regression
# #C_lr = np.arange(0.1, 1000, 0.1, dtype=float)

# #param_dist_lr = dict(C=C_lr)

# # Initialize models
# lr = LogisticRegressionCV(cv=5,penalty='l1',
#                         solver='liblinear',
#                         random_state=5,
#                         max_iter=150)

# # Test whether the accuracy of a model has significantly improved over the other
# significance_test(data[3], pred, m_names)

""" Q5: Hyperparameter tuning with Crossvalidation"""
def Hyperparam_tuning(data_sets, models, param_dists, model_names, hp_tune='baysian', CV=10, ITER=25):
    train_x, test_x, train_y, test_y = data_sets
    selection = []
    model_predictions=[]
    best_models=[]

    for i, model in enumerate(models):
        # Train and validate model.
        print(f'\n-------------------------------------------------------------------',
              f'\n                      {model_names[i]}',
              f'\n-------------------------------------------------------------------')
        
        if hp_tune == 'grid':
            model = GridSearchCV(models[i],
                                param_dists[i],
                                cv=CV,
                                scoring='f1_weighted', 
                                verbose=3,
                                n_jobs=14
                                )

        elif hp_tune == 'random':
            model = RandomizedSearchCV(models[i],
                                      param_dists[i],
                                      cv=CV,
                                      scoring='f1_weighted', 
                                      n_iter=ITER,
                                      random_state=5,
                                      verbose=3,
                                      n_jobs=14
                                      )

        elif hp_tune == 'baysian':
            model = BayesSearchCV(models[i],
                                  param_dists[i],
                                  cv=CV, 
                                  scoring='f1_weighted', 
                                  n_iter=ITER,  
                                  random_state=5,
                                  verbose=3,
                                  n_jobs=-1,
                                  n_points=ITER
                                  )
        else:
            print(f'Please specify one of the following hyperparameter tuning methods: "grid", "random" or "baysian"!')
            break

        model.fit(train_x, train_y)
        best_models.append(model.best_estimator_)
        print(f'Best estimator: {model.best_estimator_}',
              f'score of best estimator: {model.best_score_}', 
              f'best parameters setting: {model.best_params_}')     

        # Test and print the required measures of performances.
        tic = time.time()
        model_full_train = model.best_estimator_.fit(train_x, train_y)  
        print(f'Run time to executed best {model_names[i]}: {(time.time() - tic)}s')
        pred_y=model_full_train.predict(test_x)    
        model_predictions.append(pred_y)

        print(f'model: {model_names[i]}.',
              f'accuracy: {accuracy_score(test_y,pred_y)}.',
              f'precision: {precision_score(test_y,pred_y, average="weighted")}.',
              f'recall: {recall_score(test_y, pred_y, average="weighted")}.',
              f'F1 : {f1_score(test_y,pred_y, average="weighted")}.')
        cm = confusion_matrix(test_y, pred_y)
        
        ax = sb.heatmap(cm, annot = True, fmt = 'g')
        ax.set(xlabel="Predicted", ylabel="Actual")
        ax.get_figure().savefig(f'{path}/{model_names[i]}_confusionmatrix.png')

        # Performance summary
        d=pd.DataFrame(model.cv_results_)
        pd.DataFrame(model.cv_results_)[['mean_test_score', 'std_test_score', 'params']]
        selection.append(f'{models[i]}: Best parameters {model.best_score_}, best score  {model.best_score_}')

        # Visualization of hyperparameter tuning
        for j, param in enumerate(param_dists[i]):
            results = pd.DataFrame({'param': list(model.cv_results_['param_'+param]),
                                  'score': list(model.cv_results_['mean_test_score'])})

            results.sort_values(by=['param'], inplace=True)

            fig = plt.figure(figsize=(8, 5))

            ax = plt.gca()
            ax.scatter(results.iloc[:,0],
                      results.iloc[:,1],
                      color=[(random.random(), random.random(), random.random())],
                      s=20,
                      label=f'{model_names[i]}: {param} value');

            plt.xlabel(f'{param} value')
            plt.ylabel(f'Mean test score')  
            plt.title(param);
            plt.savefig(f'{path}/{model_names[i]}_{param}.png')

    return model_predictions

""" Q6: Model Selection """
# Significance testing (McNemar)
def significance_test(true_y, model_predictions, model_names):
    for i in range(len(model_predictions)):
        bool_i=model_predictions[i]==true_y
        for j in range(len(model_predictions)):
            if i < j:
              bool_j= model_predictions[j]==true_y
              table = pd.crosstab(bool_i, bool_j)
              print(f"cross table of {model_names[i]} with {model_names[j]}: {table}")
              result = mcnemar(table, exact=True)
              print(f"MCNEMAR TEST--> statistics value: {result.statistic}, pvalue: {result.pvalue} ")

""" Define the parameter values and distributions"""
# Logistic regression
C_lr = np.arange(0.01, 100, 0.01, dtype=float)

# Support vector machine
g = np.arange(0.01, 10, 0.01, dtype=float)
C_svm = np.arange(0.01, 100, 0.01, dtype=float)
kernel_type = ['poly', 'rbf', 'sigmoid']
deg = np.arange(2, 10, 1, dtype=float)

param_dist_lr = dict(C=C_lr)
param_dist_svm = dict(C=C_svm, gamma=g, kernel=kernel_type, degree=deg)

# Initialize models
lr = LogisticRegression(penalty='l1',
                        solver='liblinear',
                        random_state=5,
                        max_iter=500)

svm = SVC(decision_function_shape='ovo',
          random_state=5,
          max_iter=500)

m = [svm, lr] 
pardists = [param_dist_svm, param_dist_lr]
m_names = ['Support Vector Machine', 'Logistic Regression']

# Construct Majority class prediction
pred_mc = [1]*len(data[3])

print(f'\n-------------------------------------------------------------------',
      f'\n                      Majority Class',
      f'\n-------------------------------------------------------------------')

print(f'model: Majority Class.',
      f'accuracy: {accuracy_score(data[3],pred_mc)}.',
      f'precision: {precision_score(data[3],pred_mc, average="weighted")}.',
      f'recall: {recall_score(data[3], pred_mc, average="weighted")}.',
      f'F1 : {f1_score(data[3],pred_mc, average="weighted")}.')

# Run Hyperperameter search
pred = Hyperparam_tuning(data, m, pardists, m_names, hp_tune='baysian', CV=5, ITER=15) 

m_names.insert(0, 'Majority Class')
pred.insert(0, pred_mc)

# Test whether the accuracy of a model has significantly improve over the other
significance_test(data[3], pred, m_names)