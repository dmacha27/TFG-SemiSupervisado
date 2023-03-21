# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 11/02/2023 14:15
# Descripción: Divide los datos para los algoritmos
# Version: 1.2
import numpy as np
from pandas import DataFrame
from sklearn.model_selection import train_test_split

from algoritmos.utilidades.common import obtain_train_unlabelled


def data_split(x: DataFrame, y: DataFrame, is_unlabelled, p_unlabelled=0.8, p_test=0.2):
    """
    A partir de todos los datos con el nombre de sus características
    crea un conjunto de entrenamiento (con datos etiquetados y no etiquetados) y el conjunto de test.
    Si el conjunto ya tiene no etiquetados, simplemente dividirá en conjunto de test

    :param x: Muestras (con el nombre de las características).
    :param y: Objetivos de las muestras.
    :param is_unlabelled: Indica si el conjunto de datos ya contiene no etiquetados.
    :param p_unlabelled: Porcentaje no etiquetados.
    :param p_test: Porcentaje de test.
    :return: El conjunto de entrenamiento (features -> x_train y targets -> y_train), los datos no etiquetados
            y el conjunto de test (features -> x_test y targets -> y_test)
    """

    x = np.array(x)
    y = np.array(y).ravel()

    if not is_unlabelled:
        x_train, x_u, y_train, _ = train_test_split(x, y, test_size=p_unlabelled, random_state=0, stratify=y)
    else:
        x_train, y_train, x_u = obtain_train_unlabelled(x, y)

    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=p_test, random_state=0,
                                                        stratify=y_train)

    x_train = np.append(x_train, x_u, axis=0)
    y_train = np.append(y_train, [-1] * len(x_u))

    return x_train, y_train, x_test, y_test
