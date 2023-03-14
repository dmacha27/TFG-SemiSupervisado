#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 19/02/2023 19:20
# Descripción: Algoritmo Democratic Co-Learning
# Version: 1.0
import math
from typing import List

import numpy as np
import pandas as pd
import scipy

from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from algoritmos.utilidades.datasetloader import DatasetLoader
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

    def fit(self, x, y, x_test, y_test, features):
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

        log = pd.DataFrame(x_train, columns=features)
        log['iters'] = [[0]] * len(log)
        log['targets'] = [[lab] for lab in y_train]
        log['clfs'] = [['inicio']] * len(log)

        rest = pd.DataFrame(x_u, columns=features)
        rest['iters'] = [[-1] * len(self.clfs) for _ in range(len(rest))]
        rest['targets'] = [[-1] * len(self.clfs) for _ in range(len(rest))]
        rest['clfs'] = [[f"CLF{i + 1}({n.__class__.__name__})" for i, n in enumerate(self.clfs)]] * len(rest)

        log = pd.concat([log, rest], ignore_index=True)

        errors = []
        ls = []
        ls_new_ids = []
        ls_y = []
        for _ in self.clfs:
            ls.append(x_train)
            ls_new_ids.append(dict())
            ls_y.append(y_train)
            errors.append(0)

        iteration = 0
        stat_columns = ['Accuracy', 'Precision', 'Error', 'F1_score', 'Recall']
        stats = pd.DataFrame(columns=stat_columns)

        specific_stats = {f"CLF{i + 1}({n.__class__.__name__})": pd.DataFrame(columns=stat_columns) for i, n in
                          enumerate(self.clfs)}

        change = True
        while change:
            change = False

            for i, n in enumerate(self.clfs):
                n.fit(ls[i], ls_y[i])

            for i, n in enumerate(self.clfs):
                clf_stat = specific_stats[f"CLF{i + 1}({n.__class__.__name__})"]
                clf_stat.loc[len(clf_stat)] = [accuracy_score(y_test, n.predict(x_test)),
                                               precision_score(y_test, n.predict(x_test), average='weighted'),
                                               1 - accuracy_score(y_test, n.predict(x_test)),
                                               f1_score(y_test, n.predict(x_test), average='weighted'),
                                               recall_score(y_test, n.predict(x_test), average='weighted')]

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
            ls_prime_ids = []
            ls_prime_y = []
            for _ in self.clfs:
                ls_prime.append([])
                ls_prime_ids.append([])
                ls_prime_y.append([])

            for index, x in enumerate(x_u):
                left = [wi for n_i, wi in enumerate(ws) if n_i in votes[index]]
                left = sum(left) if left else 0  # REVISAR

                right = [wi for n_i, wi in enumerate(ws) if n_i not in votes[index]]
                right = max(right) if right else 0  # REVISAR

                if left > right:
                    for i in range(len(self.clfs)):
                        if i not in votes[index]:
                            ls_prime[i].append(x)
                            ls_prime_ids[i].append(index)
                            ls_prime_y[i].append(xs_cks[index])

            average_l = [self._confidence_interval(n, ls[index], ls_y[index])[0] for index, n in enumerate(self.clfs)]
            average_l = sum(average_l) / len(self.clfs) if average_l else 0

            for index, n in enumerate(self.clfs):
                len_li = len(ls[index])
                len_li_prime = len(ls_prime[index])

                qi = len_li * (1 - 2 * (errors[index] / len_li)) ** 2

                ei_prime = (1 - average_l) * len_li_prime

                qi_prime = (len_li + len_li_prime) * (
                        1 - ((2 * (errors[index] + ei_prime)) / (len_li + len_li_prime))) ** 2

                if qi_prime > qi:
                    for x_id, x, y in zip(ls_prime_ids[index], ls_prime[index], ls_prime_y[index]):
                        if x_id in ls_new_ids[index]:
                            # Comprobar si es igual y si lo es, no contar como cambio
                            ls_y[index][ls_new_ids[index][x_id]] = y
                            log.loc[len(x_train) + x_id, 'iters'][index] = iteration + 1
                            log.loc[len(x_train) + x_id, 'targets'][index] = y
                        else:  # Nueva etiqueta
                            change = True
                            ls_new_ids[index][x_id] = len(ls[index])
                            log.loc[len(x_train) + x_id, 'iters'][index] = iteration + 1
                            log.loc[len(x_train) + x_id, 'targets'][index] = y
                            ls[index] = np.append(ls[index], [x], axis=0)
                            ls_y[index] = np.append(ls_y[index], [y])

                    errors[index] += ei_prime

            self.ws = ws

            stats.loc[len(stats)] = [self.get_accuracy_score(x_test, y_test),
                                     self.get_precision_score(x_test, y_test),
                                     1 - self.get_accuracy_score(x_test, y_test),
                                     self.get_f1_score(x_test, y_test),
                                     self.get_recall_score(x_test, y_test)]

            iteration += 1

        return log, stats, specific_stats, iteration - 1

    def predict(self, instances):
        """
        Predice las etiquetas de una serie de instancias

        :param instances: Datos a predecir.
        :return: Predicciones
        """

        if not self.ws:
            raise ValueError("Es necesario entrenamiento")

        confidences_per_x = []

        for x in instances:
            group: List[List[int]] = [[] for _ in range(self.labels)]
            for index, n in enumerate(self.clfs):
                if self.ws[index] > 0.5:
                    label = n.predict([x])[0]
                    group[label].append(index)

            confidences = []
            for j in range(self.labels):
                op1 = (len(group[j]) + 0.5) / (len(group[j]) + 1)

                if group[j]:
                    num = [self.ws[index] for index in group[j]]
                    num = sum(num) if num else 0
                    op2 = num / len(group[j])
                else:
                    op2 = 1  # REVISAR

                confidences.append(op1 * op2)

            confidences_per_x.append(confidences)

        return np.array([np.argmax(c) for c in confidences_per_x])

    def _confidence_interval(self, n, x, y):
        """
        Calcula el intervalo de confianza del clasificador.

        Implementación por César Ignacio García Osorio

        :param n: Clasificador.
        :param x: instancias con las que calcular el intervalo.
        :param y: etiquetas de las instancias.
        :return: límite inferior, superior y su media
        """

        hits = np.sum(n.predict(x) == y)
        total = len(x)
        p_hat = hits / total  # Proporción
        margin = self.confidence * math.sqrt(p_hat * (1 - p_hat) / total)

        # p +- margin

        lower = p_hat - margin
        upper = p_hat + margin
        mean = (lower + upper) / 2

        return lower, upper, mean

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de exactitud del clasificador
        respecto a unos datos de prueba

        :param x_test: Instancias.
        :param y_test: Etiquetas de las instancias.
        :return: Exactitud
        """

        return accuracy_score(y_test, self.predict(x_test))

    def get_precision_score(self, x_test, y_test):
        """
        Obtiene la puntuación de precisión del clasificador
        respecto a unos datos de prueba

        :param x_test: Instancias.
        :param y_test: Etiquetas de las instancias.
        :return: Precisión
        """
        return precision_score(y_test, self.predict(x_test), average="weighted")

    def get_f1_score(self, x_test, y_test):
        """
        Obtiene el F1-Score

        :param x_test: Instancias.
        :param y_test: Etiquetas de las instancias.
        :return: F1-Score
        """
        return f1_score(y_test, self.predict(x_test), average='weighted')

    def get_recall_score(self, x_test, y_test):
        """
        Obtiene el recall

        :param x_test: Instancias.
        :param y_test: Etiquetas de las instancias.
        :return: Recall
        """
        return recall_score(y_test, self.predict(x_test), average='weighted')


if __name__ == '__main__':
    dl = DatasetLoader('utilidades/datasets/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = DemocraticCoLearning(clfs=[DecisionTreeClassifier(), GaussianNB(), KNeighborsClassifier()])

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)

    st.fit(x, y, x_test, y_test, dl.get_only_features())

    pred = st.predict(x_test)
    print(accuracy_score(y_test, pred))
