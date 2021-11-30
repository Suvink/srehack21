#!/usr/bin/env python
# coding: utf-8

import os
import nltk
import numpy as np
import json
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt
from nltk.stem.lancaster import LancasterStemmer
from string import punctuation
high_training_set = []
medium_training_set = []

high_test_set = []
medium_test_set = []
stemmer = LancasterStemmer()
all_words=[]


def load_training_data(sentiment):
    data = open("./traindata/priority_data/"+sentiment+"_training_set.txt",encoding="utf8")
    if sentiment == "high":        
        threshold = 0.5
    elif sentiment == "medium":
        threshold = 0.5
    elif sentiment == "low":
        threshold = 0.5
    else:
        pass
    return data,threshold


def load_test_data(sentiment):
    data = open("./traindata/priority_data/"+sentiment+"_test_set.txt",encoding="utf8")
    return data


def clean_data(training_data,threshold):
    training_set = []
    for line in training_data:
        line = line.strip().lower()
        if line.split()[-1] == "none":
            line = " ".join(filter(lambda x:x[0]!='@', line.split()))
            punct = line.maketrans("","",'.*%$^0123456789#!][\?&/)/(+-<>')
            result = line.translate(punct)
            tokened_sentence = nltk.word_tokenize(result)
            sentence = tokened_sentence[0:len(tokened_sentence)-1]
            label = tokened_sentence[-2]
            training_set.append((sentence,label))
        else:
            intensity = float(line.split()[-1])        
            if (intensity>=threshold):
                line = " ".join(filter(lambda x:x[0]!='@', line.split()))
                punct = line.maketrans("","",'.*%$^0123456789#!][\?&/)/(+-<>')
                result = line.translate(punct)
                tokened_sentence = nltk.word_tokenize(result)
                sentence = tokened_sentence[0:len(tokened_sentence)-1]
                label = tokened_sentence[-1]
                training_set.append((sentence,label))
    return training_set
    
def bag_of_words(all_data):
    training_set = []
    all_words = []
    for each_list in all_data:
        for words in each_list[0]:
            word = stemmer.stem(words)
            all_words.append(word)
    all_words = list(set(all_words))
    
    for each_sentence in all_data:  
        bag = [0]*len(all_words)
        training_set.append(encode_sentence(all_words,each_sentence[0],bag))
    return training_set,all_words

def encode_sentence(all_words,sentence, bag):
    for s in sentence:        
        stemmed_word = stemmer.stem(s)
        for i,word in enumerate(all_words):
            if stemmed_word == word:
                bag[i] = 1
    return bag
    
    
def main():
    bag = [] 
    all_data = []
    all_test_data = []
    labels = []
    classes = []
    labels = []
    test_labels = []
    words=[]
    test_words = []
        
    high_training_data,threshold = load_training_data("high")
    high_training_set = clean_data(high_training_data,threshold)
    
    medium_training_data,threshold = load_training_data("medium")
    medium_training_set = clean_data(medium_training_data,threshold)
    
    low_training_data,threshold = load_training_data("low")
    low_training_set = clean_data(low_training_data,threshold)
    
    high_test_data = load_test_data("high")
    high_test_set = clean_data(high_test_data,threshold)
    print(len(high_test_set))
    
    medium_test_data = load_test_data("medium")
    medium_test_set = clean_data(medium_test_data,threshold)
    print(len(medium_test_set))
    
    low_test_data = load_test_data("low")
    low_test_set = clean_data(low_test_data,threshold)
    print(len(low_test_set))
    
    all_data.extend(high_training_set)
    all_data.extend(medium_training_set)
    all_data.extend(low_training_set)

    all_data.extend(high_test_set)
    all_data.extend(medium_test_set)
    all_data.extend(low_test_set)
    
    
    for i,j in all_data:
        if j == "high":            
            labels.append([1,0,0,0])
        elif j == "medium":            
            labels.append([0,1,0,0])
        elif j == "low":            
            labels.append([0,0,1,0])
        else:
            pass

    print(len(labels))
    print(len(test_labels))
    classes = ["high","medium","low"]
    print(classes)
    np.set_printoptions(threshold=np.inf)
    
    training_set,words = bag_of_words(all_data)
    
    dataset = np.array(training_set)
    labels = np.array(labels)
    
    shuffling_function = np.random.permutation(dataset.shape[0])
    shuffled_dataset, shuffled_labels = np.zeros((dataset.shape)),np.zeros((dataset.shape))
    shuffled_dataset,shuffled_labels = dataset[shuffling_function],labels[shuffling_function]
    
    
    split = int(len(shuffled_dataset)*0.8)
    training_data = shuffled_dataset[:split]
    training_labels = shuffled_labels[:split]
    test_data = shuffled_dataset[split:]
    test_labels = shuffled_labels[split:]
    print(training_data.shape)
    print(training_labels.shape)    
    print(test_data.shape)
    print(test_labels.shape)
    
        
    Train_model(training_data,training_labels,words,classes)
    Test_model(test_data,test_labels,words,classes)

