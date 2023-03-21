import copy
from copy import deepcopy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sslearn.wrapper
from numpy import mean, std
from sklearn.model_selection import KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_digits, load_wine

from algoritmos import CoTraining, DemocraticCoLearning, SelfTraining
from algoritmos.utilidades.datasplitter import data_split


def cross_validation(own_clf, clf1_params, other_clf, clf2_params, x, y, folds, own_features, comparison_name,
                     ssl_features=None):
    """
    Realiza el proceso de validación cruzada manualmente para comparar modelo de implementación propia contra uno
    de sslearn

    :param own_clf: Primer modelo de entrenamiento (implementación propia).
    :param clf1_params: Parámetros para el primer modelo.
    :param other_clf: Segundo modelo de entrenamiento (sslearn).
    :param clf2_params: Parámetros para el segundo modelo.
    :param x: Instancias.
    :param y: Etiquetas de las instancias.
    :param folds: Número de folds.
    :param own_features: Etiquetas de las características (implementación propia).
    :param comparison_name: Nombre de la comparación.
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

    # En x e y solo hay datos etiquetados
    x = np.concatenate((x_labelled, x_test), axis=0)
    y = np.concatenate((y, y_test))

    kf = KFold(n_splits=folds)

    stats_clf1 = pd.DataFrame(columns=['accuracy'])
    stats_clf2 = pd.DataFrame(columns=['accuracy'])
    accuracy_clf1 = []
    accuracy_clf2 = []
    for train_index, test_index in kf.split(x):
        x_test = x[test_index]
        y_test = y[test_index]

        x_train = x[train_index]
        y_train = y[train_index]
        x_train = np.concatenate((x_train, x_unlabelled), axis=0)
        y_train = np.concatenate((y_train, [-1] * len(x_unlabelled)))

        clf1 = own_clf(**copy.deepcopy(clf1_params))

        clf1.fit(x_train, y_train, x_test, y_test, own_features)  # Implementación

        clf2 = other_clf(**copy.deepcopy(clf2_params))
        if ssl_features:
            clf2.fit(x_train, y_train, features=ssl_features)  # sslearn
        else:
            clf2.fit(x_train, y_train)

        acc = clf1.get_accuracy_score(x_test, y_test)
        accuracy_clf1.append(acc)
        stats_clf1.loc[len(stats_clf1)] = acc

        acc = clf2.score(x_test, y_test)
        accuracy_clf2.append(acc)
        stats_clf2.loc[len(stats_clf2)] = acc

    stats_clf1.to_csv(path_or_buf=f'./results/{comparison_name}-own', index=False)
    stats_clf2.to_csv(path_or_buf=f'./results/{comparison_name}-sslearn', index=False)
    return mean(accuracy_clf1), std(accuracy_clf1), mean(accuracy_clf2), std(accuracy_clf2)


def selftraining_comparison(data, comparison_name):
    """
    Este método compara la implementación de SelfTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """
    return cross_validation(SelfTraining,
                            {'clf': GaussianNB(), 'th': 0.75, 'n_iter': 10},
                            sslearn.wrapper.SelfTraining,
                            {'base_estimator': GaussianNB(), 'threshold': 0.75, 'max_iter': 10},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name)


def cotraining_comparison(data, comparison_name):
    """
    Este método compara la implementación de CoTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """
    n_features = len(data.feature_names)

    return cross_validation(CoTraining,
                            {'clf1': DecisionTreeClassifier(), 'clf2': GaussianNB(),
                             'p': 1, 'n': 3, 'u': 75, 'n_iter': 30},
                            sslearn.wrapper.CoTraining,
                            {'second_base_estimator': GaussianNB()},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name,
                            [list(range(n_features // 2 + 1)),
                             list(range(n_features // 2 + 1,
                                        n_features))])


def democraticolearning_comparison(data, comparison_name):
    """
    Este método compara la implementación de Democratic Co-Learning realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    clfs = [SVC(kernel='rbf',
                probability=True,
                C=1.0,
                gamma='scale',
                random_state=0
                ), GaussianNB(), DecisionTreeClassifier()]

    return cross_validation(DemocraticCoLearning,
                            {'clfs': deepcopy(clfs)},
                            sslearn.wrapper.DemocraticCoLearning,
                            {'base_estimator': deepcopy(clfs)},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name)


def draw_comparison(comparison_name):
    stats_clf1 = pd.read_csv(f'./results/{comparison_name}-own')
    stats_clf2 = pd.read_csv(f'./results/{comparison_name}-sslearn')

    plt.plot(stats_clf1.index, stats_clf1['accuracy'], label="Implementación")
    plt.plot(stats_clf2.index, stats_clf2['accuracy'], label="sslearn")
    plt.xlabel('Fold')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()


if __name__ == '__main__':
    data = load_breast_cancer()

    # draw_comparison("DemocraticCoLearning")

    print("---Self-Training---")
    own, std_own, ssl, std_ssl = selftraining_comparison(data, "SelfTraining-Breast")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Co-Training---")
    own, std_own, ssl, std_ssl = cotraining_comparison(data, "CoTraining-Breast")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Democratic Co-Learning---")
    own, std_own, ssl, std_ssl = democraticolearning_comparison(data, "DemocraticCoLearning-Breast")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")
