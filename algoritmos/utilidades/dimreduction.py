#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 27/01/2023 12:37
# Descripción: Reduce la dimensionalidad de los datos para ser representados
# Version: 1.1

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def log_dim_reduction(log, n_com=2):
    """
    Reduce las características (features) de los datos para ser representado
    en un gráfico. En principio para 2 componentes, arbitrariamente etiquetadas como C1, C2..

    :param log: Información de entrenamiento.
    :param n_com: Número de componentes a reducir.
    :return: El log transformado al número de componentes
    """

    # Está planteado para que las dos últimas columnas sean la iteración y el target u objetivo
    if len(log.columns) == 4:
        return log.columns['C1', 'C2', 'target', 'iter']

    rest = log.iloc[:, len(log.columns) - 2:]
    features = log.iloc[:, :len(log.columns) - 2]

    features_standard = StandardScaler().fit_transform(features)

    pca = PCA(n_components=n_com)

    pca_features = pca.fit_transform(features_standard)

    df = pd.DataFrame(
        data=pca_features,
        columns=[f"C{i}" for i in range(1, n_com + 1)])

    df['target'] = rest['target'].values
    df['iter'] = rest['iter'].values

    return df