# Method for calculating sigmoid
def sigmoid(z):
    return (1/(1+np.exp(-z)))
    
# Method for calculating relu
def relu(z):
    A = np.array(z,copy=True)
    A[z<0]=0
    assert A.shape == z.shape
    return A
    
# Method for calculating softmax
def softmax(x):
    num = np.exp(x-np.amax(x,axis=0,keepdims=True))    
    return num/np.sum(num,axis=0,keepdims=True)

# Method for calculating forward propagation
def forward_prop(n_x,n_h,n_y,m,X,W1,W2,b1,b2):
    # Forward propagate data ... dimensions should be 100x1547
    Z1 = np.dot(W1,X)+b1
    A1 = relu(Z1)
    Z2 = np.dot(W2,A1)+b2
    A2 = softmax(Z2)
    return Z1,A1,Z2,A2

# Method for calculating relu activation's derivative
def relu_backward(da,dz):
    da1 = np.array(da,copy=True)
    da1[dz<0]=0
    assert da1.shape == dz.shape
    return da1

# Method for calculating linear part of backward propagation
def linear_backward(dz,a,m,w,b):
    dw = (1/m)*np.dot(dz,a.T)
    db = (1/m)*np.sum(dz,axis=1,keepdims=True)
    da = np.dot(w.T,dz)
    assert (dw.shape==w.shape)
    assert (da.shape==a.shape)
    assert (db.shape == b.shape)
    return da,dw,db 

# Method for calculating loss function
def calculate_loss(Y,Yhat,m):
    loss = (-1/m)*np.sum(np.multiply(Y,np.log(Yhat)))
    return loss

# Method for back propagation
def back_prop(Z1,A1,Z2,A2,X,Y,W1,W2,b1,b2,learning_rate,m):
    dZ2 = A2-Y
    da1,dw2,db2 = linear_backward(dZ2,A1,m,W2,b2)
    dZ1 = relu_backward(da1,Z1)
    da0,dw1,db1 = linear_backward(dZ1,X,m,W1,b1)
    W2 = W2 - learning_rate * dw2
    b2 = b2 - learning_rate * db2
    W1 = W1 - learning_rate * dw1
    b1 = b1 - learning_rate * db1
    return W1,b1,W2,b2


# Method for training model
def Test_model(test_data, test_labels,words,classes):
    all_losses = []
    learning_rate = 0.1
    iterations = 50
    np.random.seed(1)
    X = test_data.T
    print(" Shape of X is ", X.shape)
    Y = test_labels.T
    print(" Shape of Y is ", Y.shape)
    # m is total number of training examples
    m = X.shape[1]
    print(" Shape of m is ", m)
    # Number of hidden layer neurons
    n_h = 100
    # Number of training points
    n_x = X.shape[0]
    # Number of output neurons because we have 4 classes
    n_y = 4
    
    weights_file = 'priority_weights.json' 
    with open(weights_file) as data_file: 
        weights = json.load(data_file) 
        W1 = np.asarray(weights['weight1']) 
        W2 = np.asarray(weights['weight2'])
        b1 = np.asarray(weights['bias1']) 
        b2 = np.asarray(weights['bias2'])

    print("################### TEST MODEL STATISTICS ######################")
    for i in range(1):
        # input layer is our encoded sentence
        l0 = X
        # matrix multiplication of input and hidden layer
        l1 = relu(np.dot(W1,l0)+b1)
        # output layer
        l2 = softmax(np.dot(W2,l1)+b2)
        predictions = np.argmax(l2, axis=0)
        labels = np.argmax(Y, axis=0)
        print(classification_report(predictions,labels))



