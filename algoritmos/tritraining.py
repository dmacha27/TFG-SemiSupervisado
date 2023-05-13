# Autor: David Martínez Acha
# Fecha: 28/03/2023 20:45
# Descripción: Algoritmo Tri-Training
# Version: 1.0

import numpy as np
from math import floor, ceil

import pandas as pd
from sklearn.metrics import accuracy_score

from algoritmos.utilidades.common import obtain_train_unlabelled, calculate_log_statistics


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

    def fit(self, x, y, x_test, y_test, features):
        """
        Proceso de entrenamiento y obtención de la evolución.

        Algoritmo de Zhi-Hua Zhou y Ming Li.


        :param x: Instancias.
        :param y: Etiquetas de las instancias.
        :param x_test: Conjunto de test.
        :param y_test: Etiquetas de test.
        :param features: nombre de las características de los datos (para el log).
        :return: log con la información de entrenamiento, estadísticas generales, estadísticas
                    específicas y el número de iteraciones realizadas.
        """

        x_train, y_train, x_u = obtain_train_unlabelled(x, y)

        # LOG
        log = pd.DataFrame(x_train, columns=features)
        log['iters'] = [[0]] * len(log)
        log['targets'] = [[lab] for lab in y_train]
        log['clfs'] = [['inicio']] * len(log)

        rest = pd.DataFrame(x_u, columns=features)
        rest['iters'] = [[[] for __ in range(len(self.clfs))] for _ in range(len(rest))]
        rest['targets'] = [[[] for __ in range(len(self.clfs))] for _ in range(len(rest))]
        rest['clfs'] = [[f"CLF{i + 1}({n.__class__.__name__})" for i, n in enumerate(self.clfs)]] * len(rest)

        log = pd.concat([log, rest], ignore_index=True)

        stat_columns = ['Accuracy', 'Precision', 'Error', 'F1_score', 'Recall']
        stats = pd.DataFrame(columns=stat_columns)

        specific_stats = {f"CLF{i + 1}({n.__class__.__name__})": pd.DataFrame(columns=stat_columns) for i, n in
                          enumerate(self.clfs)}

        e_prime = [0.5] * len(self.clfs)
        l_prime = [0] * len(self.clfs)
        for i, n in enumerate(self.clfs):
            s_i = np.random.choice(len(x_train), len(x_train))
            n.fit(x_train[s_i], y_train[s_i])

        # Li (instancias)
        l_i_x = [[] for _ in range(len(self.clfs))]
        # Li (etiquetas)
        l_i_y = [[] for _ in range(len(self.clfs))]
        e_i = [0] * len(self.clfs)
        updates = [False] * len(self.clfs)

        iteration = 0
        change = True
        while change:
            change = False

            for i, n in enumerate(self.clfs):
                clf_stat = specific_stats[f"CLF{i + 1}({n.__class__.__name__})"]
                clf_stat.loc[len(clf_stat)] = calculate_log_statistics(y_test, n.predict(x_test))

            stats.loc[len(stats)] = calculate_log_statistics(y_test, self.predict(x_test))

            vect_indexes = []
            for i in range(len(self.clfs)):
                l_i_x[i] = []
                l_i_y[i] = []
                updates[i] = False
                e_i[i] = self._measure_error(self.others[i], x_train, y_train)

                if e_i[i] < e_prime[i]:
                    h_j = self.clfs[self.others[i][0]].predict(x_u)
                    h_k = self.clfs[self.others[i][1]].predict(x_u)
                    vect = h_j == h_k
                    l_i_x[i] = x_u[vect]
                    l_i_y[i] = h_j[vect]

                    # LOG
                    vect_indexes = np.nonzero(vect)[0]

                    if l_prime[i] == 0:
                        l_prime[i] = floor(e_i[i] / (e_prime[i] - e_i[i]) + 1)

                    if l_prime[i] < len(l_i_x[i]):
                        if e_i[i] * len(l_i_x[i]) < e_prime[i] * l_prime[i]:
                            updates[i] = True
                        elif l_prime[i] > (e_i[i] / (e_prime[i] - e_i[i])):
                            to_keep = np.random.choice(len(l_i_x[i]),
                                                       ceil(e_prime[i] * l_prime[i] / e_i[i] - 1))
                            l_i_x[i] = [l_i_x[i][keep] for keep in to_keep]
                            l_i_y[i] = [l_i_y[i][keep] for keep in to_keep]
                            vect_indexes = to_keep
                            updates[i] = True

            for i, n in enumerate(self.clfs):
                if updates[i]:
                    change = True
                    e_prime[i] = e_i[i]
                    l_prime[i] = len(l_i_x[i])

                    # LOG
                    for index, y_aux in zip(vect_indexes, l_i_y[i]):
                        log.loc[len(x_train) + index, 'iters'][i].append(iteration + 1)
                        log.loc[len(x_train) + index, 'targets'][i].append(y_aux)

                    mew_x_train = np.concatenate((x_train, l_i_x[i]), axis=0)
                    mew_y_train = np.concatenate((y_train, l_i_y[i]))

                    n.fit(mew_x_train, mew_y_train)

            iteration += 1

        return log, stats, specific_stats, iteration - 1

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
