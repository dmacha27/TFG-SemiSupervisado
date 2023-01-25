import pandas as pd
import numpy as np

from sklearn.datasets import load_breast_cancer
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.svm import SVC

from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_dim_reduction


class CoTraining:

    def __init__(self, clf1, clf2, n):
        """
        Constructor del algoritmo SelfTraining, preparado para la obtención de todo
        el proceso de entrenamiento (con sus estadísticas).

        :param clf1: Clasificador a usar
        :param clf2: Clasificador a usar
        :param n: Número de mejores predicciones a añadir en cada iteración
        """
        self.clf1 = clf1
        self.clf2 = clf2
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

            x1, x2 = np.array_split(x_train, 2, axis=1)

            self.clf1.fit(x1, y_train)
            self.clf2.fit(x2, y_train)

            x1_u, x2_u = np.array_split(x_train_unlabelled.values, 2, axis=1)

            points1 = self.clf1.predict_proba(x1_u).max(axis=1)
            points2 = self.clf2.predict_proba(x2_u).max(axis=1)

            top = self.n
            if len(x_train_unlabelled.index) < top:
                top = len(x_train_unlabelled.index)

            # La posición de los mejores X datos (con base en su predicción)
            topx1 = points1.argsort()[-top:][::-1]
            topx2 = points2.argsort()[-top:][::-1]

            # Las mejores predicciones pueden coincidir (desempate)
            duplicates = np.intersect1d(topx1, topx2)
            for d in duplicates:
                if points1[d] > points2[d]:
                    topx2 = topx2[topx2 != d]
                else:
                    topx1 = topx1[topx1 != d]

            # Los nuevos datos a añadir (el dato y la predicción o etiqueta)
            topx1_new_labelled = x_train_unlabelled.iloc[topx1]
            topx1_pred = self.clf1.predict(x1_u[topx1]) if len(topx1) > 0 else []
            topx2_new_labelled = x_train_unlabelled.iloc[topx2]
            topx2_pred = self.clf2.predict(x2_u[topx2]) if len(topx2) > 0 else []

            # El conjunto de entrenamiento se ha extendido
            x_train = np.append(x_train, topx1_new_labelled.values, axis=0)
            y_train = np.append(y_train, topx1_pred)
            x_train = np.append(x_train, topx2_new_labelled.values, axis=0)
            y_train = np.append(y_train, topx2_pred)

            # Se eliminan los datos que antes eran no etiquetados pero ahora sí lo son
            indexes = x_train_unlabelled.index[topx1].union(x_train_unlabelled.index[topx2])
            x_train_unlabelled = x_train_unlabelled.drop(indexes)

            # Preparación de datos para la siguiente iteración
            new_classified = pd.concat([topx1_new_labelled.copy(), topx2_new_labelled.copy()])
            new_classified['iter'] = iteration
            new_classified['target'] = np.concatenate((topx1_pred, topx2_pred))
            log = pd.concat([log, new_classified])
            iteration += 1

        return log, iteration


if __name__ == '__main__':
    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

    st = CoTraining(clf1=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ),
                    clf2=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ), n=10)

    log, it = st.fit(x, y)

    df = log_dim_reduction(log, 2)
