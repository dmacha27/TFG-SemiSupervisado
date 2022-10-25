import pandas as pd
import time
import numpy as np

import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
#from sklearn.semi_supervised import SelfTrainingClassifier ¿Próximo prototipo?


def mostar(data):
    #Muestra una gráfica por cada iteración en un mismo eje de coordenadas
    #Cada punto codificado con "reading score" como la x y "writing score" como la y
    data['Etiqueta'] = data.apply(lambda x: 'Buenos' if x['Etiqueta'] == 1 else 'No tan buenos' if x['Etiqueta'] == 0 else 'No etiquetados',
                                              axis=1)
    fig = px.scatter(data, x='reading score', y='writing score', opacity=1, animation_frame='Iter', color='Etiqueta',
                     color_discrete_map={'No tan buenos': 'blue', 'Buenos': 'red', 'No etiquetados': 'lightgrey'},title='Self-Training',
                     )

    fig.show()

"""

                    PREPARACIÓN DE LA ESTRUCTURA DE LOS DATOS
                    
                    Se leen los datos y se etiquetan sobre un criterio completamente arbitrario
                    elegido.

"""


# Obtención de los datos
df = pd.read_csv('./datasets/exams.csv',
                 encoding='utf-8', delimiter=',',
                 usecols=['reading score', 'writing score']
                 )

# Denotará qué alumnos son buenos en en la lectura y escritura (lengua)
df['Bueno_Lenguaje'] = df.apply(lambda x: 1 if x['reading score'] > 70 and x['writing score'] > 70 else 0, axis=1)


data_train, data_test = train_test_split(df, test_size=0.25, random_state=0)

#Dentro del conjunto de entrenamiento se escogerán unas con datos etiquetados (1 o 0) y otros que no lo estén (-1)
data_train['Etiquetados'] = True
# Aleatoriamente algunos no estarán etiquetados
data_train.loc[data_train.sample(frac=0.1, random_state=0).index, 'Etiquetados'] = False

# 1 para los alumnos bueno en lengua, 0 para los que no y -1 para los que no se tiene información
data_train['Etiqueta'] = data_train.apply(lambda x: x['Bueno_Lenguaje'] if x['Etiquetados'] == False else -1,
                                               axis=1)

data_train = data_train[['reading score', 'writing score', 'Etiqueta']]

#Para poder mostrar en cada iteración, se irán añadiendo al dataframe todos los datos de nuevo por cada iteración
# pero es previsible que algunas etiquetas cambien en cada una de ellas. Así se podrá visualizar las fases.
data_train['Iter'] = 0
data_train['group'] = 0

# Show target value distribution
print('Clase - Número de datos')
print(data_train['Etiqueta'].value_counts())


"""
                    PREPARACIÓN DE LOS DATOS PARA EL ALGORITMO
"""

# Seleccionar todos los datos etiquetados (el -1 es como si no lo estuviera)
data_train_labeled = data_train[data_train['Etiqueta'] != -1]

# Seleccionar todos los datos no etiquetados (el -1 es como si no lo estuviera)
data_train_unlabelled = data_train[data_train['Etiqueta'] == -1]

# Datos de entrenamiento
x_train = data_train_labeled[['reading score', 'writing score']]
y_train = data_train_labeled['Etiqueta'].values

# Datos de entrenamiento no etiquetados
x_train_unlabelled = data_train_unlabelled[['reading score', 'writing score']]

# Datos de TEST
#EN ESTE PROTOTIPO SOLO SE MUESTRA EL PROCESO DE ENTRENAMIENTO
#x_test = data_test[['reading score', 'writing score']]
#y_test = data_test['Bueno_Lenguaje'].values



"""
                    ENTRENAMIENTO
                    
                    Es importante destacar que se está simulando Self-Training mediante un clasificador
                    general.
"""

NTOP = 100 #Se seleccionarán los 100 mejores datos (predicción más acertada) (cambiar si se desea)


clf = SVC(kernel='rbf',
          probability=True,
          C=1.0,
          gamma='scale',
          random_state=0
          )

# Iteración
i = 1

#Datos para mostrar
data_show = data_train.copy()

while i < 25:
    time.sleep(1)
    print('Clase - Número de datos')
    print(data_train['Etiqueta'].value_counts())

    if len(data_train['Etiqueta'].value_counts().index) == 2:
        break

    clf = clf.fit(x_train, y_train)

    # Puntuación de las predicciones para datos no etiquetados todavía (son los que luego se seleccionarán los X mejores)

    puntos = clf.predict_proba(x_train_unlabelled).max(axis=1)
    X = NTOP #Establece el número de mejores datos no etiquetados a añadir
    if len(x_train_unlabelled.index) < NTOP:
        X = len(x_train_unlabelled.index)

    # La posición de los mejores X datos (en base a su predicción)
    topX = puntos.argsort()[-X:][::-1]

    #Los nuevos datos a añadir (el dato y la predicción o etiqueta)
    topX_new_labelled = x_train_unlabelled.iloc[topX]
    topX_pred = clf.predict(topX_new_labelled)

    # El conjunto de entrenamiento se ha extendido
    x_train = pd.concat([x_train, topX_new_labelled])
    y_train = np.append(y_train, topX_pred)

    #Se eleminan los datos que antes eran no etiquetados pero ahora sí lo son
    x_train_unlabelled.drop(x_train_unlabelled.index[topX], inplace=True)

    #Preparación de datos para la siguiente iteración
    data_train_labeled = x_train.copy()
    data_train_labeled['Etiqueta'] = y_train

    data_train_unlabelled = x_train_unlabelled.copy()
    data_train_unlabelled['Etiqueta'] = -1

    data_train = pd.concat([data_train_labeled, data_train_unlabelled])

    data_train['Iter'] = i
    data_train['group'] = 0
    data_show = pd.concat([data_show, data_train])

    i += 1

mostar(data_show)
