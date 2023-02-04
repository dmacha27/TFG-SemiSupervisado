# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 04/02/2023 14:30
# Descripción: Divide los datos para los algoritmos
# Version: 1.1
import numpy as np
from pandas import DataFrame
from sklearn.model_selection import train_test_split


def data_split(x: DataFrame, y: DataFrame, p_unlabelled=0.8, p_test=0.2):
    """
    A partir de todos los datos con el nombre de sus características
    crea un conjunto de datos etiquetados y no etiquetados. A partir de estos,
    que se necesitarán para mantener la información del entrenamiento,
    se obtienen los correspondientes vectores con los que trabajará el clasificador.
    También incluye por completitud una parte de los datos para el test

    :param x: Muestras (con el nombre de las características).
    :param y: Objetivos de las muestras.
    :param p_unlabelled: Porcentaje no etiquetados.
    :param p_test: Porcentaje de test.
    :return: El conjunto de entrenamiento (features -> x_train y targets -> y_train), los datos no etiquetados
            y el conjunto de test (features -> x_test y targets -> y_test)
    """

    x = np.array(x)
    y = np.array(y)

    x_train, x_unlabelled, y_train, _ = train_test_split(x, y, test_size=p_unlabelled, random_state=0)

    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=p_test, random_state=0)

    x_train = np.append(x_train, x_unlabelled, axis=0)
    y_train = np.append(y_train, [-1] * len(x_unlabelled))

    return x_train, y_train, x_test, y_test.ravel()


def data_split_already_unlabelled(x: DataFrame, y: DataFrame, p_test=0.2):
    """
    A partir de todos los datos con el nombre de sus características
    crea un conjunto de datos de entrenamiento y de test. Los datos de entrenamiento no están todos etiquetados

    :param x: Muestras (con el nombre de las características).
    :param y: Objetivos de las muestras.
    :param p_test: Porcentaje de test.
    :return: El conjunto de entrenamiento (features -> x_train y targets -> y_train)
    y el conjunto de test (features -> x_test y targets -> y_test)
    """
    x = np.array(x)
    y = np.array(y)

    i_u = np.where(x == -1)
    x_unlabelled = x[i_u]
    x = x[~i_u]
    y = y[~i_u]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=p_test, random_state=0)

    x_train = np.append(x_train, x_unlabelled, axis=0)
    y_train = np.append(y_train, [-1] * len(x_unlabelled))

    return x_train, y_train, x_test, y_test.ravel()
