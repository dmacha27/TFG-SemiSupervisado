# Autor: David Martínez Acha
# Fecha: 27/01/2023 12:37
# Descripción: Reduce la dimensionalidad de los datos para ser representados
# Version: 1.1

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def log_pca_reduction(log, features, n_com=2):
    """
    Reduce las características (features) de los datos para ser representado
    en un gráfico. En principio para 2 componentes, etiquetadas como C1, C2..

    :param log: información de entrenamiento.
    :param features: lista de características que se van a reducir.
    :param n_com: Número de componentes a reducir.
    :return: log transformado al número de componentes
    """

    not_features = log.columns.difference(features)
    rest = log[not_features]
    features = log[features]

    features_standard = StandardScaler().fit_transform(features)

    pca = PCA(n_components=n_com)

    pca_features = pca.fit_transform(features_standard)

    df = pd.DataFrame(
        data=pca_features,
        columns=[f"C{i}" for i in range(1, n_com + 1)])

    df[not_features] = rest[not_features].values
    return df


def log_cxcy_reduction(log, cx, cy, features):
    """
    Reduce el log a las dos características (features) especificadas. Con las dos componentes cx y cy

    :param log: información de entrenamiento.
    :param cx: componente X.
    :param cy: componente Y.
    :param features: características de los datos (sin target o información adicional).
    :return: log transformado.
    """

    return log[[cx, cy] + list(log.columns.difference(features))]
