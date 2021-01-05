# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14TTpj_aWYUuVl5u7Mm8mdYCgiMughCt9
"""

#!pip install streamlit

#!wget https://s3.amazonaws.com/video.udacity-data.com/topher/2019/January/5c4147f9_data/data.zip
#!unzip data

import streamlit as st
import pandas as pd
import numpy as np
import os
from difflib import SequenceMatcher
st.title("Report Analysis")
st.subheader('Count Vectorizer')
st.write('This project is based on Linear SVC classifier')
message = st.text_area("Original Text","Enter text here..")
message_1 = st.text_area("Possible Copied Text","Enter text here..")
if st.button('Predict'):
  s = SequenceMatcher(None,message,message_1).ratio()
  st.title(s)

csv_file = 'data/file_information.csv'
plagiarism_df = pd.read_csv(csv_file)
def numerical_dataframe(csv_file='file_information.csv'):
    df = pd.read_csv(csv_file)
    df.loc[:,'Class'] =  df.loc[:,'Category'].map({'non': 0, 'heavy': 1, 'light': 1, 'cut': 1, 'orig': -1})
    df.loc[:,'Category'] =  df.loc[:,'Category'].map({'non': 0, 'heavy': 1, 'light': 2, 'cut': 3, 'orig': -1})
    return df

transformed_df = numerical_dataframe(csv_file ='file_information.csv')
import re
import operator

def create_datatype(df, train_value, test_value, datatype_var, compare_dfcolumn, operator_of_compare, value_of_compare,
                    sampling_number, sampling_seed):
    df_subset = df[operator_of_compare(df[compare_dfcolumn], value_of_compare)]
    df_subset = df_subset.drop(columns = [datatype_var])
    
    df_subset.loc[:, datatype_var] = train_value
    
    df_sampled = df_subset.groupby(['Task', compare_dfcolumn], group_keys=False).apply(lambda x: x.sample(min(len(x), sampling_number), random_state = sampling_seed))
    df_sampled = df_sampled.drop(columns = [datatype_var])
    df_sampled.loc[:, datatype_var] = test_value
    
    for index in df_sampled.index: 
        df_subset.loc[index, datatype_var] = test_value

    for index in df_subset.index:
        df.loc[index, datatype_var] = df_subset.loc[index, datatype_var]
    
def train_test_dataframe(clean_df, random_seed=100):
    
    new_df = clean_df.copy()

    new_df.loc[:,'Datatype'] = 0

    create_datatype(new_df, 1, 2, 'Datatype', 'Category', operator.gt, 0, 1, random_seed)

    create_datatype(new_df, 1, 2, 'Datatype', 'Category', operator.eq, 0, 2, random_seed)
    
    mapping = {0:'orig', 1:'train', 2:'test'} 

    new_df.Datatype = [mapping[item] for item in new_df.Datatype] 

    return new_df


def process_file(file):
    all_text = file.read().lower()
    all_text = re.sub(r"[^a-zA-Z0-9]", " ", all_text)
    all_text = re.sub(r"\t", " ", all_text)
    all_text = re.sub(r"\n", " ", all_text)
    all_text = re.sub("  ", " ", all_text)
    all_text = re.sub("   ", " ", all_text)
    
    return all_text


def create_text_column(df, file_directory='data/'):
   
    text_df = df.copy()
    text = []
    
    for row_i in df.index:
        filename = df.iloc[row_i]['File']
        file_path = file_directory + filename
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:

            file_text = process_file(file)
            text.append(file_text)
    text_df['Text'] = text
    
    return text_df

text_df = create_text_column(transformed_df)

from unittest.mock import MagicMock, patch
import sklearn.naive_bayes
import numpy as np
import pandas as pd
import re

TEST_CSV = 'test_info.csv'

class AssertTest(object):
    '''Defines general test behavior.'''
    def __init__(self, params):
        self.assert_param_message = '\n'.join([str(k) + ': ' + str(v) + '' for k, v in params.items()])
    
    def test(self, assert_condition, assert_message):
        assert assert_condition, assert_message + '\n\nUnit Test Function Parameters\n' + self.assert_param_message

def _print_success_message():
    print('Tests Passed!')


def test_numerical_df(numerical_dataframe):
    transformed_df = numerical_dataframe(TEST_CSV)
                                
    assert isinstance(transformed_df, pd.DataFrame), 'Returned type is {}.'.format(type(transformed_df))
    
    column_names = list(transformed_df)
    assert 'File' in column_names, 'No File column, found.'
    assert 'Task' in column_names, 'No Task column, found.'
    assert 'Category' in column_names, 'No Category column, found.'
    assert 'Class' in column_names, 'No Class column, found.'
                                       
    assert transformed_df.loc[0, 'Category'] == 1, '`heavy` plagiarism mapping test, failed.'
    assert transformed_df.loc[2, 'Category'] == 0, '`non` plagiarism mapping test, failed.'
    assert transformed_df.loc[30, 'Category'] == 3, '`cut` plagiarism mapping test, failed.'
    assert transformed_df.loc[5, 'Category'] == 2, '`light` plagiarism mapping test, failed.'
    assert transformed_df.loc[37, 'Category'] == -1, 'original file mapping test, failed; should have a Category = -1.'
    assert transformed_df.loc[41, 'Category'] == -1, 'original file mapping test, failed; should have a Category = -1.'
    
    _print_success_message()


def test_containment(complete_df, containment_fn):
    
    test_val = containment_fn(complete_df, 1, 'g0pA_taske.txt')
    
    assert isinstance(test_val, float), 'Returned type is {}.'.format(type(test_val))
    assert test_val<=1.0, 'It appears that the value is not normalized; expected a value <=1, got: '+str(test_val)
    
    filenames = ['g0pA_taska.txt', 'g0pA_taskb.txt', 'g0pA_taskc.txt', 'g0pA_taskd.txt']
    ngram_1 = [0.39814814814814814, 1.0, 0.86936936936936937, 0.5935828877005348]
    ngram_3 = [0.0093457943925233638, 0.96410256410256412, 0.61363636363636365, 0.15675675675675677]
    
    results_1gram = []
    results_3gram = []
    
    for i in range(4):
        val_1 = containment_fn(complete_df, 1, filenames[i])
        val_3 = containment_fn(complete_df, 3, filenames[i])
        results_1gram.append(val_1)
        results_3gram.append(val_3)
        

    assert all(np.isclose(results_1gram, ngram_1, rtol=1e-04)), \
    'n=1 calculations are incorrect. Double check the intersection calculation.'
  
    assert all(np.isclose(results_3gram, ngram_3, rtol=1e-04)), \
    'n=3 calculations are incorrect.'
    
    _print_success_message()
    
def test_lcs(df, lcs_word):
    
    test_index = 10 
    
    answer_text = df.loc[test_index, 'Text'] 
    
    task = df.loc[test_index, 'Task']
    orig_rows = df[(df['Class'] == -1)]
    orig_row = orig_rows[(orig_rows['Task'] == task)]
    source_text = orig_row['Text'].values[0]
    
    test_val = lcs_word(answer_text, source_text)
    
    assert isinstance(test_val, float), 'Returned type is {}.'.format(type(test_val))
    assert test_val<=1.0, 'It appears that the value is not normalized; expected a value <=1, got: '+str(test_val)
    
    lcs_vals = [0.1917808219178082, 0.8207547169811321, 0.8464912280701754, 0.3160621761658031, 0.24257425742574257]
    
    results = []
    
    for i in range(5):
        answer_text = df.loc[i, 'Text'] 
        task = df.loc[i, 'Task']
        orig_rows = df[(df['Class'] == -1)]
        orig_row = orig_rows[(orig_rows['Task'] == task)]
        source_text = orig_row['Text'].values[0]
        val = lcs_word(answer_text, source_text)
        results.append(val)
        
    assert all(np.isclose(results, lcs_vals, rtol=1e-05)), 'LCS calculations are incorrect.'
    
    _print_success_message()
    
def test_data_split(train_x, train_y, test_x, test_y):
        
    assert isinstance(train_x, np.ndarray),\
        'train_x is not an array, instead got type: {}'.format(type(train_x))
    assert isinstance(train_y, np.ndarray),\
        'train_y is not an array, instead got type: {}'.format(type(train_y))
    assert isinstance(test_x, np.ndarray),\
        'test_x is not an array, instead got type: {}'.format(type(test_x))
    assert isinstance(test_y, np.ndarray),\
        'test_y is not an array, instead got type: {}'.format(type(test_y))
        
    assert len(train_x) + len(test_x) == 95, \
        'Unexpected amount of train + test data. Expecting 95 answer text files, got ' +str(len(train_x) + len(test_x))
    assert len(test_x) > 1, \
        'Unexpected amount of test data. There should be multiple test files.'
        
    assert train_x.shape[1]==2, \
        'train_x should have as many columns as selected features, got: {}'.format(train_x.shape[1])
    assert len(train_y.shape)==1, \
        'train_y should be a 1D array, got shape: {}'.format(train_y.shape)
    
    _print_success_message()

row_idx = 0 
sample_text = text_df.iloc[0]['Text']

random_seed = 1
complete_df = train_test_dataframe(text_df, random_seed=random_seed)

from sklearn.feature_extraction.text import CountVectorizer
def calculate_containment(df, n, answer_filename):
    
    answer_text, answer_task  = df[df.File == answer_filename][['Text', 'Task']].iloc[0]
    source_text = df[(df.Task == answer_task) & (df.Class == -1)]['Text'].iloc[0]
    
    counter = CountVectorizer(analyzer='word', ngram_range=(n,n))
    ngrams_array = counter.fit_transform([answer_text, source_text]).toarray()
    
    count_common_ngrams = sum(min(a, s) for a, s in zip(*ngrams_array))
    count_ngrams_a = ngrams_array[0].sum()
    
    return count_common_ngrams / count_ngrams_a

n = 3

test_indices = range(5)
category_vals = []
containment_vals = []
for i in test_indices:
    category_vals.append(complete_df.loc[i, 'Category'])
    filename = complete_df.loc[i, 'File']
    c = calculate_containment(complete_df, n, filename)
    containment_vals.append(c)

def lcs_norm_word(answer_text, source_text):
    
    a_words = answer_text.split()
    s_words = source_text.split()
    
    a_word_count = len(a_words)
    s_word_count = len(s_words)
        
    lcs_matrix = np.zeros((s_word_count + 1, a_word_count + 1), dtype=int)

    for s, s_word in enumerate(s_words, 1):
        for a, a_word in enumerate(a_words, 1):
            if s_word == a_word:
                lcs_matrix[s][a] = lcs_matrix[s-1][a-1] + 1
            else:
                lcs_matrix[s][a] = max(lcs_matrix[s-1][a], lcs_matrix[s][a-1])
    
    lcs = lcs_matrix[s_word_count][a_word_count]
    
    return lcs / a_word_count

test_indices = range(5) 

category_vals = []
lcs_norm_vals = []
for i in test_indices:
    category_vals.append(complete_df.loc[i, 'Category'])
    answer_text = complete_df.loc[i, 'Text'] 
    task = complete_df.loc[i, 'Task']
    orig_rows = complete_df[(complete_df['Class'] == -1)]
    orig_row = orig_rows[(orig_rows['Task'] == task)]
    source_text = orig_row['Text'].values[0]
    
    lcs_val = lcs_norm_word(answer_text, source_text)
    lcs_norm_vals.append(lcs_val)

def create_containment_features(df, n, column_name=None):
    
    containment_values = []
    
    if(column_name==None):
        column_name = 'c_'+str(n) # c_1, c_2, .. c_n
    
    for i in df.index:
        file = df.loc[i, 'File']
        if df.loc[i,'Category'] > -1:
            c = calculate_containment(df, n, file)
            containment_values.append(c)
        else:
            containment_values.append(-1)
    
    print(str(n)+'-gram containment features created!')
    return containment_values

def create_lcs_features(df, column_name='lcs_word'):
    
    lcs_values = []
    
    for i in df.index:
        if df.loc[i,'Category'] > -1:
            answer_text = df.loc[i, 'Text'] 
            task = df.loc[i, 'Task']
            orig_rows = df[(df['Class'] == -1)]
            orig_row = orig_rows[(orig_rows['Task'] == task)]
            source_text = orig_row['Text'].values[0]

            lcs = lcs_norm_word(answer_text, source_text)
            lcs_values.append(lcs)
        else:
            lcs_values.append(-1)

    print('LCS features created!')
    return lcs_values

ngram_range = range(1,21)
features_list = []

all_features = np.zeros((len(ngram_range)+1, len(complete_df)))
i=0
for n in ngram_range:
    column_name = 'c_'+str(n)
    features_list.append(column_name)
    all_features[i]=np.squeeze(create_containment_features(complete_df, n))
    i+=1

features_list.append('lcs_word')
all_features[i]= np.squeeze(create_lcs_features(complete_df))

features_df = pd.DataFrame(np.transpose(all_features), columns=features_list)

def train_test_data(complete_df, features_df, selected_features):
    df = pd.concat([complete_df, features_df[selected_features]], axis=1)    
    df_train = df[df.Datatype == 'train']
    df_test = df[df.Datatype == 'test']

    train_x = df_train[selected_features].values
    train_y = df_train['Class'].values
    
    test_x = df_test[selected_features].values
    test_y = df_test['Class'].values
    
    return (train_x, train_y), (test_x, test_y)

selected_features = ['c_1', 'c_11', 'lcs_word']

(train_x, train_y), (test_x, test_y) = train_test_data(complete_df, features_df, selected_features)

def make_csv(x, y, filename, data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    pd.concat([pd.DataFrame(y), pd.DataFrame(x)], axis=1).to_csv(os.path.join(data_dir, filename), header=False, index=False)

data_dir = 'plagiarism_data'
make_csv(train_x, train_y, filename='train.csv', data_dir=data_dir)
make_csv(test_x, test_y, filename='test.csv', data_dir=data_dir)

import argparse
import os
import pandas as pd
from sklearn.externals import joblib
from sklearn.svm import LinearSVC

def model_fn(model_dir):
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model

train_data = pd.read_csv('plagiarism_data/train.csv',header=None,names=None)
X_train = train_data.iloc[:,1:].values
y_train = train_data.iloc[:,0].values
model = LinearSVC()
model.fit(train_x, train_y)
test_data = pd.read_csv('plagiarism_data/test.csv', header=None, names=None)
y_test = test_data.iloc[:,0]
X_test = test_data.iloc[:,1:]
y_pred = model.predict(X_test)

df = pd.concat([pd.DataFrame(X_test), pd.DataFrame(y_test), pd.DataFrame(y_pred)], axis=1)
df.columns=['c_1', 'c_11', 'lcs_word', 'class', 'predicted']

