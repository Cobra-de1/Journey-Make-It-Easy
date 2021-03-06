# -*- coding: utf-8 -*-
"""Jouney-Make-It-Easy Recomendation System.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qeWXghL07XDoMgs-dEjiCGoOAziihYyi
"""

from __future__ import print_function

import numpy as np
import pandas as pd
import collections
from mpl_toolkits.mplot3d import Axes3D
#from IPython import display
from matplotlib import pyplot as plt
import sklearn
import sklearn.manifold
import tensorflow.compat.v1 as tf
from random import randrange

import psycopg2

tf.disable_v2_behavior()
tf.logging.set_verbosity(tf.logging.ERROR)

# Add some convenience functions to Pandas DataFrame.
pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.3f}'.format
def mask(df, key, function):
    """Returns a filtered dataframe, by applying function to key"""
    return df[function(df[key])]

def flatten_cols(df):
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df

pd.DataFrame.mask = mask
pd.DataFrame.flatten_cols = flatten_cols

import altair as alt
alt.data_transformers.enable('default', max_rows=None)
alt.renderers.enable('colab')

DOT = 'dot'
COSINE = 'cosine'

users_cols = ['id', 'name']
ratings_cols = ['user_id', 'item_id', 'point']
item_cols = ['id', 'name']

def GetAttrationDB(cursor):
    cursor.execute("SELECT id, username FROM auth_user")
    data = cursor.fetchall()
    users = pd.DataFrame(data=data, index=None, columns=users_cols)

    cursor.execute("SELECT id, name FROM api_attraction")
    data = cursor.fetchall()
    items = pd.DataFrame(data=data, index=None, columns=item_cols)

    cursor.execute("SELECT user_id, item_id, point FROM api_attraction_review")
    data = cursor.fetchall()
    ratings = pd.DataFrame(data=data, index=None, columns=ratings_cols)

    print(users.info())
    print(users)
    print(ratings.info())
    print(ratings)
    print(items.info())
    print(items)

    return users, ratings, items

def GetRestaurantDB(cursor):
    cursor.execute("SELECT id, username FROM auth_user")
    data = cursor.fetchall()
    users = pd.DataFrame(data=data, index=None, columns=users_cols)

    cursor.execute("SELECT id, name FROM api_restaurant")
    data = cursor.fetchall()
    items = pd.DataFrame(data=data, index=None, columns=item_cols)

    cursor.execute("SELECT user_id, item_id, point FROM api_restaurant_review")
    data = cursor.fetchall()
    ratings = pd.DataFrame(data=data, index=None, columns=ratings_cols)

    print(users.info())
    print(users)
    print(ratings.info())
    print(ratings)
    print(items.info())
    print(items)

    return users, ratings, items

def GetStayDB(cursor):
    cursor.execute("SELECT id, username FROM auth_user")
    data = cursor.fetchall()
    users = pd.DataFrame(data=data, index=None, columns=users_cols)

    cursor.execute("SELECT id, name FROM api_stay")
    data = cursor.fetchall()
    items = pd.DataFrame(data=data, index=None, columns=item_cols)

    cursor.execute("SELECT user_id, item_id, point FROM api_stay_review")
    data = cursor.fetchall()
    ratings = pd.DataFrame(data=data, index=None, columns=ratings_cols)

    print(users.info())
    print(users)
    print(ratings.info())
    print(ratings)
    print(items.info())
    print(items)

    return users, ratings, items

# Use for testing
def GetRandom():
    users = pd.DataFrame(data=[[i, 'user' + str(i)] for i in range(10000, 10500)], index=None, columns=users_cols)
    ratings = pd.DataFrame(data=[[randrange(10000, 10500), randrange(1000, 1300), randrange(1, 5)] for i in range(8000)], index=None, columns=ratings_cols)
    items = pd.DataFrame(data=[[i, 'item' + str(i)] for i in range(1000, 1300)], index=None, columns=item_cols)

    return users, ratings, items

def get_from_database(type):
    # Get data from database
    conn = psycopg2.connect(
        database="d9blgfqt5b3tc8",
        user="joukvtgcdmogtd",
        password="f6a0284a9aa31c19e842d1dadcfa1c11420e6114ea6a9653c4b05f518caa74b2",
        host="ec2-3-230-219-251.compute-1.amazonaws.com",
        port="5432",
    )
    cursor = conn.cursor()

    if type == 'Attraction':
        users, ratings, items = GetAttrationDB(cursor)
    elif type == 'Restaurant':
        users, ratings, items = GetRestaurantDB(cursor)
    elif type == 'Stay':
        users, ratings, items = GetStayDB(cursor)
    else:
        users, ratings, items = GetRandom()

    cursor.close()
    conn.close()

    values, keys = pd.factorize(users['id'])
    user_mapping = dict(zip(users['id'], values))
    reverse_user_mapping = dict(zip(values, users['id']))
    users['id'] = values

    values, keys = pd.factorize(items['id'])
    item_mapping = dict(zip(items['id'], values))
    reverse_item_mapping = dict(zip(values, items['id']))
    items['id'] = values

    ratings['user_id'] = ratings['user_id'].apply(lambda x: user_mapping[x])
    ratings['item_id'] = ratings['item_id'].apply(lambda x: item_mapping[x])

    # Add anonymous user
    anonymous = len(user_mapping)
    users = users.append({'id': anonymous, 'name': 'anonymous'}, ignore_index = True)

    return users, ratings, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous

