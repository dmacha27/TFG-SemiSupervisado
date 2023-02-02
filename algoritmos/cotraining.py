#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 27/01/2023 13:25
# Descripción: Algoritmo CoTraining
# Version: 1.0


import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator

from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.svm import SVC

from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_pca_reduction


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

    def fit(self, x, y):
        """
        Proceso de entrenamiento y obtención de la evolución

        :param x: Muestras (con el nombre de las características).
        :param y: Objetivos de las muestras.
        :return: El log con la información de entrenamiento y el número de iteraciones
                realizadas.
        """
        (
            log,
            x_train,
            y_train,
            x_train_unlabelled,
            x_test,
            y_test
        ) = data_split(x, y)

        iteration = 0
        stats = pd.DataFrame()

        log['clf'] = 'inicio'

        selected_unlabelled_samples = x_train_unlabelled.sample(
            n=self.u if self.u <= len(x_train_unlabelled) else len(x_train_unlabelled))
        x_train_unlabelled = x_train_unlabelled.drop(selected_unlabelled_samples.index)
        positive = np.argmin(np.bincount(y_train)[::-1])

        while len(selected_unlabelled_samples) and (
                iteration < self.n_iter or not self.n_iter):  # Criterio generalmente seguido

            x1, x2 = np.array_split(x_train, 2, axis=1)

            self.clf1.fit(x1, y_train)
            self.clf2.fit(x2, y_train)

            x1_u, x2_u = np.array_split(selected_unlabelled_samples.values, 2, axis=1)

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
            topx1_new_labelled = selected_unlabelled_samples.iloc[topx1]
            topx1_pred = pred1[topx1] if len(topx1) > 0 else topx1
            topx2_new_labelled = selected_unlabelled_samples.iloc[topx2]
            topx2_pred = pred2[topx2] if len(topx2) > 0 else topx2

            # El conjunto de entrenamiento se ha extendido
            x_train = np.append(x_train, topx1_new_labelled.values, axis=0)
            y_train = np.append(y_train, topx1_pred)
            x_train = np.append(x_train, topx2_new_labelled.values, axis=0)
            y_train = np.append(y_train, topx2_pred)

            # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
            indexes = selected_unlabelled_samples.index[topx1].union(selected_unlabelled_samples.index[topx2])
            selected_unlabelled_samples = selected_unlabelled_samples.drop(indexes)

            # Preparación de datos para la siguiente iteración (reponer)
            aux = x_train_unlabelled.sample(
                n=self.replenish if len(x_train_unlabelled) >= self.replenish else len(x_train_unlabelled))
            x_train_unlabelled = x_train_unlabelled.drop(aux.index)
            selected_unlabelled_samples = pd.concat([selected_unlabelled_samples, aux])

            # Log
            topx1_aux = topx1_new_labelled.copy()
            topx1_aux['clf'] = f'CLF1({self.clf1.__class__.__name__})'
            topx2_aux = topx2_new_labelled.copy()
            topx2_aux['clf'] = f'CLF2({self.clf2.__class__.__name__})'

            new_classified = pd.concat([topx1_aux, topx2_aux])
            new_classified['iter'] = iteration + 1
            new_classified['target'] = np.concatenate((topx1_pred, topx2_pred))
            log = pd.concat([log, new_classified])
            iteration += 1

        x1, x2 = np.array_split(x_train, 2, axis=1)
        # Entrenar con los últimos etiquetados
        self.clf1.fit(x1, y_train)
        self.clf2.fit(x2, y_train)

        # print(log)
        print(self.get_accuracy_score(x_test, y_test))
        return log, iteration

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de precisión del clasificador
        respecto a unos datos de prueba

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: Precisión
        """
        x1, x2 = np.array_split(x_test, 2, axis=1)

        p1 = accuracy_score(y_test, self.clf1.predict(x1))
        p2 = accuracy_score(y_test, self.clf2.predict(x2))

        return (p1 + p2) / 2


if __name__ == '__main__':
    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

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
                             ), p=1, n=3, u=20, n_iter=120)

    log, it = st.fit(x, y)

    df = log_pca_reduction(log, data['feature_names'], 2)
    print(df.to_string())
