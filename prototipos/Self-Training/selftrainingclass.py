import pandas as pd
import numpy as np

from sklearn.datasets import load_breast_cancer
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.svm import SVC

from utilidades import data_split, log_dim_reduction


class SelfTraining:

    def __init__(self, clf, n):
        """
        Constructor del algoritmo SelfTraining, preparado para la obtención de todo
        el proceso de entrenamiento (con sus estadísticas).

        :param clf: Clasificador a usar
        :param n: Número de mejores predicciones a añadir en cada iteración
        """
        self.clf = clf
        self.n = n

    def fit(self, x, y):
        """

        :param x: Muestras (con el nombre de las características).
        :param y: Objetivos de las muestras.
        :return: El log con la información de entrenamiento y el número de iteraciones
                realizadas.
        """
        (
            log,
            x_train,
            y_train,
            x_train_unlabelled,
            x_test,
            y_test
        ) = data_split(x, y)

        iteration = 1
        stats = pd.DataFrame()
        while len(x_train_unlabelled) != 0:  # Criterio generalmente seguido

            self.clf.fit(x_train, y_train)

            points = self.clf.predict_proba(x_train_unlabelled.values).max(axis=1)

            top = self.n
            if len(x_train_unlabelled.index) < top:
                top = len(x_train_unlabelled.index)

            # La posición de los mejores X datos (con base en su predicción)
            topx = points.argsort()[-top:][::-1]

            # Los nuevos datos a añadir (el dato y la predicción o etiqueta)
            topx_new_labelled = x_train_unlabelled.iloc[topx]
            topx_pred = self.clf.predict(topx_new_labelled.values)

            # El conjunto de entrenamiento se ha extendido
            x_train = np.append(x_train, topx_new_labelled.values, axis=0)
            y_train = np.append(y_train, topx_pred)

            # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
            indexes = x_train_unlabelled.index[topx]
            x_train_unlabelled = x_train_unlabelled.drop(indexes)

            # Preparación de datos para la siguiente iteración
            new_classified = topx_new_labelled.copy()
            new_classified['iter'] = iteration
            new_classified['target'] = topx_pred
            log = pd.concat([log, new_classified])

            iteration += 1
        print(self.get_confusion_matrix(x_test, y_test))
        print(self.get_accuracy_score(x_test, y_test))
        print(self.get_f1_score(x_test, y_test))
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

    def get_f1_score(self, x_test, y_test):
        """
        Obtiene la puntuación de precisión del clasificador
        respecto a unos datos de prueba

        :param x_test: Conjunto de datos de test.
        :param y_test: Objetivo de los datos.
        :return: F1 Score
        """
        f1 = f1_score(y_test, self.clf.predict(x_test), average='micro')
        return f1


data = load_breast_cancer()
x = pd.DataFrame(data['data'], columns=data['feature_names'])
y = pd.DataFrame(data['target'], columns=['target'])

st = SelfTraining(clf=SVC(kernel='rbf',
                          probability=True,
                          C=1.0,
                          gamma='scale',
                          random_state=0
                          ), n=10)

log, it = st.fit(x, y)

pca_df = log_dim_reduction(log, 2)
