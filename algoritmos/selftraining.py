#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 04/02/2023 21:30
# Descripción: Algoritmo SelfTraining
# Version: 1.1

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator

from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from algoritmos.utilidades import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split
from sklearn.semi_supervised import SelfTrainingClassifier


class SelfTraining:

    def __init__(self, clf, n=None, th=None, n_iter=20):
        """
        Algoritmo SelfTraining, preparado para la obtención de todo
        el proceso de entrenamiento (con sus estadísticas)

        :param clf: Clasificador a usar.
        :param n: Número de mejores predicciones a añadir en cada iteración.
        :param th: Límite (threshold) de probabilidad de correcta clasificación a considerar.
        :param n_iter: Número de iteraciones (si n_iter == 0 finalizará al terminar de clasificar todas las muestras).
        """
        self.clf = clf
        self.n = n
        self.th = th
        self.n_iter = n_iter

        if self.n is None and self.th is None:
            raise ValueError("Se debe seleccionar un criterio de adición")
        if self.n is not None and self.th is not None:
            raise ValueError("Se debe seleccionar un único criterio de adición")
        if self.clf is None or not issubclass(type(self.clf), BaseEstimator):
            raise ValueError("El clasificador base no puede ser nulo y tiene que ser un estimador de Scikit-Learn")
        if self.n_iter < 0:
            raise ValueError("El número de iteraciones no puede ser negativo")

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

        mask = np.ones(len(x), bool)
        i_u = np.where(y == -1)
        mask[i_u] = 0  # A cero los no etiquetados
        x_u = x[~mask]
        x_train = x[mask]
        y_train = y[mask]

        log = pd.DataFrame(x_train, columns=features)
        log['iter'] = 0
        log['target'] = y_train

        iteration = 0
        stats = pd.DataFrame()

        while len(x_u) and (
                iteration < self.n_iter or not self.n_iter):  # Criterio generalmente seguido

            self.clf.fit(x_train, y_train)

            # Predicción
            points = self.clf.predict_proba(x_u).max(axis=1)
            if self.n is not None:  # n mejores
                top = min(self.n, len(x_u))
                topx = points.argsort()[-top:][::-1]
            else:  # mejores con límite
                topx = np.where(points > self.th)
                if not len(topx[0]):
                    break

            # Los nuevos datos a añadir (el dato y la predicción o etiqueta)
            topx_pred = self.clf.predict(x_u[topx])
            # El conjunto de entrenamiento se ha extendido
            x_train = np.append(x_train, x_u[topx], axis=0)
            y_train = np.append(y_train, topx_pred)

            # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
            topx_new_labelled = x_u[topx]
            x_u = np.delete(x_u, topx, axis=0)

            # Preparación de datos para la siguiente iteración
            new_classified = pd.DataFrame(topx_new_labelled, columns=features)
            new_classified['iter'] = iteration + 1
            new_classified['target'] = topx_pred
            log = pd.concat([log, new_classified], ignore_index=True)

            iteration += 1

        self.clf.fit(x_train, y_train)  # Entrenar con los últimos etiquetados

        print(self.get_confusion_matrix(x_test, y_test))
        print(log)
        print("Precisión Implementación: ", self.get_accuracy_score(x_test, y_test))
        return log, iteration

    def get_confusion_matrix(self, x_test, y_test):
        """
        Obtiene la matriz de confusión a partir de unos datos de test

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: Matriz de confusión en forma de array
        """
        cm = confusion_matrix(y_test, self.clf.predict(x_test))
        return cm

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de precisión del clasificador
        respecto a unos datos de prueba

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: Precisión
        """
        p = accuracy_score(y_test, self.clf.predict(x_test))
        return p


if __name__ == '__main__':
    dl = DatasetLoader('utilidades/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = SelfTraining(clf=SVC(kernel='rbf',
                              probability=True,
                              C=1.0,
                              gamma='scale',
                              random_state=0
                              ), n=10, n_iter=20)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, p_unlabelled=0.9, p_test=0.7)

    log, it = st.fit(x, y, x_test, y_test, dl.get_only_features())

    stsk = SelfTrainingClassifier(base_estimator=SVC(kernel='rbf',
                                                     probability=True,
                                                     C=1.0,
                                                     gamma='scale',
                                                     random_state=0
                                                     ))

    stsk.fit(x, y)
    print("Precisión Sklearn: ", stsk.score(x_test, y_test))
