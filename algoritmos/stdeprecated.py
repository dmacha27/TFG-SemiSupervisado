import pandas as pd
import numpy as np

import plotly.express as px
from pandas import DataFrame

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC



def mostrar(data: DataFrame):
    """Muestra una gráfica por cada iteración en un mismo eje de coordenadas. Cada punto codificado con "reading
    score" como la "x" y "writing score" como la "y"

    :param data: Contiene cada uno de los datos (con sus características) por cada iteración para ser
    visualizado con plotly.
    """
    #
    data['Etiqueta'] = data.apply(
        lambda x: 'Buenos' if x['Etiqueta'] == 1 else 'No tan buenos' if x['Etiqueta'] == 0 else 'No etiquetados',
        axis=1)
    fig = px.scatter(data, x='reading score', y='writing score', opacity=1, animation_frame='IterClasificado',
                     color='Etiqueta',
                     color_discrete_map={'No tan buenos': 'blue', 'Buenos': 'red', 'No etiquetados': 'lightgrey'},
                     title='Self-Training',
                     )

    fig.show()


def preparar(data: DataFrame, iteraciones: int):
    """Prepara los datos para poder ser mostrados. Genera una fila nueva de cada dato por cada una de las
    iteraciones. Si la iteración un dato se ha etiquetado en la iteración X, las iteraciones anteriores será no
    etiquetado, en la iteración X y las siguientes se establecerá la generada por el algoritmo.
    :param data: Conjunto de datos con sus características y la iteración en la que se establece la etiqueta.
    :param iteraciones.
    :return: Conjunto de datos preparados para la visualización.
    :rtype: DataFrame
    """
    data_show = pd.DataFrame()
    for i in range(0, iteraciones):
        yaclasificados = data.copy()[data['IterClasificado'] <= i]
        yaclasificados['IterClasificado'] = i

        noclasificados = data.copy()[data['IterClasificado'] > i]
        noclasificados['IterClasificado'] = i
        noclasificados['Etiqueta'] = -1

        data_show = pd.concat([data_show, yaclasificados, noclasificados])
    return data_show


def datos():
    """Prepara la estructura de datos: Se leen los datos y se etiquetan sobre un criterio completamente arbitrario
    elegido.

    :returns:
        - data_train_labeled - Conjunto de datos de entrada etiquetados
        - data_train_unlabelled - Conjunto de datos no etiquetados
        - x_train - Cojunto de datos de entrenamiento
        - y_train - Etiquetas del conjunto de datos "x_train"
        - x_train_unlabelled - Conjunto de datos de entrenamiento no etiquetados
    """
    # Obtención de los datos
    df = pd.read_csv('../datasets/exams.csv',
                     encoding='utf-8', delimiter=',',
                     usecols=['reading score', 'writing score']
                     )

    # Denotará qué alumnos son buenos en en la lectura y escritura (lengua)
    df['Bueno_Lenguaje'] = df.apply(lambda x: 1 if x['reading score'] > 70 and x['writing score'] > 70 else 0, axis=1)

    data_train, data_test = train_test_split(df, test_size=0.25, random_state=0)

    # Dentro del conjunto de entrenamiento se escogerán unas con datos etiquetados (1 o 0) y otros que no lo estén (-1)
    data_train['Etiquetados'] = True
    # Aleatoriamente algunos no estarán etiquetados
    data_train.loc[data_train.sample(frac=0.1, random_state=0).index, 'Etiquetados'] = False

    # 1 para los alumnos bueno en lengua, 0 para los que no y -1 para los que no se tiene información
    data_train['Etiqueta'] = data_train.apply(lambda x: x['Bueno_Lenguaje'] if x['Etiquetados'] is False else -1,
                                              axis=1)

    data_train = data_train[['reading score', 'writing score', 'Etiqueta']]
    data_train.drop_duplicates(['reading score', 'writing score'], inplace=True)

    # Seleccionar todos los datos etiquetados (el -1 es como si no lo estuviera)
    data_train_labeled = data_train.copy()[data_train['Etiqueta'] != -1]
    data_train_labeled['IterClasificado'] = 0

    # Seleccionar todos los datos no etiquetados (el -1 es como si no lo estuviera)
    data_train_unlabelled = data_train.copy()[data_train['Etiqueta'] == -1]
    data_train_unlabelled['IterClasificado'] = None

    # Datos de entrenamiento
    x_train = data_train_labeled[['reading score', 'writing score']].values
    y_train = data_train_labeled['Etiqueta'].values

    # Datos de entrenamiento no etiquetados
    x_train_unlabelled = data_train_unlabelled[['reading score', 'writing score']]

    # Datos de TEST
    # EN ESTE PROTOTIPO SOLO SE MUESTRA EL PROCESO DE ENTRENAMIENTO
    # x_test = data_test[['reading score', 'writing score']]
    # y_test = data_test['Bueno_Lenguaje'].values

    return data_train_labeled, data_train_unlabelled, x_train, y_train, x_train_unlabelled


NTOP = 100  # Se seleccionarán los 100 mejores datos (predicción más acertada) (cambiar si se desea)


def entrenamiento(data_train_labeled: DataFrame, data_train_unlabelled: DataFrame, x_train,
                  y_train, x_train_unlabelled: DataFrame):
    """Se encarga del entrenamiento de un clasificador (Supor Vector Classification) mediante algoritmo Self-Training

    :param DataFrame data_train_labeled: Conjunto de datos de entrada etiquetados.
    :param DataFrame data_train_unlabelled: Conjunto de datos no etiquetados.
    :param DataFrame x_train: Cojunto de datos de entrenamiento (cada iteración aumentará).
    :param DataFrame y_train: Etiquetas del conjunto de datos "x_train".
    :param DataFrame x_train_unlabelled: Conjunto de datos de entrenamiento no etiquetados.
    :returns:
        - data_train_labeled - Conjunto de todos los datos ya etiquetados
        - iteration - iteración en la que para el algoritmo
    """
    clf = SVC(kernel='rbf',
              probability=True,
              C=1.0,
              gamma='scale',
              random_state=0
              )

    # Iteración
    iteration = 1

    while len(x_train_unlabelled) != 0:

        clf = clf.fit(x_train, y_train)

        # Puntuación de las predicciones para datos no etiquetados todavía (son los que luego se seleccionarán los X
        # mejores)

        puntos = clf.predict_proba(x_train_unlabelled.values).max(axis=1)
        x = NTOP  # Establece el número de mejores datos no etiquetados a añadir
        if len(x_train_unlabelled.index) < NTOP:
            x = len(x_train_unlabelled.index)

        # La posición de los mejores X datos (con base en su predicción)
        topx = puntos.argsort()[-x:][::-1]

        # Los nuevos datos a añadir (el dato y la predicción o etiqueta)
        topx_new_labelled = x_train_unlabelled.iloc[topx]
        topx_pred = clf.predict(topx_new_labelled.values)

        # El conjunto de entrenamiento se ha extendido
        x_train = np.append(x_train, topx_new_labelled.values, axis=0)
        y_train = np.append(y_train, topx_pred)

        # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
        indexs = x_train_unlabelled.index[topx]
        x_train_unlabelled = x_train_unlabelled.drop(indexs)

        # Preparación de datos para la siguiente iteración
        new_classified = topx_new_labelled.copy()
        new_classified['IterClasificado'] = iteration
        data_train_labeled = pd.concat([data_train_labeled, new_classified])
        data_train_labeled['Etiqueta'] = y_train

        data_train_unlabelled = data_train_unlabelled.drop(indexs)
        iteration += 1
    return data_train_labeled, iteration