# Method for training model
def Train_model(training_data, training_labels,words,classes):
    all_losses = []
    learning_rate = 0.1
    iterations = 50
    np.random.seed(1)
    X = training_data.T
    print(" Shape of X is ", X.shape)
    Y = training_labels.T
    print(" Shape of Y is ", Y.shape)
    # m is total number of training examples
    m = X.shape[1]
    print(" Shape of m is ", m)
    # Number of hidden layer neurons
    n_h = 100
    # Number of training points
    n_x = X.shape[0]
    # Number of output neurons because we have 4 classes
    n_y = 4
    # Multiplying by 0.01 so that we get smaller weights .. dimensions 100x3787
    W1 = np.random.randn(n_h,n_x)*0.01
    print(" Shape of W1 is ", W1.shape)
    # Dimensions 100x1
    b1 = np.zeros((n_h,1))
    # Dimensions 1547 x 4
    W2 = np.random.randn(n_y,n_h)
    print(" Shape of W2 is ", W2.shape)
    # Forward propagate data ... dimensions should be 100x1547
    b2 = np.zeros((n_y,1))
    print("################### TRAIN MODEL STATISTICS ######################")
    for i in range(0,iterations):
        Z1,A1,Z2,A2 = forward_prop(n_x,n_h,n_y,m,X,W1,W2,b1,b2)
        predictions = np.argmax(A2, axis=0)
        labels = np.argmax(Y, axis=0)
        print(classification_report(predictions,labels))
        Loss = calculate_loss(Y,A2,m)
        W1,b1,W2,b2 = back_prop(Z1,A1,Z2,A2,X,Y,W1,W2,b1,b2,learning_rate,m)
        all_losses.append(Loss)

    # storing weights so that we can reuse them without having to retrain the neural network
    weights = {'weight1': W1.tolist(), 'weight2': W2.tolist(), 
               'bias1':b1.tolist(), 'bias2':b2.tolist(),
               'words': words,
               'classes': classes
              }
    weights_file = "priority_weights.json"

    with open(weights_file, 'w') as outfile:
        json.dump(weights, outfile, indent=4, sort_keys=True)
    print ("saved synapses to:", weights_file)
    

    
if __name__ == '__main__':
    main()
                    



# probability threshold
ERROR_THRESHOLD = 0.1
# load our calculated weight values
weights_file = 'priority_weights.json' 
with open(weights_file) as data_file: 
    weights = json.load(data_file) 
    W1 = np.asarray(weights['weight1']) 
    W2 = np.asarray(weights['weight2'])
    b1 = np.asarray(weights['bias1']) 
    b2 = np.asarray(weights['bias2'])
    all_words = weights['words']
    classes = weights['classes']
    
def clean_sentence(verification_data):
    line = verification_data
    # Remove whitespace from line and lower case iter
    line = line.strip().lower()
    # Removing word with @ sign as we dont need name tags of 
    line = " ".join(filter(lambda x:x[0]!='@', line.split()))
    # Remove punctuations and numbers from the line
    punct = line.maketrans("","",'.*%$^0123456789#!][\?&/)/(+-<>')
    result = line.translate(punct)
    # Tokenize the whole tweet sentence
    tokened_sentence = nltk.word_tokenize(result)
    # We take the tweet sentence from tokened sentence
    sentence = tokened_sentence[0:len(tokened_sentence)]
    return sentence    

def verify(sentence, show_details=False):
    bag=[0]*len(all_words)
    cleaned_sentence = clean_sentence(sentence)
    # This line returns the bag of words as 0 or 1 if words in sentence are found in all_words
    x = encode_sentence(all_words,cleaned_sentence,bag)
    x = np.array(x)
    x = x.reshape(x.shape[0],1)
    
#    print("Shape of X is ", x.shape)
    if show_details:
        print ("sentence:", sentence, "\n bow:", x)
    # input layer is our encoded sentence
    l0 = x
    # matrix multiplication of input and hidden layer
    l1 = relu(np.dot(W1,l0)+b1)
    # output layer
    l2 = softmax(np.dot(W2,l1)+b2)
    
    return l2


