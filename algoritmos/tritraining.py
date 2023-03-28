# Autor: David Martínez Acha
# Fecha: 26/03/2023 23:00
# Descripción: Algoritmo Tri-Training
# Version: 0.1

import numpy as np
from math import floor, ceil
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from algoritmos.utilidades.common import obtain_train_unlabelled, calculate_log_statistics
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split


class TriTraining:

    def __init__(self, clfs):
        """
        Algoritmo Tri-Training.

        :param clfs: LISTA de clasificadores a usar.
        """
        self.clfs = clfs
        self.others = {0: [1, 2],
                       1: [0, 2],
                       2: [0, 1]}

    def fit(self, x, y, x_test=None, y_test=None, features=None):
        """
        Proceso de entrenamiento y obtención de la evolución.

        Algoritmo de Zhi-Hua Zhou y Ming Li.


        :param x: Instancias.
        :param y: Etiquetas de las instancias.
        :param x_test: Conjunto de test.
        :param y_test: Etiquetas de test.
        :return: iteración.
        """

        x_train, y_train, x_u = obtain_train_unlabelled(x, y)

        e_prime = [0.5] * len(self.clfs)
        l_prime = [0] * len(self.clfs)
        for n in self.clfs:
            s_i = np.random.choice(len(x_train), len(x_train))
            n.fit(x_train[s_i], y_train[s_i])

        iteration = 0

        change = True

        while change:
            change = False
            # Li (instancias)
            l_i_x = [[] for _ in range(len(self.clfs))]
            # Li (etiquetas)
            l_i_y = [[] for _ in range(len(self.clfs))]
            e_i = [0] * len(self.clfs)
            updates = [False] * len(self.clfs)

            for i in range(len(self.clfs)):
                updates[i] = False
                e_i[i] = self._measure_error(self.others[i], x_train, y_train)

                if e_i[i] < e_prime[i]:
                    for x in x_u:
                        h_j = self.clfs[self.others[i][0]].predict([x])
                        h_k = self.clfs[self.others[i][1]].predict([x])
                        if h_j == h_k:
                            l_i_x[i].append(x)
                            l_i_y[i].append(h_j[0])

                    if l_prime[i] == 0:
                        l_prime[i] = floor(e_i[i] / (e_prime[i] - e_i[i]) + 1)

                    if l_prime[i] < len(l_i_x[i]):
                        if e_i[i] * len(l_i_x[i]) < e_prime[i] * l_prime[i]:
                            updates[i] = True
                            change = True
                        elif l_prime[i] > (e_i[i] / (e_prime[i] - e_i[i])):
                            to_keep = np.random.choice(len(l_i_x[i]),
                                                       ceil(e_prime[i] * l_prime[i] / e_i[i] - 1))
                            l_i_x[i] = [l_i_x[i][keep] for keep in to_keep]
                            l_i_y[i] = [l_i_y[i][keep] for keep in to_keep]
                            updates[i] = True
                            change = True

            for i, n in enumerate(self.clfs):
                if updates[i]:
                    e_prime[i] = e_i[i]
                    l_prime[i] = len(l_i_x[i])

                    mew_x_train = np.concatenate((x_train, l_i_x[i]), axis=0)
                    mew_y_train = np.concatenate((y_train, l_i_y[i]))

                    n.fit(mew_x_train, mew_y_train)

            iteration += 1

        return iteration - 1

    def _measure_error(self, others_clfs, x_train, y_train):
        """
        Calcula el error según lo impuesto en el artículo:
        El error de clasificación se aproxima dividiendo el
        número de instancias en las que el resto (dos) clasificador
        se equivocan entre el número de instancias en el que
        predicen (el resto) la misma etiqueta

        :param others_clfs: lista con el resto de clasificadores.
        :param x_train: instancias (L).
        :param y_train: etiquetas de las instancias.
        :return: error de clasificación.
        """
        h_j = self.clfs[others_clfs[0]].predict(x_train)
        h_k = self.clfs[others_clfs[1]].predict(x_train)

        h_j_correct = h_j == y_train
        h_k_correct = h_k == y_train

        or_operation = np.asarray(h_j_correct | h_k_correct)

        return np.count_nonzero(np.invert(or_operation)) / np.count_nonzero(h_j == h_k)

    def predict(self, instances):
        """
        Predice las etiquetas de una serie de instancias

        :param instances: Instancias a predecir.
        :return: Predicciones de las instancias
        """
        return np.array([np.bincount([n.predict([x])[0] for n in self.clfs]).argmax() for x in instances])

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de exactitud del clasificador
        respecto a unos datos de prueba

        :param x_test: Instancias.
        :param y_test: Etiquetas de las instancias.
        :return: Exactitud
        """

        return accuracy_score(y_test, self.predict(x_test))


if __name__ == '__main__':
    tt = TriTraining([GaussianNB(), DecisionTreeClassifier(), KNeighborsClassifier()])

    data = load_breast_cancer()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(data.data, data.target, False, p_unlabelled=0.8, p_test=0.02)

    it = tt.fit(x, y)

    print(accuracy_score(y_test, tt.predict(x_test)))
