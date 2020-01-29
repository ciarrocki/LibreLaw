#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 20:16:45 2020

@author: dan
"""


from sklearn.decomposition import IncrementalPCA
from sklearn.manifold import TSNE
import umap
import numpy as np
import matplotlib.pyplot as plt
import random





def reduce_dimensions_UMAP(model, dimensions=2, wordlist=[]):
        
    vectors = [] # Positions in vector space
    labels = [] # Keep track of words to label our data when done transforming

    if len(wordlist) > 0:
        for word in wordlist:
            vectors.append(model.wv[word])
            labels.append(word)
    else:
        for word in model.wv.vocab:
            vectors.append(model.wv[word])
            labels.append(word)

    # Convert both lists into numpy vectors for reduction
    vectors = np.asarray(vectors)
    labels = np.asarray(labels)

    # Reduce using UMAP
    reducer = umap.UMAP(random_state=42, n_components=dimensions)
    reducer.fit(vectors)
    vectors_umap = reducer.transform(vectors)

    # Verify that the result of calling transform is
    # idenitical to accessing the embedding_ attribute
    assert(np.all(vectors_umap == reducer.embedding_))

    x_vals = [v[0] for v in vectors_umap]
    y_vals = [v[1] for v in vectors_umap]

    if dimensions == 3: 
        z_vals = [v[2] for v in vectors_umap]
        return x_vals, y_vals, z_vals, labels

    return x_vals, y_vals, labels





def reduce_dimensions_IPCA(model, dimensions=2, wordlist=[]):
    
    vectors = [] # Positions in vector space
    labels = [] # Keep track of words to label our data when done transforming
    
    if len(wordlist) > 0:
        for word in wordlist:
            vectors.append(model.wv[word])
            labels.append(word)
    else:
        for word in model.wv.vocab:
            vectors.append(model.wv[word])
            labels.append(word)
        
    # Convert both lists into numpy vectors for reduction
    vectors = np.asarray(vectors)
    labels = np.asarray(labels)

    # Reduce using IPCA
    ipca = IncrementalPCA(n_components=dimensions, batch_size=20)
    vectors_ipca = ipca.fit_transform(vectors)

    x_vals = [v[0] for v in vectors_ipca]
    y_vals = [v[1] for v in vectors_ipca]

    if dimensions == 3: 
        z_vals = [v[2] for v in vectors_ipca]
        return x_vals, y_vals, z_vals, labels

    return x_vals, y_vals, labels






def reduce_dimensions_TSNE(model, dimensions=2, wordlist=[]):

    vectors = [] # Positions in vector space
    labels = [] # Keep track of words to label our data when done transforming
    
    if len(wordlist) > 0:
        for word in wordlist:
            vectors.append(model.wv[word])
            labels.append(word)
    else:
        for word in model.wv.vocab:
            vectors.append(model.wv[word])
            labels.append(word)
        
    # Convert both lists into numpy vectors for reduction
    vectors = np.asarray(vectors)
    labels = np.asarray(labels)

    # Reduce using t-SNE
    tsne = TSNE(n_components=dimensions, random_state=0)
    vectors_tsne = tsne.fit_transform(vectors)

    x_vals = [v[0] for v in vectors_tsne]
    y_vals = [v[1] for v in vectors_tsne]

    if dimensions == 3: 
        z_vals = [v[2] for v in vectors_tsne]
        return x_vals, y_vals, z_vals, labels

    return x_vals, y_vals, labels





def plot_with_matplotlib(x_vals, y_vals, labels):
    
    random.seed(0)
    
    plt.figure(figsize=(12, 12))
    plt.scatter(x_vals, y_vals)
    
    # Label 25 random data points
    indices = list(range(len(labels)))
    #selected_indices = random.sample(indices, 25)
    selected_indices = indices
    for i in selected_indices:
        plt.annotate(labels[i], (x_vals[i], y_vals[i]))



