# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 11/02/2023 14:30
# Descripción: Métodos comunes para eliminar código duplicado
# Version: 0.1
import numpy as np
from numpy import ndarray
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score


def obtain_train_unlabelled(x: ndarray, y: ndarray):
    """
    A partir de unos datos (tanto etiquetados como no) obtiene
    el conjunto de entrenamiento inicial (todos etiquetados) y
    los no etiquetados

    :param x: Datos.
    :param y: Etiquetar de los datos.
    :return: conjunto de datos etiquetados (x_train) con sus etiquetas (y_train) y conjunto
            de datos no etiquetados
    """

    mask = np.ones(len(x), bool)
    i_u = np.where(y == -1)
    mask[i_u] = 0  # A cero los no etiquetados
    x_u = x[~mask]
    x_train = x[mask]
    y_train = y[mask]

    return x_train, y_train, x_u


def calculate_log_statistics(y_test, predicted):
    """
    Realiza los cálculos de las estadísticas que se desean registrar
    en el log del entrenamiento de los algoritmos

    :param y_test: etiquetas reales.
    :param predicted:  etiquetas predichas.
    :return: lista con las estadísticas calculadas en cada posición
    """

    return [accuracy_score(y_test, predicted),
            precision_score(y_test, predicted, average="weighted"),
            1 - accuracy_score(y_test, predicted),
            f1_score(y_test, predicted, average='weighted'),
            recall_score(y_test, predicted, average='weighted')]
