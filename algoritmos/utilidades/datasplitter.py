# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 27/01/2023 12:37
# Descripción: Divide los datos para los algoritmos
# Version: 1.0

from pandas import DataFrame
from sklearn.model_selection import train_test_split


def data_split(x: DataFrame, y: DataFrame):
    """
    A partir de todos los datos con el nombre de sus características
    crea un conjunto de datos etiquetados y no etiquetados. A partir de estos,
    que se necesitarán para mantener la información del entrenamiento,
    se obtienen los correspondientes vectores con los que trabajará el clasificador.
    También incluye por completitud una parte de los datos para el test

    :param x: Muestras (con el nombre de las características).
    :param y: Objetivos de las muestras.
    :return: Un log, el conjunto de entrenamiento (features -> x_train y targets -> y_train), los datos no etiquetados
            y el conjunto de test (features -> x_test y targets -> y_test)
    """

    data_train, data_test, train_labels, test_labels = train_test_split(x, y, test_size=0.2, random_state=0)

    data_train_labelled = data_train.sample(frac=0.2)  # POSIBLE PARÁMETRO PERSONALIZABLE
    x_train = data_train_labelled.values
    y_train = train_labels.loc[data_train_labelled.index].values.ravel()

    # El resto son no etiquetados
    x_train_unlabelled = data_train.drop(data_train_labelled.index)

    # Datos de TEST
    x_test = data_test.values
    y_test = test_labels.values

    # Logger con la información de entrenamiento
    log = data_train_labelled.copy()
    log['target'] = y_train
    log['iter'] = 0

    return log, x_train, y_train, x_train_unlabelled, x_test, y_test
