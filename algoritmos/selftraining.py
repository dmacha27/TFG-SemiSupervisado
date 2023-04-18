# Autor: David Martínez Acha
# Fecha: 21/03/2023 18:00
# Descripción: Algoritmo SelfTraining
# Version: 1.2

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score
from algoritmos.utilidades.common import obtain_train_unlabelled, calculate_log_statistics


class SelfTraining:
    """
    Algoritmo Self-Training.
    """
    def __init__(self, clf, n=None, th=None, n_iter=20):
        """
        Algoritmo SelfTraining, preparado para la obtención de todo
        el proceso de entrenamiento (con sus estadísticas)

        :param clf: clasificador a usar.
        :param n: número de mejores predicciones a añadir en cada iteración.
        :param th: límite (threshold) de probabilidad de correcta clasificación a considerar.
        :param n_iter: número de iteraciones (si n_iter == 0 finalizará al terminar
                        de clasificar todas las muestras).
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
            raise ValueError("El clasificador base no puede ser nulo y "
                             "tiene que ser un estimador de Scikit-Learn")
        if self.n_iter < 0:
            raise ValueError("El número de iteraciones no puede ser negativo")

    def fit(self, x, y, x_test, y_test, features):
        """
        Proceso de entrenamiento y obtención de la evolución

        :param x: instancias de entrenamiento.
        :param y: etiquetas de las instancias.
        :param x_test: conjunto de test.
        :param y_test: etiquetas de test.
        :param features: nombre de las características de los datos (para el log).
        :return: log con la información de entrenamiento, estadísticas y el número de iteraciones
                realizadas.
        """

        x_train, y_train, x_u = obtain_train_unlabelled(x, y)

        log = pd.DataFrame(x_train, columns=features)
        log['iter'] = 0
        log['target'] = y_train

        iteration = 0
        stats = pd.DataFrame(columns=['Accuracy', 'Precision', 'Error', 'F1_score', 'Recall'])

        while len(x_u) and (
                iteration < self.n_iter or not self.n_iter):  # Criterio generalmente seguido

            self.clf.fit(x_train, y_train)
            stats.loc[len(stats)] = calculate_log_statistics(y_test, self.predict(x_test))

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
            x_train = np.concatenate((x_train, x_u[topx]), axis=0)
            y_train = np.concatenate((y_train, topx_pred))

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

        rest = pd.DataFrame(x_u, columns=features)
        rest['iter'] = iteration
        rest['target'] = -1
        log = pd.concat([log, rest], ignore_index=True)
        stats.loc[len(stats)] = calculate_log_statistics(y_test, self.predict(x_test))

        return log, stats, iteration

    def predict(self, x):
        """
        Predice la etiqueta de las instancias x

        :param x: instancias
        :return: etiqueta de cada instancia en x
        """

        return self.clf.predict(x)

    def get_accuracy_score(self, x_test, y_test):
        """
        Obtiene la puntuación de exactitud del clasificador
        respecto a unos datos de prueba

        :param x_test: instancias.
        :param y_test: etiquetas de las instancias.
        :return: accuracy
        """
        return accuracy_score(y_test, self.predict(x_test))
