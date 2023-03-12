import numpy as np
import pandas as pd
from numpy import mean, std
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_digits, load_wine

from algoritmos import CoTraining, DemocraticCoLearning, SelfTraining
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split


def executor(algorithm, data):
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = pd.Series(data.target)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(df[data.feature_names], df['target'], is_unlabelled=False, p_unlabelled=0.8, p_test=0.2)

    _, stats, _ = algorithm.fit(x, y, x_test, y_test, data.feature_names)

    print(stats)


if __name__ == '__main__':
    data = load_digits()

    algorithm = SelfTraining(DecisionTreeClassifier(),
                             n=10,
                             n_iter=10)

    executor(algorithm, data)
