from copy import deepcopy
from math import ceil

import numpy as np
import pandas as pd
import sslearn.wrapper
from numpy import mean, std
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_digits, load_wine

from algoritmos import CoTraining, DemocraticCoLearning, SelfTraining
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split


def cross_validation(clf1, clf2, x, y, folds, own_features, ssl_features=None):
    """
    Realiza el proceso de validación cruzada manualmente para comparar modelo de implementación propia contra uno
    de sslearn

    :param clf1: Primer modelo de entrenamiento (implementación propia)
    :param clf2: Segundo modelo de entrenamiento (sslearn)
    :param x: Instancias.
    :param y: Etiquetas de las instancias.
    :param own_features: Etiquetas de las características (implementación propia)
    :param ssl_features: Índices de las características (sslearn)
    :return: Exactitud de ambos modelos (mismo orden que de entrada) junto con ambas desviaciones estándar
    """
    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled=False, p_unlabelled=0.8, p_test=0.2)

    first_i_u = np.where(y == -1)[0][0]
    x_labelled = x[:first_i_u]
    x_unlabelled = x[first_i_u:]

    y = y[:first_i_u]

    x = np.concatenate((x_labelled, x_test), axis=0)
    y = np.concatenate((y, y_test))

    fold_step = ceil(len(x) / folds)

    folds_x = []
    folds_y = []
    clf1_clones = []
    clf2_clones = []
    for i in range(folds):
        folds_x.append(x[i * fold_step: min(len(y), (i + 1) * fold_step) + 1])
        folds_y.append(y[i * fold_step: min(len(y), (i + 1) * fold_step) + 1])
        clf1_clones.append(deepcopy(clf1))
        clf2_clones.append(deepcopy(clf2))

    accuracy_clf1 = []
    accuracy_clf2 = []
    for i in range(folds):
        x_test = folds_x[i]
        y_test = folds_y[i]

        left_folds_x = np.concatenate(folds_x[0:i], axis=0) if i != 0 else [[]]
        left_folds_y = np.concatenate(folds_y[0:i]) if i != 0 else []

        right_folds_x = np.concatenate(folds_x[i + 1:len(folds_x)], axis=0) if i != folds - 1 else [[]]
        right_folds_y = np.concatenate(folds_y[i + 1:len(folds_y)]) if i != folds - 1 else []

        if i == 0:
            x = right_folds_x
            y = right_folds_y
        elif i == folds - 1:
            x = left_folds_x
            y = left_folds_y
        else:
            x = np.concatenate((left_folds_x, right_folds_x), axis=0)
            y = np.concatenate((left_folds_y, right_folds_y))

        x = np.concatenate((x, x_unlabelled), axis=0)
        y = np.concatenate((y, [-1] * len(x_unlabelled)))

        clf1_clones[i].fit(x, y, x_test, y_test, own_features)  # Implementación
        if ssl_features:
            clf2_clones[i].fit(x, y, features=ssl_features)  # sslearn
        else:
            clf2_clones[i].fit(x, y)

        accuracy_clf1.append(clf1_clones[i].get_accuracy_score(x_test, y_test))
        accuracy_clf2.append(clf2_clones[i].score(x_test, y_test))

    return mean(accuracy_clf1), std(accuracy_clf1), mean(accuracy_clf2), std(accuracy_clf2)


def selftraining_comparison(data):
    """
    Este método compara la implementación de SelfTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = pd.Series(data.target)

    return cross_validation(SelfTraining(GaussianNB(), th=0.75, n_iter=10),
                            sslearn.wrapper.SelfTraining(GaussianNB(), threshold=0.75, max_iter=10),
                            df[data.feature_names],
                            df['target'],
                            10,
                            data.feature_names)


def cotraining_comparison(data):
    """
    Este método compara la implementación de CoTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = pd.Series(data.target)

    return cross_validation(CoTraining(clf1=DecisionTreeClassifier(),
                                       clf2=GaussianNB(), p=1, n=3, u=75, n_iter=30),
                            sslearn.wrapper.CoTraining(second_base_estimator=GaussianNB()),
                            df[data.feature_names],
                            df['target'],
                            10,
                            data.feature_names,
                            [[0, 1, 2, 3, 4], [5, 6, 7, 8]])


def democraticolearning_comparison(data):
    """
    Este método compara la implementación de Democratic Co-Learning realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = pd.Series(data.target)

    clfs = [SVC(kernel='rbf',
                probability=True,
                C=1.0,
                gamma='scale',
                random_state=0
                ), GaussianNB(), DecisionTreeClassifier()]

    dcl = DemocraticCoLearning(clfs=deepcopy(clfs))

    dclssl = sslearn.wrapper.DemocraticCoLearning(base_estimator=deepcopy(clfs))

    return cross_validation(dcl,
                            dclssl,
                            df[data.feature_names],
                            df['target'],
                            10,
                            data.feature_names, )


if __name__ == '__main__':
    data = load_breast_cancer()

    print("---Self-Training---")
    own, std_own, ssl, std_ssl = selftraining_comparison(data)

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Co-Training---")
    own, std_own, ssl, std_ssl = cotraining_comparison(data)

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Democratic Co-Learning---")

    own, std_own, ssl, std_ssl = democraticolearning_comparison(data)

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")
