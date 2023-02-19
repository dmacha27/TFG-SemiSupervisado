#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 19/02/2023 19:20
# Descripción: Algoritmo Democratic Co-Learning
# Version: 0.1

from typing import List

import numpy as np
import scipy

from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import accuracy_score, precision_score
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from algoritmos.utilidades import DatasetLoader
from algoritmos.utilidades.common import obtain_train_unlabelled
from algoritmos.utilidades.datasplitter import data_split


class DemocraticCoLearning:

    def __init__(self, clfs):
        """
        Algoritmo Democratic Co-Learning.

        :param clfs: LISTA de clasificadores a usar.
        """
        self.labels = 0
        self.ws = []
        self.clfs = clfs
        self.confidence = scipy.stats.norm.ppf(1.95 / 2.0)

    def fit(self, x, y, x_test, y_test):
        """
        Proceso de entrenamiento y obtención de la evolución.

        Algoritmo de Yan Zhou y Sally Goldman.


        :param x: Muestras (con el nombre de las características).
        :param y: Objetivos de las muestras.
        :param x_test: Conjunto de test.
        :param y_test: Etiquetas de test.
        :return: iteración.
        """

        x_train, y_train, x_u = obtain_train_unlabelled(x, y)
        self.labels = max(y_train) + 1

        errors = []
        ls = []
        ls_y = []
        for _ in self.clfs:
            ls.append(x_train)
            ls_y.append(y_train)
            errors.append(0)

        iteration = 0
        change = True
        while change:
            change = False

            for i, n in enumerate(self.clfs):
                n.fit(ls[i], ls_y[i])

            xs_cks = []
            votes = []
            for x in x_u:
                c = np.array([n.predict([x]) for n in self.clfs])

                # Etiqueta mayoritaria
                ck = np.bincount(c.ravel()).argmax()
                xs_cks.append(ck)

                # Almacenar qué clasificador ha votado la mayoritaria
                votes_ck = np.where(c.ravel() == ck)
                votes.append(votes_ck[0])

            ws = []
            for n in self.clfs:
                _, _, mean = self._confidence_interval(n, x_train, y_train)
                ws.append(mean)

            ls_prime = []
            ls_prime_y = []
            for _ in self.clfs:
                ls_prime.append([])
                ls_prime_y.append([])

            for index, x in enumerate(x_u):
                left = [wi for n_i, wi in enumerate(ws) if n_i in votes[index]]
                left = sum(left) if left else 0

                right = [wi for n_i, wi in enumerate(ws) if n_i not in votes[index]]
                right = max(right) if right else 0

                if left > right:
                    for i in range(len(self.clfs)):
                        if i not in votes[index]:
                            ls_prime[i].append(x)
                            ls_prime_y[i].append(xs_cks[index])

            for index, n in enumerate(self.clfs):
                len_li = len(ls[index])
                len_li_prime = len(ls_prime[index])

                l, h, mean = self._confidence_interval(n, ls[index], ls_y[index])

                qi = len_li * (1 - 2 * (errors[index] / len_li)) ** 2

                ei_prime = (1 - ((l * len_li) / len_li) * len_li_prime)

                qi_prime = (len_li + len_li_prime) * (
                        1 - ((2 * (errors[index] + ei_prime)) / (len_li + len_li_prime))) ** 2

                if qi_prime > qi:
                    change = True
                    ls[index] = np.concatenate((ls[index], ls_prime[index]), axis=0)
                    ls_y[index] = np.concatenate((ls_y[index], ls_prime_y[index]))
                    errors[index] += ei_prime

            self.ws = ws

            iteration += 1

        return iteration

    def _confidence_interval(self, n, x_train, y_train):
        y_pred = n.predict(x_train)
        accuracy = accuracy_score(y_train, y_pred)
        inf = accuracy - self.confidence * np.sqrt(accuracy * (1 - accuracy) / len(y_train))  # l
        sup = accuracy + self.confidence * np.sqrt(accuracy * (1 - accuracy) / len(y_train))  # h
        mean = (inf + sup) / 2

        return inf, sup, mean


if __name__ == '__main__':
    dl = DatasetLoader('utilidades/datasets/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = DemocraticCoLearning(clfs=[GaussianNB(), SVC(), DecisionTreeClassifier()])

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.9, p_test=0.5)

    st.fit(x, y, x_test, y_test)