# Utility to split the data into training and test sets.
def split_dataframe(df, holdout_fraction=0.1):
    """Splits a DataFrame into training and test sets.
    Args:
      df: a dataframe.
      holdout_fraction: fraction of dataframe rows to use in the test set.
    Returns:
      train: dataframe for training
      test: dataframe for testing
    """
    test = df.sample(frac=holdout_fraction, replace=False)
    train = df[~df.index.isin(test.index)]
    return train, test

def build_rating_sparse_tensor(ratings_df, a, b):
    indices = ratings_df[['user_id', 'item_id']].values
    values = ratings_df['point'].values
    return tf.SparseTensor(
        indices=indices,
        values=values,
        dense_shape=[a, b])

def sparse_mean_square_error(sparse_ratings, user_embeddings, movie_embeddings):
    """
    Args:
      sparse_ratings: A SparseTensor rating matrix, of dense_shape [N, M]
      user_embeddings: A dense Tensor U of shape [N, k] where k is the embedding
        dimension, such that U_i is the embedding of user i.
      movie_embeddings: A dense Tensor V of shape [M, k] where k is the embedding
        dimension, such that V_j is the embedding of movie j.
    Returns:
      A scalar Tensor representing the MSE between the true ratings and the
        model's predictions.
    """
    predictions = tf.reduce_sum(
        tf.gather(user_embeddings, sparse_ratings.indices[:, 0]) *
        tf.gather(movie_embeddings, sparse_ratings.indices[:, 1]),
        axis=1)
    loss = tf.losses.mean_squared_error(sparse_ratings.values, predictions)
    return loss

class CFModel(object):
    """Simple class that represents a collaborative filtering model"""
    def __init__(self, embedding_vars, ratings, users, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous, loss, metrics=None):
        """Initializes a CFModel.
        Args:
          embedding_vars: A dictionary of tf.Variables.
          loss: A float Tensor. The loss to optimize.
          metrics: optional list of dictionaries of Tensors. The metrics in each
            dictionary will be plotted in a separate figure during training.
        """
        self._embedding_vars = embedding_vars
        self._loss = loss
        self._metrics = metrics
        self._embeddings = {k: None for k in embedding_vars}
        self._session = None
        self._ratings = ratings
        self._users = users
        self._items = items
        self._user_mapping = user_mapping
        self._item_mapping = item_mapping
        self._reverse_user_mapping = reverse_user_mapping
        self._reverse_item_mapping = reverse_item_mapping
        self._anonymous = anonymous

    @property
    def embeddings(self):
        """The embeddings dictionary."""
        return self._embeddings

    def train(self, num_iterations=100, learning_rate=1.0, plot_results=True,
              optimizer=tf.train.GradientDescentOptimizer):
        """Trains the model.
        Args:
          iterations: number of iterations to run.
          learning_rate: optimizer learning rate.
          plot_results: whether to plot the results at the end of training.
          optimizer: the optimizer to use. Default to GradientDescentOptimizer.
        Returns:
          The metrics dictionary evaluated at the last iteration.
        """
        with self._loss.graph.as_default():
            opt = optimizer(learning_rate)
            train_op = opt.minimize(self._loss)
            local_init_op = tf.group(
                tf.variables_initializer(opt.variables()),
                tf.local_variables_initializer())
            if self._session is None:
                self._session = tf.Session()
                with self._session.as_default():
                    self._session.run(tf.global_variables_initializer())
                    self._session.run(tf.tables_initializer())
                    tf.train.start_queue_runners()

        with self._session.as_default():
            local_init_op.run()
            iterations = []
            metrics = self._metrics or ({},)
            metrics_vals = [collections.defaultdict(list) for _ in self._metrics]

            # Train and append results.
            for i in range(num_iterations + 1):
                _, results = self._session.run((train_op, metrics))
                if (i % 10 == 0) or i == num_iterations:
                    print("\r iteration %d: " % i + ", ".join(
                        ["%s=%f" % (k, v) for r in results for k, v in r.items()]),
                          end='')
                    iterations.append(i)
                    for metric_val, result in zip(metrics_vals, results):
                        for k, v in result.items():
                            metric_val[k].append(v)

            for k, v in self._embedding_vars.items():
                self._embeddings[k] = v.eval()

            if plot_results:
                # Plot the metrics.
                num_subplots = len(metrics)+1
                fig = plt.figure()
                fig.set_size_inches(num_subplots*10, 8)
                for i, metric_vals in enumerate(metrics_vals):
                    ax = fig.add_subplot(1, num_subplots, i+1)
                    for k, v in metric_vals.items():
                        ax.plot(iterations, v, label=k)
                    ax.set_xlim([1, num_iterations])
                    ax.legend()
            return results

