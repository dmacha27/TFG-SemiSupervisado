# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 29/01/2023 23:24
# Descripción: Permite cargar datasets
# Version: 1.1

from os.path import isfile

import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.preprocessing import LabelEncoder

from algoritmos.utilidades import FileType


class DatasetLoader:

    def __init__(self, file):
        """
        Cargador para archivos (ARFF o CSV).

        :param file: Ruta del fichero
        """

        self.target = None
        if not isfile(file):
            raise FileNotFoundError("El archivo no existe en el conjunto de datasets")

        if ".csv" in file:
            self.type = FileType.CSV
        elif ".arff" in file:
            self.type = FileType.ARFF
        else:
            raise ValueError("El fichero no es CSV o ARFF")

        self.file = file

    def get_allfeatures(self):
        """
        Obtiene las características de los datos. NO distingue el target (también se incluye)

        :return: Listado de las características de los datos.
        """

        return self._get_data().columns.values

    def set_target(self, target):
        """
        Especifica el target de los datos

        :param target: El target o clase para la posterior clasificación
        """
        self.target = target

    def get_only_features(self):
        """
        Obtiene las características de los datos. NO incluye target

        :return: Listado de las características de los datos (sin target).
        """
        if self.target is None:
            raise ValueError("La clase o target no ha sido establecida, selecciona primero la característica que "
                             "actúa como target")

        return np.setdiff1d(self._get_data().columns.values, self.target)

    def _get_data(self):
        """
        Obtiene los datos sin procesar (directamente del fichero) según
        el tipo de fichero que sea

        :return: Datos en forma de dataframe
        """
        if self.type == FileType.CSV:
            return self._csv_data()
        elif self.type == FileType.ARFF:
            return self._arff_data()

    def _csv_data(self):
        return pd.read_csv(self.file)

    def _arff_data(self):
        """
        Convierte los datos del fichero en un dataframe

        :return: Datos en forma de dataframe
        """
        data = arff.loadarff(self.file)
        df = pd.DataFrame(data[0])

        return df

    def get_x_y(self):
        """
        Obtiene por separado los datos (las características) y los target o clases

        :return: Las características (x), las clases o targets (y), el mapeo de las clases codificadas a las
        originales y el codificador utilizado para ello
        """

        if self.target is None:
            raise ValueError("La clase o target no ha sido establecida, selecciona primero la característica que "
                             "actúa como target")

        data = self._get_data()

        x = data.loc[:, data.columns != self.target]

        le = LabelEncoder()

        y = pd.DataFrame(le.fit_transform(data[self.target]), columns=['target'])

        mapping = {int(t): str(c, encoding='utf-8') for t, c in zip(le.transform(le.classes_), le.classes_)}

        return x, y, mapping, le


if __name__ == '__main__':
    dl = DatasetLoader('iris.csv')
    print(dl._get_data())
    print(dl.get_allfeatures())
    # dl.set_target("variety")
    print(dl.get_x_y())
