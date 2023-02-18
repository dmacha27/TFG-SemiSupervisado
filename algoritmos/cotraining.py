#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 04/02/2023 21:30
# Descripción: Algoritmo CoTraining
# Version: 1.1


import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator

from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score
from sklearn.svm import SVC

from algoritmos.utilidades import DatasetLoader
from algoritmos.utilidades.common import obtain_train_unlabelled
from algoritmos.utilidades.datasplitter import data_split


class CoTraining:

    def __init__(self, clf1, clf2, p, n, u, n_iter):
        """
        Algoritmo CoTraining, preparado para la obtención de todo
        el proceso de entrenamiento (con sus estadísticas).

        :param clf1: Clasificador a usar.
        :param clf2: Clasificador a usar.
        :param p: Número de predicciones positivas a añadir. Se entiende como positiva de aquellas predicciones
                    que corresponde con la clase minoritaria.
        :param n: Número de predicciones negativas a añadir. No positivas
        :param u: Número de muestras seleccionadas en el inicio.
        :param n_iter: Número de iteraciones
        """

        self.clf1 = clf1
        self.clf2 = clf2
        self.p = p
        self.n = n
        self.u = u
        self.replenish = 2 * self.p + 2 * self.n
        self.n_iter = n_iter

        if self.clf1 is None or not issubclass(type(self.clf1), BaseEstimator):
            raise ValueError("El primer clasificador base no puede ser nulo y tiene que ser un estimador de "
                             "Scikit-Learn")
        if self.clf2 is None or not issubclass(type(self.clf2), BaseEstimator):
            raise ValueError("El segundo clasificador base no puede ser nulo y tiene que ser un estimador de "
                             "Scikit-Learn")
        if self.n_iter < 0:
            raise ValueError("El número de iteraciones no puede ser negativo")
        if self.p < 0:
            raise ValueError("El número de positivos no puede ser negativo")
        if self.n < 0:
            raise ValueError("El número de negativos no puede ser negativo")
        if not self.n and not self.p:
            raise ValueError("Los positivos y negativos no pueden ser ambos nulos "
                             "(no se añadirían nuevas predicciones)")
        if self.u <= 0:
            raise ValueError("El número de elementos iniciales debe ser, al menos, 1")

    def fit(self, x, y, x_test, y_test, features):
        """
        Proceso de entrenamiento y obtención de la evolución

        :param x: Muestras (con el nombre de las características).
        :param y: Objetivos de las muestras.
        :param x_test: Conjunto de test.
        :param y_test: Etiquetas de test.
        :param features: Nombre de las características de los datos (para el log).
        :return: El log con la información de entrenamiento y el número de iteraciones
                realizadas.
        """

        x_train, y_train, x_u = obtain_train_unlabelled(x, y)

        log = pd.DataFrame(x_train, columns=features)
        log['iter'] = 0
        log['target'] = y_train
        log['clf'] = 'inicio'

        iteration = 0
        stats = pd.DataFrame(columns=['iter', 'accuracy', 'precision'])

        ids = np.random.choice(len(x_u), size=self.u if self.u <= len(x_u) else len(x_u), replace=False)
        s_u_s = x_u[ids]  # Selected unlabelled samples
        x_u = np.delete(x_u, ids, axis=0)
        positive = np.argmin(np.bincount(y_train)[::-1])

        while len(s_u_s) and (
                iteration < self.n_iter or not self.n_iter):  # Criterio generalmente seguido

            x1, x2 = np.array_split(x_train, 2, axis=1)

            self.clf1.fit(x1, y_train)
            self.clf2.fit(x2, y_train)
            stats.loc[len(stats)] = [iteration,
                                     self.get_accuracy_score(x_test, y_test),
                                     self.get_precision_score(x_test, y_test)]

            x1_u, x2_u = np.array_split(s_u_s, 2, axis=1)

            pred1, points1 = self.clf1.predict(x1_u), self.clf1.predict_proba(x1_u)
            pred2, points2 = self.clf2.predict(x2_u), self.clf2.predict_proba(x2_u)

            best_p_ipoints1 = points1[:, positive].argsort()[-self.p:]
            best_n_ipoints1 = np.delete(points1, positive, axis=1).max(axis=1, initial=0).argsort()[-self.n:]

            best_p_ipoints2 = points2[:, positive].argsort()[-self.p:]
            best_n_ipoints2 = np.delete(points2, positive, axis=1).max(axis=1, initial=0).argsort()[-self.n:]

            topx1 = np.unique(np.concatenate((best_p_ipoints1, best_n_ipoints1), dtype=int))
            topx2 = np.unique(np.concatenate((best_p_ipoints2, best_n_ipoints2), dtype=int))

            # Las mejores predicciones pueden coincidir (desempate)
            duplicates = np.intersect1d(topx1, topx2)
            for d in duplicates:
                if points1[d][int(pred1[d])] > points2[d][int(pred2[d])]:
                    topx2 = topx2[topx2 != d]
                else:
                    topx1 = topx1[topx1 != d]

            # Los nuevos datos a añadir (el dato y la predicción o etiqueta)
            topx1_new_labelled = s_u_s[topx1]
            topx1_pred = pred1[topx1] if len(topx1) > 0 else topx1
            topx2_new_labelled = s_u_s[topx2]
            topx2_pred = pred2[topx2] if len(topx2) > 0 else topx2

            # El conjunto de entrenamiento se ha extendido
            x_train = np.concatenate((x_train, topx1_new_labelled, topx2_new_labelled), axis=0)
            y_train = np.concatenate((y_train, topx1_pred, topx2_pred))

            # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
            indexes = np.concatenate((topx1, topx2))
            s_u_s = np.delete(s_u_s, indexes, axis=0)

            # Preparación de datos para la siguiente iteración (reponer)
            ids_replenish = np.random.choice(len(x_u), size=self.replenish if len(x_u) >= self.replenish else len(x_u),
                                             replace=False)
            s_u_s = np.append(s_u_s, x_u[ids_replenish], axis=0)
            x_u = np.delete(x_u, ids_replenish, axis=0)

            # Log
            topx1_aux = pd.DataFrame(topx1_new_labelled, columns=features)
            topx1_aux['clf'] = f'CLF1({self.clf1.__class__.__name__})'
            topx2_aux = pd.DataFrame(topx2_new_labelled, columns=features)
            topx2_aux['clf'] = f'CLF2({self.clf2.__class__.__name__})'

            new_classified = pd.concat([topx1_aux, topx2_aux], ignore_index=True)
            new_classified['iter'] = iteration + 1
            new_classified['target'] = np.concatenate((topx1_pred, topx2_pred))
            log = pd.concat([log, new_classified], ignore_index=True)
            iteration += 1

        x1, x2 = np.array_split(x_train, 2, axis=1)
        # Entrenar con los últimos etiquetados
        self.clf1.fit(x1, y_train)
        self.clf2.fit(x2, y_train)

        rest = pd.DataFrame(np.concatenate((x_u, s_u_s), axis=0), columns=features)
        rest['iter'] = iteration
        rest['target'] = -1
        rest['clf'] = -1
        log = pd.concat([log, rest], ignore_index=True)
        stats.loc[len(stats)] = [iteration,
                                 self.get_accuracy_score(x_test, y_test),
                                 self.get_precision_score(x_test, y_test)]

        return log, stats

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de exactitud del clasificador
        respecto a unos datos de prueba

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: Exactitud
        """
        x1, x2 = np.array_split(x_test, 2, axis=1)

        a1 = accuracy_score(y_test, self.clf1.predict(x1))
        a2 = accuracy_score(y_test, self.clf2.predict(x2))

        return (a1 + a2) / 2

    def get_precision_score(self, x_test, y_test):
        """
        Obtiene la puntuación de precisión del clasificador
        respecto a unos datos de prueba

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: Precisión
        """
        x1, x2 = np.array_split(x_test, 2, axis=1)

        p1 = precision_score(y_test, self.clf1.predict(x1))
        p2 = precision_score(y_test, self.clf2.predict(x2))

        return (p1 + p2) / 2


if __name__ == '__main__':
    dl = DatasetLoader('utilidades/datasets/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = CoTraining(clf1=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ),
                    clf2=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ), p=1, n=3, u=5, n_iter=10)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)

    log, stats = st.fit(x, y, x_test, y_test, dl.get_only_features())

    print(st.get_accuracy_score(x_test, y_test))