def build_model(ratings, users, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous, embedding_dim=3, init_stddev=1.):
    """
    Args:
      ratings: a DataFrame of the ratings
      embedding_dim: the dimension of the embedding vectors.
      init_stddev: float, the standard deviation of the random initial embeddings.
    Returns:
      model: a CFModel.
    """
    # Split the ratings DataFrame into train and test.
    train_ratings, test_ratings = split_dataframe(ratings)
    # SparseTensor representation of the train and test datasets.
    A_train = build_rating_sparse_tensor(train_ratings, users.shape[0], items.shape[0])
    A_test = build_rating_sparse_tensor(test_ratings, users.shape[0], items.shape[0])
    # Initialize the embeddings using a normal distribution.
    U = tf.Variable(tf.random_normal(
        [A_train.dense_shape[0], embedding_dim], stddev=init_stddev))
    V = tf.Variable(tf.random_normal(
        [A_train.dense_shape[1], embedding_dim], stddev=init_stddev))
    train_loss = sparse_mean_square_error(A_train, U, V)
    test_loss = sparse_mean_square_error(A_test, U, V)
    metrics = {
        'train_error': train_loss,
        'test_error': test_loss
    }
    embeddings = {
        "user_id": U,
        "item_id": V
    }
    return CFModel(embeddings, ratings, users, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous, train_loss, [metrics])

def compute_scores(query_embedding, item_embeddings, measure=DOT):
    """Computes the scores of the candidates given a query.
    Args:
      query_embedding: a vector of shape [k], representing the query embedding.
      item_embeddings: a matrix of shape [N, k], such that row i is the embedding
        of item i.
      measure: a string specifying the similarity measure to be used. Can be
        either DOT or COSINE.
    Returns:
      scores: a vector of shape [N], such that scores[i] is the score of item i.
    """
    u = query_embedding
    V = item_embeddings
    if measure == COSINE:
        V = V / np.linalg.norm(V, axis=1, keepdims=True)
        u = u / np.linalg.norm(u)
    scores = u.dot(V.T)
    return scores

def user_recommendations(model, id, measure=DOT, exclude_rated=False, k=6):
    if id in model._user_mapping:
        id = model._user_mapping[id]
    else:
        id = model._anonymous
    scores = compute_scores(
        model.embeddings["user_id"][id], model.embeddings["item_id"], measure)
    score_key = measure + ' score'
    df = pd.DataFrame({
        score_key: list(scores),
        'item_id': [model._reverse_item_mapping[i] for i in model._items['id']],
        'name': model._items['name'],
    })
    if exclude_rated:
        # remove items that are already rated
        rated_items = model._ratings[model._ratings.user_id == id]["item_id"].values
        df = df[df.item_id.apply(lambda item_id: item_id not in rated_items)]
        df = df.sort_values([score_key], ascending=False)
    return df['item_id'][:k].tolist(), df[score_key][:k].tolist()

'''
def item_neighbors(model, name_substring, measure=DOT, k=6):
  # Search for item ids that match the given substring.
  ids =  model._items[model._items['name'].str.contains(name_substring)].index.values
  titles = model._items.iloc[ids]['name'].values
  if len(titles) == 0:
    raise ValueError("Found no items with title %s" % name_substring)
  print("Nearest neighbors of : %s." % titles[0])
  if len(titles) > 1:
    print("[Found more than one matching item. Other candidates: {}]".format(
        ", ".join(titles[1:])))
  item_id = ids[0]
  scores = compute_scores(
      model.embeddings["item_id"][item_id], model.embeddings["item_id"],
      measure)
  score_key = measure + ' score'
  df = pd.DataFrame({
      score_key: list(scores),
      'item_id': [model._reverse_item_mapping[i] for i in model._items['id']],
      'name': model._items['name']
  })
  display.display(df.sort_values([score_key], ascending=False).head(k))
'''

def create_model(type='Attraction'):
    users, ratings, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous = get_from_database(type)

    model = build_model(ratings, users, items, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping, anonymous, embedding_dim=30, init_stddev=0.5)
    model.train(num_iterations=1000, learning_rate=10.)

    return model
