import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import math
import matplotlib.pyplot as plt #plotting
from mpl_toolkits.mplot3d import Axes3D #3d plots
from sklearn.neighbors import NearestNeighbors


def get_parameters(Signal):
    datDelayInformation = []
    for i in range(1, 21):
        try:
           datDelayInformation = np.append(datDelayInformation, [mutualInformation(Signal, i, 10)])
        except:
            pass
    plt.plot(range(1, 21), datDelayInformation)
    plt.xlabel('delay')
    plt.ylabel('mutual information')
    # Get the indices of minimum element
    t = int(np.where( datDelayInformation == np.amin(datDelayInformation))[0][0])
    nFNN = []
    for i in range(1, 7):
        nFNN.append(false_nearest_neighours(Signal, t, i) / len(Signal))
    plt.plot(range(1, 7), nFNN)
    plt.xlabel('embedding dimension')
    plt.ylabel('Fraction of fNN')
    d = int(np.where(nFNN== np.amin(nFNN))[0][0])

    return t, d

def mutualInformation(data, delay, nBins):
    #"This function calculates the mutual information given the delay"
    I = 0
    xmax = max(data)
    xmin = min(data)
    delayData = data[delay:len(data)]
    shortData = data[0:len(data)-delay]
    sizeBin = abs(xmax - xmin) / nBins    #the use of dictionaries makes the process a bit faster
    probInBin = {}
    conditionBin = {}
    conditionDelayBin = {}
    for h in range(0, nBins):
        if h not in probInBin:
            conditionBin.update({h : (shortData >= (xmin + h*sizeBin)) & (shortData < (xmin + (h+1)*sizeBin))})
            probInBin.update({h : len(shortData[conditionBin[h]]) / len(shortData)})
        for k in range(0, nBins):
            if k not in probInBin:
                conditionBin.update({k : (shortData >= (xmin + k*sizeBin)) & (shortData < (xmin + (k+1)*sizeBin))})
                probInBin.update({k : len(shortData[conditionBin[k]]) / len(shortData)})
            if k not in conditionDelayBin:
                conditionDelayBin.update({k : (delayData >= (xmin + k*sizeBin)) & (delayData < (xmin + (k+1)*sizeBin))})
            Phk = len(shortData[conditionBin[h] & conditionDelayBin[k]]) / len(shortData)
            if Phk != 0 and probInBin[h] != 0 and probInBin[k] != 0:
                I -= Phk * math.log( Phk / (probInBin[h] * probInBin[k]))
    return I

def false_nearest_neighours(data,delay,embeddingDimension):
    "Calculates the number of false nearest neighbours of embedding dimension"
    embeddedData = takensEmbedding(data,delay,embeddingDimension);
    #the first nearest neighbour is the data point itself, so we choose the second one
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='auto').fit(embeddedData.transpose())
    distances, indices = nbrs.kneighbors(embeddedData.transpose())
    #two data points are nearest neighbours if their distance is smaller than the standard deviation
    epsilon = np.std(distances.flatten())
    nFalseNN = 0
    for i in range(0, len(data)-delay*(embeddingDimension+1)):
        if (0 < distances[i,1]) and (distances[i,1] < epsilon) and ( (abs(data[i+embeddingDimension*delay] - data[indices[i,1]+embeddingDimension*delay]) / distances[i,1]) > 10):
            nFalseNN += 1;
    return nFalseNN



def takensEmbedding (data, delay, dimension):
    "This function returns the Takens embedding of data with delay into dimension, delay*dimension must be < len(data)"
    if delay*dimension > len(data):
        raise NameError('Delay times dimension exceed length of data!')
    embeddedData = np.array([data[0:len(data)-delay*dimension]])
    for i in range(1, dimension):
        embeddedData = np.append(embeddedData, [data[i*delay:len(data) - delay*(dimension - i)]], axis=0)
    return embeddedData
